import warnings
import os
import sys
import argparse
import ast
warnings.filterwarnings('ignore')

import numpy as np
import scipy.sparse
import pandas as pd
import MDAnalysis as mda
from MDAnalysis.lib.distances import capped_distance
from joblib import Parallel, delayed

if __name__ == '__main__':
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    package_root = os.path.abspath(os.path.join(current_dir, '..'))
    if package_root not in sys.path:
        sys.path.insert(0, package_root)
from analysis.analysis_base import AnalysisBase, WriteExcelBubble

__all__ = ['ClusterDistribution']


class ClusterDistribution(AnalysisBase):
    """
    聚类分布分析：统计每帧中大于阈值的聚类数量，并以固定间隔分组转换为概率
    """

    def __init__(self, universe: mda.Universe, residues_group: dict, cutoff: float = 8.0,
                 min_cluster_size: int = 10, bin_width: int = 10, filePath: str = None,
                 parallel: bool = False, n_jobs: int = -1):
        """
        初始化聚类分布分析
        
        Args:
            universe: MDAnalysis Universe对象
            residues_group: 残基组字典，格式如 {'DPPC': ['PO4'], 'CHOL': ['ROH']}
            cutoff: 聚类距离阈值（埃）
            min_cluster_size: 最小聚类大小阈值
            bin_width: 分组间隔宽度
            filePath: 输出文件路径
            parallel: 是否并行处理
            n_jobs: 并行任务数
        """
        super().__init__(universe.trajectory)
        self.u = universe
        self.residues = list(residues_group)
        self.cutoff = cutoff
        self.min_cluster_size = min_cluster_size
        self.bin_width = bin_width
        self.file_path = filePath
        self.parallel = parallel
        self.n_jobs = n_jobs
        
        # 支持的图表类型
        self.supported_figure_types = ['Line Chart', 'Bar Chart']
        
        # 存储绘图数据
        self.plot_data = None
        
        self.atomSp = {sp: ' '.join(residues_group[sp]) for sp in self.residues}
        print("Atoms for clustering:", self.atomSp)

        self.headAtoms = self.u.atoms[[]]
        for sp in self.residues:
            self.headAtoms += self.u.select_atoms('resname %s and name %s'
                                                  % (sp, self.atomSp[sp]), updating=False)

        if self.headAtoms.n_atoms == 0:
            raise ValueError("Atom selection is empty. Please check your `residues_group` dictionary and atomic names.")

        self.n_residues = self.headAtoms.n_residues
        self.atom_resindices = self.headAtoms.resindices
        self.residue_names = self.headAtoms.residues.resnames

        self.results.ClusterCount = None
        self.parameters = f"{residues_group}, cutoff={cutoff}, min_size={min_cluster_size}, bin_width={bin_width}"

    @property
    def ClusterCount(self):
        return self.results.ClusterCount

    def _prepare(self):
        # 存储每帧所有大于阈值的聚类大小
        self.results.ClusterCount = [None] * self.n_frames

    @staticmethod
    def _calculate_cluster_count_for_frame(positions, box, cutoff, atom_resindices, n_residues, min_cluster_size):
        """
        计算单帧中大于阈值的聚类大小列表
        
        Returns:
            聚类大小列表（list）
        """
        pairs = capped_distance(
            positions,
            positions,
            max_cutoff=cutoff,
            box=box,
            return_distances=False
        )

        if pairs.shape[0] == 0:
            return []

        residue_indices_pairs = np.unique(atom_resindices[pairs], axis=0)

        if residue_indices_pairs.shape[0] == 0:
            return []

        # 过滤掉超出范围的索引
        valid_mask = (residue_indices_pairs[:, 0] < n_residues) & (residue_indices_pairs[:, 1] < n_residues)
        residue_indices_pairs = residue_indices_pairs[valid_mask]
        
        if residue_indices_pairs.shape[0] == 0:
            return []

        # 移除自连接
        ref, nei = residue_indices_pairs[residue_indices_pairs[:, 0] != residue_indices_pairs[:, 1]].T
        data = np.ones_like(ref, dtype=np.int8)

        # 构建稀疏邻接矩阵
        neighbours_matrix = scipy.sparse.csr_matrix(
            (data, (ref, nei)),
            shape=(n_residues, n_residues)
        )

        # 使用连通分量算法找到所有聚类
        n_components, com_labels = scipy.sparse.csgraph.connected_components(
            neighbours_matrix, directed=False
        )

        if n_components == 0:
            return []

        # 统计每个聚类的大小
        _, counts = np.unique(com_labels, return_counts=True)
        
        # 返回大小 > min_cluster_size 的聚类大小列表
        valid_sizes = counts[counts > min_cluster_size].tolist()
        
        return valid_sizes

    def _single_frame(self):
        """处理单帧数据"""
        cluster_sizes = ClusterDistribution._calculate_cluster_count_for_frame(
            self.headAtoms.positions,
            self._ts.dimensions,
            self.cutoff,
            self.atom_resindices,
            self.n_residues,
            self.min_cluster_size
        )
        self.results.ClusterCount[self._frame_index] = cluster_sizes

    def _get_inputs_generator(self):
        """生成并行处理的输入参数"""
        for ts in self.u.trajectory[self.start:self.stop:self.step]:
            yield (
                self.headAtoms.positions.copy(),
                ts.dimensions,
                self.cutoff,
                self.atom_resindices,
                self.n_residues,
                self.min_cluster_size
            )

    def run(self, start=None, stop=None, step=None, verbose=None, callBack=None, plot_type='none', plot_output=None):
        """运行聚类分布分析"""
        # 处理stop参数
        if stop == -1:
            stop = None
        
        # 对于并行模式，需要先计算实际的stop值用于n_frames计算
        if stop is None:
            actual_stop = self._trajectory.n_frames
        elif stop < 0:
            actual_stop = self._trajectory.n_frames + stop + 1
        else:
            actual_stop = stop if stop <= self._trajectory.n_frames else self._trajectory.n_frames
        
        self.start = start if start is not None else 0
        self.stop = actual_stop
        self.step = step if step is not None else 1
        self.n_frames = len(range(self.start, self.stop, self.step))
        self._prepare()

        if self.parallel:
            print(f"Running in parallel on {self.n_jobs} jobs...")
            verbose_level = 10 if verbose else 0
            inputs_generator = self._get_inputs_generator()
            results_list = Parallel(n_jobs=self.n_jobs, verbose=verbose_level)(
                delayed(ClusterDistribution._calculate_cluster_count_for_frame)(*inputs) 
                for inputs in inputs_generator
            )
            if results_list:
                self.results.ClusterCount = results_list
        else:
            print("Running in serial mode...")
            super().run(start=start, stop=stop, step=step, verbose=verbose, callBack=callBack)

        # 计算概率分布
        self._calculate_probability_distribution()
        
        # 调用_conclude
        self._conclude(plot_type=plot_type, plot_output=plot_output)

    def _calculate_probability_distribution(self):
        """
        计算概率分布：收集所有帧的聚类大小，按bin_width分组统计每个区间的频次，再转换为概率
        """
        # 收集所有帧中所有聚类的大小
        all_cluster_sizes = []
        for frame_clusters in self.results.ClusterCount:
            if frame_clusters is not None and len(frame_clusters) > 0:
                all_cluster_sizes.extend(frame_clusters)
        
        if not all_cluster_sizes:
            print("\nNo clusters found that meet the criteria.")
            self.bin_ranges = []
            self.bin_counts = np.array([])
            self.probabilities = np.array([])
            return
        
        # 确定分组范围
        min_size = int(min(all_cluster_sizes))
        max_size = int(max(all_cluster_sizes))
        
        # 调整到bin_width的倍数
        bin_start = (min_size // self.bin_width) * self.bin_width
        bin_end = ((max_size // self.bin_width) + 1) * self.bin_width
        
        # 创建bins（区间边界）
        bins = np.arange(bin_start, bin_end + self.bin_width, self.bin_width)
        
        # 统计每个区间内聚类出现的总频次
        bin_counts = np.zeros(len(bins) - 1, dtype=int)  # 区间数量 = bin数量 - 1
        
        for size in all_cluster_sizes:
            # 找到size落在哪个区间
            bin_idx = np.digitize(size, bins) - 1
            # 确保索引有效
            if 0 <= bin_idx < len(bin_counts):
                bin_counts[bin_idx] += 1
        
        # 计算总频次
        total_freq = np.sum(bin_counts)
        
        # 转换为概率（百分比）
        probabilities = (bin_counts / total_freq * 100) if total_freq > 0 else bin_counts
        
        # 保存结果
        self.bin_ranges = [(bins[i], bins[i+1]) for i in range(len(bins)-1)]
        self.bin_counts = bin_counts
        self.probabilities = probabilities
        
        print(f"\nCluster size distribution range: [{min_size}, {max_size}]")
        print(f"Bin width: {self.bin_width}")
        print(f"Number of bins: {len(bins)-1}")
        print(f"Total clusters: {total_freq}")
        
        # 打印概率分布
        print("\nProbability distribution:")
        for i, (bin_range, prob) in enumerate(zip(self.bin_ranges, self.probabilities)):
            if bin_counts[i] > 0:
                print(f"  Range {bin_range[0]}-{bin_range[1]}: {prob:.2f}% ({bin_counts[i]} clusters)")

    def _conclude(self, plot_type='none', plot_output=None):
        """结束处理，保存结果和绘图"""
        if self.file_path:
            # 如果概率分布已计算，保存区间分布数据
            if hasattr(self, 'bin_ranges') and len(self.bin_ranges) > 0:
                # 准备区间分布数据
                distribution_data = []
                for i, (bin_range, prob) in enumerate(zip(self.bin_ranges, self.probabilities)):
                    if self.bin_counts[i] > 0:
                        distribution_data.append({
                            'Range': f"{bin_range[0]}-{bin_range[1]}",
                            'Count': self.bin_counts[i],
                            'Probability_%': prob
                        })
                
                # 保存为CSV
                df = pd.DataFrame(distribution_data)
                comments = ['Created by LNB-MDT v1.0', 'Cluster Distribution', 'TYPE:Distribution', 'Parameters:' + self.parameters]
                # 使用 WriteExcel 的静态方法
                from analysis.analysis_base import WriteExcel
                WriteExcel._write_to_csv(self.file_path, comments, df)
                print(f"Results saved to {self.file_path}")
        
        # 如果概率分布已计算，准备绘图数据并绘图
        if hasattr(self, 'bin_ranges'):
            self._prepare_plot_data()
            if plot_type != 'none':
                self.plot_distribution(plot_type, plot_output)
        
        if not self.file_path:
            return self.results.ClusterCount

    def _prepare_plot_data(self):
        """准备绘图数据：区间和对应的概率"""
        data = []
        
        for i, (bin_range, prob) in enumerate(zip(self.bin_ranges, self.probabilities)):
            # 只保留有数据的区间
            if self.bin_counts[i] > 0:
                row = {
                    'Range': f"{bin_range[0]}-{bin_range[1]}",
                    'Probability_%': prob,
                    'Count': self.bin_counts[i]
                }
                data.append(row)
        
        self.plot_data = pd.DataFrame(data)
        print(f"Cluster distribution plot data prepared: {self.plot_data.shape}")

    def plot_distribution(self, plot_type='both', plot_output=None):
        """
        绘制聚类分布图
        
        Args:
            plot_type: 绘图类型，'line', 'hist', 'both', 或 'none'
            plot_output: 输出文件路径
        """
        import matplotlib.pyplot as plt
        
        if self.plot_data is None:
            self._prepare_plot_data()
        
        if plot_type == 'none':
            return
        
        should_show = plot_output is None
        
        if plot_type in ['line', 'both']:
            self.plot_line()
            
            if plot_output:
                if plot_type == 'both':
                    output_file = plot_output.replace('.png', '_line.png') if plot_output.endswith('.png') else f"{plot_output}_line.png"
                else:
                    output_file = plot_output if plot_output.endswith('.png') else f"{plot_output}.png"
                
                current_fig = plt.gcf()
                current_fig.savefig(output_file, dpi=300, bbox_inches='tight')
                print(f"Line chart saved to: {output_file}")
                plt.close()
        
        if plot_type in ['hist', 'both']:
            self.plot_hist()
            
            if plot_output:
                if plot_type == 'both':
                    output_file = plot_output.replace('.png', '_hist.png') if plot_output.endswith('.png') else f"{plot_output}_hist.png"
                else:
                    output_file = plot_output if plot_output.endswith('.png') else f"{plot_output}.png"
                
                current_fig = plt.gcf()
                current_fig.savefig(output_file, dpi=300, bbox_inches='tight')
                print(f"Histogram saved to: {output_file}")
                plt.close()
        
        if should_show:
            plt.show()

    def plot_line(self, figure_settings=None):
        """绘制折线图：横坐标为区间，纵坐标为概率"""
        if self.plot_data is None:
            self._prepare_plot_data()
        
        if figure_settings is None:
            figure_settings = {
                'x_title': 'Cluster Count Range',
                'y_title': 'Probability (%)',
                'axis_text': 12,
                'marker_shape': 'o',
                'marker_size': 8,
                'line_color': 'blue'
            }
        
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.plot_data['Range'], self.plot_data['Probability_%'],
                marker=figure_settings.get('marker_shape', 'o'),
                markersize=figure_settings.get('marker_size', 8),
                color=figure_settings.get('line_color', 'blue'),
                linestyle='-', linewidth=2, label='Probability')
        
        plt.xlabel(figure_settings.get('x_title', 'Cluster Count Range'), fontsize=figure_settings.get('axis_text', 12))
        plt.ylabel(figure_settings.get('y_title', 'Probability (%)'), fontsize=figure_settings.get('axis_text', 12))
        plt.title('Cluster Distribution Probability', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

    def plot_hist(self, figure_settings=None):
        """绘制直方图：横坐标为区间，纵坐标为概率"""
        if self.plot_data is None:
            self._prepare_plot_data()
        
        if figure_settings is None:
            figure_settings = {
                'x_title': 'Cluster Count Range',
                'y_title': 'Probability (%)',
                'axis_text': 12,
                'hist_color': 'lightblue'
            }
        
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(self.plot_data['Range'], self.plot_data['Probability_%'],
                      color=figure_settings.get('hist_color', 'lightblue'),
                      alpha=0.7,
                      edgecolor='black',
                      linewidth=0.5)
        
        # 在条形顶部显示概率值
        for bar, prob in zip(bars, self.plot_data['Probability_%']):
            plt.text(bar.get_x() + bar.get_width() / 2, prob + 0.5,
                    f'{prob:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        plt.xlabel(figure_settings.get('x_title', 'Cluster Count Range'), fontsize=figure_settings.get('axis_text', 12))
        plt.ylabel(figure_settings.get('y_title', 'Probability (%)'), fontsize=figure_settings.get('axis_text', 12))
        plt.title('Cluster Distribution Probability', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()


# --- Command-line Argument Parsing ---
def parse_args():
    parser = argparse.ArgumentParser(
        description="Perform Cluster Size Distribution analysis on molecular dynamics trajectories."
    )

    parser.add_argument(
        "--gro-file", "-g",
        type=str,
        default="cases/lnb.gro",
        help="Path to the GRO file (topology file)."
    )
    parser.add_argument(
        "--xtc-file", "-x",
        type=str,
        default=None,
        help="Path to the XTC file (trajectory file). Optional. If not provided, only GRO file will be analyzed (single frame)."
    )
    parser.add_argument(
        "--output-csv", "-o",
        type=str,
        default="cases/csv/cluster_distribution_results.csv",
        help="Path to the output CSV file for cluster distribution results."
    )
    parser.add_argument(
        "--residues", "-r",
        type=str,
        default="{'DPPC': ['PO4'], 'DAPC': ['PO4'], 'CHOL': ['ROH']}",
        help="A dictionary string defining residue groups for analysis. E.g., \"{'DPPC': ['PO4'], 'CHOL': ['ROH']}\""
    )
    parser.add_argument(
        "--cutoff",
        type=float,
        default=8.0,
        help="Cutoff distance for clustering (in Angstroms)."
    )
    parser.add_argument(
        "--min-cluster-size",
        type=int,
        default=10,
        help="Minimum cluster size to be counted. Only clusters larger than this value will be included."
    )
    parser.add_argument(
        "--bin-width",
        type=int,
        default=10,
        help="Bin width for grouping cluster counts (default: 10)."
    )
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Enable parallel processing for cluster distribution calculation."
    )
    parser.add_argument(
        "--n-jobs", "-j",
        type=int,
        default=-1,
        help="Number of jobs to run in parallel. -1 means using all available CPU cores."
    )
    parser.add_argument(
        "--start-frame", "-s",
        type=int,
        default=0,
        help="Starting frame for analysis (0-indexed)."
    )
    parser.add_argument(
        "--stop-frame", "-e",
        type=int,
        help="Stopping frame for analysis (exclusive). Defaults to end of trajectory."
    )
    parser.add_argument(
        "--step-frame", "-t",
        type=int,
        default=1,
        help="Step size for frames during analysis."
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output during analysis."
    )
    parser.add_argument(
        "--plot",
        type=str,
        choices=['line', 'hist', 'both', 'none'],
        default='none',
        help="Type of plot to generate. 'line' for line chart, 'hist' for histogram, 'both' for both, 'none' to skip plotting."
    )
    parser.add_argument(
        "--plot-output",
        type=str,
        default=None,
        help="Output file path for the plot. If not specified and plot is enabled, plot will only be displayed (not saved)."
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # Parse residues_group from string
    try:
        residues_group_parsed = ast.literal_eval(args.residues)
        if not isinstance(residues_group_parsed, dict):
            raise ValueError("Residues argument must be a dictionary string.")
    except (ValueError, SyntaxError) as e:
        print(f"Error: Could not parse residues argument: {e}")
        print("Please ensure it's a valid dictionary string, e.g., \"{'DPPC': ['PO4'], 'CHOL': ['ROH']}\"")
        sys.exit(1)

    print("\n--- Initializing MDAnalysis Universe ---")
    try:
        if args.xtc_file and os.path.exists(args.xtc_file):
            u = mda.Universe(args.gro_file, args.xtc_file)
            print(f"Loaded both GRO and XTC files: {args.gro_file}, {args.xtc_file}")
        else:
            u = mda.Universe(args.gro_file)
            print(f"Loaded only GRO file: {args.gro_file}")
            print(f"Note: Analyzing single frame (frame 0) from GRO file")
    except Exception as e:
        print(f"Error loading MDAnalysis Universe: {e}")
        print("Please check if GRO/XTC files exist and are valid.")
        sys.exit(1)

    print("\n--- Running Cluster Distribution Analysis ---")
    cluster_dist = ClusterDistribution(
        u,
        residues_group_parsed,
        cutoff=args.cutoff,
        min_cluster_size=args.min_cluster_size,
        bin_width=args.bin_width,
        filePath=args.output_csv,
        parallel=args.parallel,
        n_jobs=args.n_jobs
    )
    
    cluster_dist.run(
        start=args.start_frame,
        stop=args.stop_frame,
        step=args.step_frame,
        verbose=args.verbose,
        plot_type=args.plot,
        plot_output=args.plot_output
    )

    print("\n--- Analysis Finished ---")
    if args.output_csv:
        print(f"Results saved to: {args.output_csv}")

import warnings
import os
import sys
import argparse
warnings.filterwarnings('ignore')

import numpy as np
import matplotlib.pyplot as plt
import MDAnalysis as mda
from MDAnalysis.lib.distances import distance_array

if __name__ == '__main__':
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    package_root = os.path.abspath(os.path.join(current_dir, '..'))
    if package_root not in sys.path:
        sys.path.insert(0, package_root)
from analysis.analysis_base import AnalysisBase, WriteExcelBubble

__all__ = ['GasLipidContact']


class GasLipidContact(AnalysisBase):
    """
    分析气体分组和不同磷脂的接触数
    
    原理：对每种磷脂的指定原子，搜索其附近截断半径内的气体分子数目,
          然后对每种磷脂类型求平均（总接触数/该磷脂类型的分子数）
          最后根据平均值计算比例（每种磷脂的平均值/所有磷脂平均值之和）
          
    使用方法：
        需要参数：
        1. universe: MDAnalysis Universe对象
        eg: u = mda.Universe("ach.tpr", "ach.xtc")
        注：可以只为单独的gro文件
        
        2. gas_name: str
        eg: gas_name = "N2"
        注：输入选定的气体残基名称
        
        3. lipid_atoms_dict: dict
        eg: lipid_atoms_dict = {"DPPC": ["C4A", "C4B"], "DAPC": ["C4A", "C4B"]}
        注：字典，键是磷脂名称，值是该磷脂要分析的原子列表
        
        4. cut_off_value: float
        注：截断半径为多少A
        
        5. filePath: str (可选)
        注：输出CSV文件路径
        
    return:
        results.ContactMean: np.array([len(lipid_atoms_dict), n_frames])
        每行代表一种磷脂类型，每列代表一帧的平均接触数（总接触数/该磷脂类型的分子数）
        
        results.ContactCount: np.array([len(lipid_atoms_dict), n_frames])
        每行代表一种磷脂类型，每列代表一帧的总接触数
        
        results.ContactRatio: np.array([len(lipid_atoms_dict), n_frames])
        每行代表一种磷脂类型，每列代表一帧的接触比例（基于平均值）
        
    用法：
        eg:    
        glc = GasLipidContact(u, "N2", {"DPPC": ["C4A", "C4B"], "DAPC": ["C4A", "C4B"]}, 5.0, filePath="contact.csv")
        glc.run(1000, 2000, 2, verbose=True)
        glc.make_figure()
    """

    def __init__(self, universe, gas_name: str, lipid_atoms_dict: dict, cut_off_value: float, 
                 filePath: str = None):
        super().__init__(universe.trajectory)
        self.u = universe
        self._gas = gas_name
        self._lipid_atoms_dict = lipid_atoms_dict  # 字典，键是磷脂名称，值是该磷脂的原子列表
        self._lipid_residues = list(lipid_atoms_dict.keys())  # 磷脂名称列表
        self._cut_value = cut_off_value
        self.file_path = filePath
        
        self.results.ContactCount = None  # 总接触数
        self.results.ContactMean = None  # 平均接触数（总接触数/该磷脂类型的分子数）
        self.results.ContactRatio = None  # 接触比例（基于平均值）
        self.parameters = f"gas_name={gas_name}, lipid_atoms_dict={lipid_atoms_dict}, cutoff={cut_off_value}"
        
        # 支持的图表类型
        self.supported_figure_types = ['Line Chart', 'Bar Chart']

    def _prepare(self):
        """初始化结果数组"""
        self.results.ContactCount = np.zeros([len(self._lipid_residues), self.n_frames])  # 总接触数
        self.results.ContactMean = np.zeros([len(self._lipid_residues), self.n_frames])  # 平均接触数
        self.results.ContactRatio = np.zeros([len(self._lipid_residues), self.n_frames])  # 接触比例

    def _single_frame(self):
        """
        对单帧进行分析：
        1. 对每种磷脂的指定原子，搜索附近截断半径内的气体分子
        2. 统计每种磷脂类型的总接触数
        3. 计算平均值（总接触数/该磷脂类型的分子数）
        4. 根据平均值计算比例
        """
        contact_count_arr = np.zeros([len(self._lipid_residues)])  # 总接触数
        contact_mean_arr = np.zeros([len(self._lipid_residues)])  # 平均接触数
        
        # 获取所有气体分子
        gas_atoms = self.u.select_atoms('resname %s' % self._gas)
        
        # 对每种磷脂类型进行分析
        for i, lipid_name in enumerate(self._lipid_residues):
            # 获取该磷脂类型的指定原子
            atom_names = self._lipid_atoms_dict[lipid_name]
            atom_names_str = ' '.join(atom_names)
            lipid_atoms = self.u.select_atoms('resname %s and name %s' % (lipid_name, atom_names_str))
            
            if lipid_atoms.n_atoms == 0:
                contact_count_arr[i] = 0.0
                contact_mean_arr[i] = 0.0
                continue
            
            # 使用distance_array高效计算距离
            lipid_positions = lipid_atoms.positions
            gas_positions = gas_atoms.positions
            
            # 计算所有距离矩阵
            distances = distance_array(lipid_positions, gas_positions, box=self._ts.dimensions)
            
            # 统计在截断半径内的接触数
            contacts = (distances <= self._cut_value) & (distances > 0)  # 排除自身
            total_contacts = np.sum(contacts)
            
            # 存储总接触数
            contact_count_arr[i] = total_contacts
            
            # 获取该磷脂类型的总分子数
            n_lipid_molecules = self.u.select_atoms('resname %s' % lipid_name).n_residues
            
            # 计算平均值（总接触数/该磷脂类型的分子数）
            if n_lipid_molecules > 0:
                contact_mean_arr[i] = total_contacts / n_lipid_molecules
            else:
                contact_mean_arr[i] = 0.0
        
        # 存储总接触数和平均值
        self.results.ContactCount[:, self._frame_index] = contact_count_arr
        self.results.ContactMean[:, self._frame_index] = contact_mean_arr
        
        # 根据平均值计算比例（每种磷脂的平均值/所有磷脂平均值之和）
        sum_mean = np.sum(contact_mean_arr)
        if sum_mean > 0:
            contact_ratio_arr = contact_mean_arr / sum_mean
        else:
            contact_ratio_arr = np.zeros_like(contact_mean_arr)
        
        self.results.ContactRatio[:, self._frame_index] = contact_ratio_arr

    def _conclude(self):
        """分析完成后的处理，保存结果到CSV文件"""
        if self.file_path:
            # 保存每种磷脂的总接触数
            for i, lipid_name in enumerate(self._lipid_residues):
                lipid_count_dict = {
                    'frames': list(range(self.start, self.stop, self.step))[:self.n_frames],
                    'results': self.results.ContactCount[i, :],
                    'file_path': self.file_path.replace('.csv', f'_{lipid_name}_count.csv') if self.file_path.endswith('.csv') else self.file_path + f'_{lipid_name}_count.csv',
                    'description': f'Gas-{self._gas} {lipid_name} Total Contact Count',
                    'parameters': self.parameters,
                    'trajectory': self._trajectory
                }
                WriteExcelBubble(**lipid_count_dict).run()
            
            # 保存每种磷脂的平均接触数
            for i, lipid_name in enumerate(self._lipid_residues):
                lipid_mean_dict = {
                    'frames': list(range(self.start, self.stop, self.step))[:self.n_frames],
                    'results': self.results.ContactMean[i, :],
                    'file_path': self.file_path.replace('.csv', f'_{lipid_name}_mean.csv') if self.file_path.endswith('.csv') else self.file_path + f'_{lipid_name}_mean.csv',
                    'description': f'Gas-{self._gas} {lipid_name} Contact Mean (total contacts / lipid count)',
                    'parameters': self.parameters,
                    'trajectory': self._trajectory
                }
                WriteExcelBubble(**lipid_mean_dict).run()
            
            # 保存接触比例结果（基于平均值）
            for i, lipid_name in enumerate(self._lipid_residues):
                lipid_ratio_dict = {
                    'frames': list(range(self.start, self.stop, self.step))[:self.n_frames],
                    'results': self.results.ContactRatio[i, :],
                    'file_path': self.file_path.replace('.csv', f'_{lipid_name}_ratio.csv') if self.file_path.endswith('.csv') else self.file_path + f'_{lipid_name}_ratio.csv',
                    'description': f'Gas-{self._gas} {lipid_name} Contact Ratio (based on mean)',
                    'parameters': self.parameters,
                    'trajectory': self._trajectory
                }
                WriteExcelBubble(**lipid_ratio_dict).run()
            
            print(f"Analysis complete. Results saved to {self.file_path}")

    def make_figure(self, show_ratio=True, show_count=False, show_mean=True):
        """
        绘制接触数、平均接触数或接触比例的图表
        
        Args:
            show_ratio: bool, 是否显示接触比例图（默认True）
            show_count: bool, 是否显示总接触数图（默认False）
            show_mean: bool, 是否显示平均接触数图（默认True）
        """
        if show_mean:
            plt.figure(figsize=(10, 6))
            data = self.results.ContactMean
            
            # 绘制每条曲线，即每种磷脂的平均接触数
            for i, lipid_name in enumerate(self._lipid_residues):
                plt.plot(data[i, :], label=f'{lipid_name} Mean', linewidth=2)
            
            # 设置图例
            plt.legend()
            # 设置x轴标签和y轴标签
            plt.xlabel('Frames', fontsize=12)
            plt.ylabel(f'Contact Mean (contacts/molecule) with {self._gas}', fontsize=12)
            plt.title(f'Gas-{self._gas} Lipid Contact Mean (total contacts / lipid count)', fontsize=14)
            # 显示网格
            plt.grid(True, alpha=0.3)
            # 显示
            plt.tight_layout()
            plt.show()
        
        if show_count:
            plt.figure(figsize=(10, 6))
            data = self.results.ContactCount
            
            # 绘制每条曲线，即每种磷脂的总接触数
            for i, lipid_name in enumerate(self._lipid_residues):
                plt.plot(data[i, :], label=f'{lipid_name} Count', linewidth=2)
            
            # 设置图例
            plt.legend()
            # 设置x轴标签和y轴标签
            plt.xlabel('Frames', fontsize=12)
            plt.ylabel(f'Total Contact Count with {self._gas}', fontsize=12)
            plt.title(f'Gas-{self._gas} Lipid Total Contact Count', fontsize=14)
            # 显示网格
            plt.grid(True, alpha=0.3)
            # 显示
            plt.tight_layout()
            plt.show()
        
        if show_ratio:
            plt.figure(figsize=(10, 6))
            data = self.results.ContactRatio
            
            # 绘制每条曲线，即每种磷脂的接触比例
            for i, lipid_name in enumerate(self._lipid_residues):
                plt.plot(data[i, :], label=f'{lipid_name} Ratio', linewidth=2)
            
            # 设置图例
            plt.legend()
            # 设置x轴标签和y轴标签
            plt.xlabel('Frames', fontsize=12)
            plt.ylabel(f'Contact Ratio (based on mean) with {self._gas}', fontsize=12)
            plt.title(f'Gas-{self._gas} Lipid Contact Ratio (based on mean)', fontsize=14)
            # 显示网格
            plt.grid(True, alpha=0.3)
            # 显示
            plt.tight_layout()
            plt.show()


# --- Command-line Argument Parsing ---
def parse_args():
    parser = argparse.ArgumentParser(
        description="分析气体分组和不同磷脂的接触数"
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
        help="Path to the XTC file (trajectory file). Optional, can analyze single GRO file."
    )
    parser.add_argument(
        "--gas-name", "-n",
        type=str,
        required=True,
        help="Gas residue name (e.g., 'O2', 'N2')."
    )
    parser.add_argument(
        "--lipid-atoms-dict", "-d",
        type=str,
        required=True,
        help="Dictionary string defining lipid atoms for analysis. E.g., \"{'DPPC': ['C4A', 'C4B'], 'DAPC': ['C4A', 'C4B']}\""
    )
    parser.add_argument(
        "--cutoff", "-c",
        type=float,
        default=5.0,
        help="Cutoff distance for contact analysis (in Angstroms)."
    )
    parser.add_argument(
        "--output-csv", "-o",
        type=str,
        default="cases/csv/gas_lipid_contact_results.csv",
        help="Path to the output CSV file for gas-lipid contact results."
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
        "--show-figure",
        action="store_true",
        help="Show figure after analysis."
    )
    parser.add_argument(
        "--show-count",
        action="store_true",
        help="Show total contact count figure."
    )
    parser.add_argument(
        "--show-mean",
        action="store_true",
        help="Show contact mean figure (default: True)."
    )
    parser.add_argument(
        "--show-ratio",
        action="store_true",
        help="Show contact ratio figure."
    )

    return parser.parse_args()


if __name__ == "__main__":
    import ast
    args = parse_args()

    print("\n--- Initializing MDAnalysis Universe ---")
    try:
        if args.xtc_file:
            u = mda.Universe(args.gro_file, args.xtc_file)
        else:
            u = mda.Universe(args.gro_file)
            print("Note: Only GRO file provided. Analyzing single frame.")
    except Exception as e:
        print(f"Error loading MDAnalysis Universe: {e}")
        print("Please check if GRO/XTC files exist and are valid.")
        sys.exit(1)

    # Parse lipid_atoms_dict from string
    try:
        lipid_atoms_dict_parsed = ast.literal_eval(args.lipid_atoms_dict)
        if not isinstance(lipid_atoms_dict_parsed, dict):
            raise ValueError("lipid-atoms-dict argument must be a dictionary string.")
    except (ValueError, SyntaxError) as e:
        print(f"Error: Could not parse lipid-atoms-dict argument: {e}")
        print("Please ensure it's a valid dictionary string, e.g., \"{'DPPC': ['C4A', 'C4B'], 'DAPC': ['C4A', 'C4B']}\"")
        sys.exit(1)

    print("\n--- Running Gas-Lipid Contact Analysis ---")
    print(f"Gas name: {args.gas_name}")
    print(f"Lipid atoms dict: {lipid_atoms_dict_parsed}")
    print(f"Cutoff: {args.cutoff} A")
    
    glc = GasLipidContact(
        u,
        args.gas_name,
        lipid_atoms_dict_parsed,
        args.cutoff,
        filePath=args.output_csv
    )
    
    glc.run(
        start=args.start_frame,
        stop=args.stop_frame,
        step=args.step_frame,
        verbose=args.verbose
    )

    print("\n--- Analysis Finished ---")
    print(f"Results saved to: {args.output_csv}")
    
    if args.show_figure:
        # 默认显示mean，除非用户指定了其他选项
        show_mean = args.show_mean if (args.show_count or args.show_ratio or args.show_mean) else True
        glc.make_figure(
            show_ratio=args.show_ratio,
            show_count=args.show_count,
            show_mean=show_mean
        )


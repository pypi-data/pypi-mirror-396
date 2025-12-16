import numpy as np
import matplotlib.pyplot as plt
import MDAnalysis as mda

# 读取GROMACS轨迹文件
u = mda.Universe("1.gro","5.xtc")

# 选择氮气分子
nitrogen = u.select_atoms("name N2")

# 获取盒子信息
box = u.dimensions[:3]

# 设置径向密度分布参数
nbins = 50
rmax = np.min(box) / 2.0
dr = rmax / nbins
r = np.linspace(0, rmax, nbins)

# 初始化径向密度分布数组
density = np.zeros(nbins)

# 遍历轨迹
for ts in u.trajectory:
    # 获取氮气分子坐标
    positions = nitrogen.positions - box / 2.0

    # 计算氮气分子与盒子中心的距离
    distances = np.linalg.norm(positions, axis=1)

    # 统计距离在每个径向分布区间内的氮气分子数目
    for i in range(nbins):
        n_particles = np.sum((distances >= i * dr) & (distances < (i + 1) * dr))
        volume = 4.0 / 3.0 * np.pi * ((i + 1) * dr) ** 3 - 4.0 / 3.0 * np.pi * (i * dr) ** 3
        density[i] += n_particles * 280000 / 6.02 / volume

# 归一化径向密度分布
density /= len(u.trajectory)

# 绘制径向密度分布图像
plt.plot(r, density)
plt.xlabel("Distance from box center (nm)")
plt.ylabel("Radial density (nm^-3)")
plt.show()

print(rmax)
print(volume)
print(n_particles)
print(r)
print(density)
print(nitrogen)
print(dr)

with open("red.txt", "w") as f:
    for x, y in zip(r, density):
        f.write(f"{x} {y}\n")
        print(x, y)
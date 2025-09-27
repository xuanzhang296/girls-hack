import numpy as np
import matplotlib.pyplot as plt
import time

# 生成示例信号（正弦波 + 噪声）
fs = 1000  # 采样率 Hz
T = 2      # 总时长 s
t = np.linspace(0, T, fs*T, endpoint=False)  # 时间向量（0 到 T，不包含 T）
signalTotal = np.sin(2*np.pi*5*t) + 0.2*np.random.randn(len(t))  # 5Hz 正弦 + 噪声

# 窗函数参数
window_size = 200   # 每次窗口的采样点数
step_size = 20      # 每次滑动多少点

# 实时滑动演示
plt.ion()  # 打开交互模式，允许图像在循环中动态刷新
fig, ax = plt.subplots()  # 创建画布与坐标轴
line, = ax.plot([], [], lw=2)  # 预先创建一条空线，后续通过 set_data 更新
ax.set_xlim(0, window_size/fs)  # 初始 x 轴范围（以窗口时长设置）
ax.set_ylim(signalTotal.min()-0.5, signalTotal.max()+0.5)  # y 轴留上下边距 0.5
ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude")
ax.set_title("Sliding Window over Signal")
start_time=time.time  # 记录起始时间的函数引用（若需实际时间请调用 time.time()）

for start in range(0, len(signalTotal)-window_size, step_size):  # 每次滑动 step_size 个采样点
    tick=time.time()  # 当前循环开始时间（可用于统计耗时，当前未使用）
    end = start + window_size  # 当前窗口结束索引

    window_t = t[start:end]   # 窗口内时间（与原始时间轴一致）
    # 如果希望窗口时间从 0 开始，可用：window_t = t[start:end] - t[start]
    window_signal = signalTotal[start:end]  # 窗口内的信号片段

    line.set_data(window_t, window_signal)  # 更新曲线的数据点
    ax.set_xlim(window_t[0], window_t[-1])  # 将 x 轴范围同步到当前窗口，实现“滑动”效果
    print(window_t[0])  # 打印当前窗口的起始时间（用于调试/观察）
    plt.pause(0.05)  # 控制播放速度（每 50ms 刷新一次）

plt.ioff()  # 关闭交互模式
plt.show()  # 展示最终图像（阻塞）
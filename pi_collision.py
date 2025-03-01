import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 用户输入处理
while True:
    try:
        k = int(input("请输入质量比指数 k (建议1-4): "))
        if k >= 0:
            break
        print("请输入非负整数")
    except ValueError:
        print("请输入有效整数")

# 物理参数配置
m1 = 1                   # 小方块质量
m2 = 100**k              # 大方块质量 (100^k倍)
width = 20               # 方块宽度
precision = 1e-12        # 碰撞检测精度阈值

# 初始化参数
x1 = 150.0               # 小方块初始位置
x2 = 200.0               # 大方块初始位置
v1 = -5.0                # 小方块初始速度
v2 = 0.0                 # 大方块初始速度
wall_pos = 300.0         # 右侧墙壁位置
collisions = 0           # 碰撞计数器

# 创建图形界面
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xlim(0, wall_pos + 100)
ax.set_ylim(0, 100)
ax.set_aspect('equal')
plt.axis('off')

# 创建图形元素
wall = plt.Line2D([wall_pos, wall_pos], [0, 100], color='k', lw=3)
rect1 = plt.Rectangle((x1-width/2, 40), width, 20, color='royalblue', alpha=0.8)
rect2 = plt.Rectangle((x2-width/2, 40), width, 20, color='crimson', alpha=0.8)
ax.add_patch(rect1)
ax.add_patch(rect2)
ax.add_line(wall)

# 创建信息显示
info_text = ax.text(20, 85, 
                   f"质量比: 1 : {100**k}\n碰撞次数: 0\nπ ≈ 0.0000000000",
                   fontsize=12, 
                   bbox=dict(facecolor='white', alpha=0.9))

def precise_collision():
    """精确处理碰撞事件的子函数"""
    global x1, x2, v1, v2, collisions
    dt_remaining = 1/30  # 固定每帧持续时间
    
    while dt_remaining > precision:
        # 计算可能的碰撞时间
        t_block = t_wall = float('inf')
        
        # 方块间碰撞检测
        if v1 > v2:
            distance = (x2 - width/2) - (x1 + width/2)
            if distance > 0:
                t_block = distance / (v1 - v2)
        
        # 墙壁碰撞检测
        if v2 > 0:
            distance_wall = (wall_pos - width/2) - x2
            if distance_wall > 0:
                t_wall = distance_wall / v2
        
        # 确定最小时间间隔
        delta_t = min(t_block, t_wall, dt_remaining)
        
        # 更新位置
        x1 += v1 * delta_t
        x2 += v2 * delta_t
        dt_remaining -= delta_t
        
        # 处理碰撞事件
        if delta_t == t_block:
            # 精确动量守恒计算
            u1 = ((m1 - m2)/(m1 + m2)) * v1 + (2*m2/(m1 + m2)) * v2
            u2 = (2*m1/(m1 + m2)) * v1 + ((m2 - m1)/(m1 + m2)) * v2
            v1, v2 = u1, u2
            collisions += 1
        elif delta_t == t_wall:
            v2 = -v2
            collisions += 1

def update(frame):
    """动画更新函数"""
    precise_collision()
    
    # 更新方块位置
    rect1.set_x(x1 - width/2)
    rect2.set_x(x2 - width/2)
    
    # 计算圆周率近似值
    pi_approx = collisions / (10**k)
    
    # 更新信息显示
    info_text.set_text(
        f"质量比: 1 : {100**k}\n"
        f"碰撞次数: {collisions}\n"
        f"π ≈ {pi_approx:.10f}"
    )
    
    # 停止条件：当不再可能发生碰撞时
    if v1 <= v2 and (x1 + width/2) < (x2 - width/2):
        ani.event_source.stop()
        print(f"\n模拟结束，最终结果:\n碰撞次数: {collisions}\nπ近似值: {pi_approx:.10f}")
    
    return rect1, rect2, info_text

# 创建并启动动画
ani = animation.FuncAnimation(fig, update, interval=30, blit=True)
plt.show()

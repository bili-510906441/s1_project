# 提示用户输入数据点
print("请输入数据点，格式为 x,y，多个点用空格分隔（例如：1,2 3,4 5,6）：")
data_input = input().strip()

if not data_input:
    print("错误：未输入数据。")
    exit()

# 解析输入数据
points = []
for item in data_input.split():
    # 检查格式是否正确
    if ',' not in item:
        print(f"错误：输入项 '{item}' 格式不正确，请使用逗号分隔的 x,y 格式。")
        exit()
    parts = item.split(',')
    if len(parts) != 2:
        print(f"错误：输入项 '{item}' 格式不正确，应包含且仅包含一个逗号。")
        exit()
    # 转换为浮点数
    try:
        x = float(parts[0])
        y = float(parts[1])
        points.append((x, y))
    except ValueError:
        print(f"错误：输入项 '{item}' 包含非数字字符。")
        exit()

# 检查数据点数量
n = len(points)
if n < 2:
    print("错误：至少需要两个数据点才能计算线性回归。")
    exit()

# 计算统计量
sum_x = sum(x for x, y in points)
sum_y = sum(y for x, y in points)
sum_xy = sum(x * y for x, y in points)
sum_x2 = sum(x ** 2 for x, y in points)

# 计算斜率 (m) 和截距 (b)
denominator = n * sum_x2 - sum_x ** 2
if denominator == 0:
    print("错误：所有 x 值相同，无法计算斜率。")
    exit()

m = (n * sum_xy - sum_x * sum_y) / denominator
b = (sum_y - m * sum_x) / n

# 输出结果
print(f"\n线性回归方程为：y = {m:.4f}x + {b:.4f}")

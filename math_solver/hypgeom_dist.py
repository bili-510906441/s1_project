import sys
import math
from fractions import Fraction

def format_fraction(f):
    """格式化分数输出"""
    if f.denominator == 1:
        return f"{f.numerator}"
    return f"{f.numerator}/{f.denominator}"

# 组合函数兼容处理
if sys.version_info >= (3, 10):
    from math import comb
else:
    def comb(n, k):
        """自定义组合函数"""
        if k < 0 or k > n:
            return 0
        if k == 0 or k == n:
            return 1
        k = min(k, n - k)
        result = 1
        for i in range(1, k+1):
            result = result * (n - k + i) // i
        return result

# 输入处理
try:
    N = int(input("请输入总体数量 N: "))
    M = int(input("请输入成功项数量 M: "))
    n = int(input("请输入抽样数量 n: "))
except ValueError:
    print("输入必须为整数")
    exit()

# 参数验证
if not all([N >= 1, 0 <= M <= N, 0 <= n <= N]):
    print("参数范围错误")
    exit()

# 计算合法k范围
k_min = max(0, n + M - N)
k_max = min(n, M)
if k_min > k_max:
    print("无效参数组合")
    exit()

# 计算分布列
distribution = {}
for k in range(k_min, k_max + 1):
    c1 = comb(M, k)
    c2 = comb(N-M, n-k)
    c_total = comb(N, n)
    prob = Fraction(c1*c2, c_total) if c_total else Fraction(0)
    distribution[k] = prob

# 计算期望和方差
expectation = Fraction(n*M, N)
variance = expectation * Fraction(N-M, N) * Fraction(N-n, N-1) if N > 1 else Fraction(0)

# 输出结果
print("\n超几何分布列:")
for k in sorted(distribution):
    print(f"P(X={k}) = {format_fraction(distribution[k])}")

print(f"\n概率验证: {format_fraction(sum(distribution.values()))} = 1")
print(f"期望值: {format_fraction(expectation)} ≈ {float(expectation):.4f}")
print(f"方差值: {format_fraction(variance)} ≈ {float(variance):.4f}")
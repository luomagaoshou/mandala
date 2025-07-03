"""
文档来源：
- 文件：docs_source/topics/05_collections.ipynb
- 主题：原生处理 Python 集合
- 描述：展示了如何在记忆化过程中处理 Python 集合
- 关键概念：
  1. 集合透明性：集合元素作为独立引用
  2. 集合注解：显式声明集合类型
  3. 存储重用：共享元素的高效存储
  4. 计算图集成：集合操作作为内部操作
- 相关文档：
  - docs/docs/topics/05_collections.md
  - docs/docs/topics/03_cf.md

本示例展示了集合操作的基本功能：
1. 使用集合类型注解
2. 处理集合输入和输出
3. 分析集合的计算历史
4. 理解集合的存储机制
"""

from typing import List, Dict
from mandala.imports import Storage, op, MList, MDict

@op
def average(nums: MList[float]) -> float:
    """计算数字列表的平均值
    
    参数:
        nums: 数字列表
    返回:
        平均值
    """
    return sum(nums) / len(nums)

@op
def group_by_parity(nums: MList[int]) -> MDict[str, MList[int]]:
    """按奇偶性分组数字
    
    参数:
        nums: 数字列表
    返回:
        按奇偶分组的字典
    """
    result = {'even': [], 'odd': []}
    for num in nums:
        key = 'even' if num % 2 == 0 else 'odd'
        result[key].append(num)
    return result

@op
def sum_groups(groups: MDict[str, MList[int]]) -> MDict[str, int]:
    """计算每个分组的和
    
    参数:
        groups: 分组字典
    返回:
        每个分组的和
    """
    return {key: sum(values) for key, values in groups.items()}

def demonstrate_collections():
    """演示集合操作的基本用法"""
    storage = Storage()
    
    print("1. 基本集合操作:")
    with storage:
        # 计算平均值
        nums = [1, 2, 3, 4, 5]
        avg = average(nums)
        print(f"- 数字列表: {nums}")
        print(f"- 平均值: {avg}")
    
    print("\n2. 分析计算框架:")
    # 创建并展开计算框架
    cf = storage.cf(average).expand_all()
    print("- 计算框架结构:")
    print(cf)
    
    print("\n3. 查看数据框:")
    # 转换为数据框并显示
    df = cf.df(values='objs')
    print("- 计算历史数据框:")
    print(df)
    
    print("\n4. 复杂集合操作:")
    with storage:
        # 按奇偶性分组并计算和
        nums = list(range(10))
        groups = group_by_parity(nums)
        sums = sum_groups(groups)
        print(f"- 原始数字: {nums}")
        print(f"- 分组结果: {storage.unwrap(groups)}")
        print(f"- 分组求和: {storage.unwrap(sums)}")
    
    print("\n5. 分析复杂操作的计算框架:")
    # 创建并展开计算框架
    cf = storage.cf(sum_groups).expand_all()
    print("- 计算框架结构:")
    print(cf)

def main():
    print("演示集合操作的基本用法...")
    demonstrate_collections()

if __name__ == '__main__':
    main() 
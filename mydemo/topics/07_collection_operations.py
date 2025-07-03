"""
文档来源：
- 文件：docs_source/topics/05_collections.ipynb
- 主题：集合操作（Collection Operations）
- 描述：展示了 mandala 中如何处理和操作 Python 集合类型
- 关键概念：
  1. MList：可追踪的列表类型
  2. MDict：可追踪的字典类型
  3. 集合操作：列表和字典的基本操作
  4. 依赖追踪：集合操作的依赖管理
- 相关文档：
  - docs/docs/topics/05_collections.md
  - docs/docs/blog/02_deps.md

本示例展示了如何在 mandala 中使用集合操作。
主要功能包括：
1. 使用可追踪的列表和字典
2. 执行基本的集合操作
3. 追踪集合操作的依赖关系
4. 管理集合数据的版本
"""

import os
import numpy as np
from typing import List, Dict
from mandala.imports import Storage, op, MList, MDict

# 配置存储路径
DB_PATH = 'mandala_storage/collections_demo.db'
os.makedirs('mandala_storage', exist_ok=True)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# 创建存储实例
storage = Storage(
    db_path=DB_PATH,
)

# 设置随机种子以保证结果可重现
np.random.seed(0)

# 1. 基本集合操作示例
@op
def create_data() -> MList[float]:
    """创建一个浮点数列表。"""
    print("创建数据...")
    return [1.0, 2.0, 3.0, 4.0, 5.0]

@op
def calculate_stats(numbers: MList[float]) -> MDict[str, float]:
    """计算基本统计量。"""
    print("计算统计量...")
    return {
        "平均值": sum(numbers) / len(numbers),
        "最大值": max(numbers),
        "最小值": min(numbers),
        "总和": sum(numbers)
    }

@op
def filter_numbers(numbers: MList[float], threshold: float) -> MList[float]:
    """过滤大于阈值的数字。"""
    print(f"过滤数字 (阈值={threshold})...")
    return [x for x in numbers if x > threshold]

# 2. 集合元素重用示例
@op
def create_overlapping_lists() -> MDict[str, MList[float]]:
    """创建两个有重叠元素的列表。"""
    print("创建重叠列表...")
    return {
        "list1": [1.0, 2.0, 3.0],
        "list2": [2.0, 3.0, 4.0]
    }

@op
def find_common_elements(lists: MDict[str, MList[float]]) -> MList[float]:
    """找出两个列表的共同元素。"""
    print("查找共同元素...")
    list1 = lists["list1"]
    list2 = lists["list2"]
    return sorted(list(set(list1) & set(list2)))

# 3. 复杂集合操作示例
@op
def create_nested_structure() -> MDict[str, MList[float]]:
    """创建嵌套的数据结构。"""
    print("创建嵌套结构...")
    return {
        "组A": [1.0, 2.0, 3.0],
        "组B": [4.0, 5.0, 6.0],
        "组C": [2.0, 4.0, 6.0]
    }

@op
def analyze_groups(data: MDict[str, MList[float]]) -> MDict[str, MDict[str, float]]:
    """分析每个组的统计信息。"""
    print("分析组数据...")
    results = {}
    for group_name, numbers in data.items():
        results[group_name] = {
            "平均值": sum(numbers) / len(numbers),
            "最大值": max(numbers),
            "最小值": min(numbers)
        }
    return results

def demo_basic_operations():
    """演示基本集合操作。"""
    print("\n1. 基本集合操作示例")
    print("-" * 50)
    
    with storage:
        # 创建数据并计算统计量
        numbers = create_data()
        stats = calculate_stats(numbers)
        print("统计结果:", stats)
        
        # 过滤数据
        filtered = filter_numbers(numbers, 2.5)
        filtered_stats = calculate_stats(filtered)
        print("过滤后的统计结果:", filtered_stats)
    
    # 分析计算图
    print("\n计算图分析:")
    cf = storage.cf(calculate_stats).expand_all()
    print(cf)
    print("\n计算图数据框:")
    print(cf.df(values='objs').to_markdown())

def demo_element_reuse():
    """演示集合元素重用。"""
    print("\n2. 集合元素重用示例")
    print("-" * 50)
    
    with storage:
        # 创建重叠列表并找出共同元素
        lists = create_overlapping_lists()
        common = find_common_elements(lists)
        print("共同元素:", common)
    
    # 分析计算图
    print("\n计算图分析:")
    cf = storage.cf(find_common_elements).expand_all()
    print(cf)

def demo_complex_operations():
    """演示复杂集合操作。"""
    print("\n3. 复杂集合操作示例")
    print("-" * 50)
    
    with storage:
        # 创建嵌套结构并分析
        data = create_nested_structure()
        analysis = analyze_groups(data)
        print("分组分析结果:")
        for group, stats in analysis.items():
            print(f"{group}:", stats)
    
    # 分析计算图
    print("\n计算图分析:")
    cf = storage.cf(analyze_groups).expand_all()
    print(cf)

def main():
    """运行所有示例。"""
    demo_basic_operations()
    demo_element_reuse()
    demo_complex_operations()

if __name__ == "__main__":
    main() 
"""
文档来源：
- 文件：docs_source/topics/06_advanced_cf.ipynb
- 主题：高级计算框架（Advanced ComputationFrame）
- 描述：展示了 mandala 计算框架的高级功能，包括集合操作和计算图分析
- 关键概念：
  1. 计算框架合并：并集和交集操作
  2. 上下游分析：依赖关系追踪
  3. 计算图可视化：复杂计算链展示
  4. 计算框架过滤：按条件筛选操作
- 相关文档：
  - docs/docs/topics/06_advanced_cf.md
  - docs/docs/blog/01_cf.md

本示例展示了如何使用 mandala 的高级计算框架功能。
主要功能包括：
1. 计算框架的集合操作
2. 计算图的上下游分析
3. 复杂计算链的可视化
4. 计算框架的过滤和筛选
"""

import os
import numpy as np
from mandala.imports import Storage, op, MList, MDict

storage = Storage()

@op
def inc(x): return x + 1

@op
def add(y, z): return y + z

@op
def square(w): return w ** 2

@op
def divmod_(u, v): return divmod(u, v)

def demo_set_operations():
    """演示计算框架的集合操作。"""
    print("\n1. 计算框架的集合操作")
    print("-" * 50)
    
    with storage:
        # 创建计算链
        xs = [inc(i) for i in range(5)]
        ys = [add(x, z=42) for x in xs] + [square(x) for x in range(5, 10)]
        zs = [divmod_(x, y) for x, y in zip(xs, ys[3:8])]
    
    
    # 获取计算框架
    cf_add = storage.cf(add).expand_all()
    cf_square = storage.cf(square).expand_all()
    
    print("\n计算框架 add:")
    print(cf_add)
    
    print("\n计算框架 square:")
    print(cf_square)
    
    print("\n合并后的计算框架 (并集):")
    cf_union = cf_add | cf_square
    print(cf_union)
    

def demo_graph_operations():
    """演示计算图的上下游分析。"""
    print("\n2. 计算图的上下游分析")
    print("-" * 50)
    
    with storage:
        # 创建计算链
        xs = [inc(i) for i in range(5)]
        ys = [add(x, z=42) for x in xs]
        zs = [divmod_(x, y) for x, y in zip(xs, ys)]
    
    # 获取计算框架
    cf = storage.cf(divmod_).expand_all()
    
    print("\n原始计算框架:")
    print(cf)
    
    print("\n上游计算 (从divmod_到输入):")
    # 获取所有变量名
    var_names = cf.vs.keys()
    print("可用的变量名:", var_names)
    
    # 选择一个变量名进行上游分析
    target_var = next(iter(var_names))
    cf_upstream = cf.upstream(target_var)
    print(f"\n变量 {target_var} 的上游计算:")
    print(cf_upstream)
    
    print("\n下游计算 (从变量到输出):")
    cf_downstream = cf.downstream(target_var)
    print(f"\n变量 {target_var} 的下游计算:")
    print(cf_downstream)

def main():
    """运行所有示例。"""
    print("开始运行高级计算框架工具示例...")
    demo_set_operations()
    demo_graph_operations()
    print("\n示例运行完成。")

if __name__ == "__main__":
    main()

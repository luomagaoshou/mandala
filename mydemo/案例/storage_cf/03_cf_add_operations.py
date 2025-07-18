#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComputationFrame增加操作详解
===========================

本文件详细展示ComputationFrame的各种增加操作，
包括添加节点、边、引用、调用等功能。
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from mandala1.imports import *
import pandas as pd
import numpy as np

def demo_add_variables():
    """演示添加变量操作"""
    print("="*60)
    print("ComputationFrame添加变量操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建基础计算图
    @op(output_names=['result'])
    def base_function(x: int) -> int:
        return x * 2
    
    with storage:
        for i in range(3):
            base_function(i)
    
    # 创建基础CF
    cf = storage.cf(base_function)
    print(f"\n1. 原始CF状态:")
    print(f"   变量节点: {cf.vnames}")
    print(f"   函数节点: {cf.fnames}")
    print(f"   节点总数: {len(cf.nodes)}")
    
    # 添加新变量
    print(f"\n2. 添加新变量:")
    
    # 使用_add_var添加变量
    new_var_name = cf._add_var("new_variable")
    print(f"   添加变量: {new_var_name}")
    print(f"   更新后变量节点: {cf.vnames}")
    print(f"   更新后节点总数: {len(cf.nodes)}")
    
    # 添加另一个变量
    another_var_name = cf._add_var("another_var")
    print(f"   添加变量: {another_var_name}")
    print(f"   更新后变量节点: {cf.vnames}")
    
    # 添加变量时自动生成名称
    auto_var_name = cf._add_var(None)
    print(f"   自动生成变量: {auto_var_name}")
    print(f"   最终变量节点: {cf.vnames}")
    
    print(f"\n3. 查看变量内容:")
    for vname in cf.vnames:
        print(f"   变量 {vname}: {len(cf.vs[vname])} 个元素")
    
    return storage, cf

def demo_expand_operations():
    """演示扩展操作"""
    print("\n" + "="*60)
    print("ComputationFrame扩展操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建复杂计算图
    @op(output_names=['doubled'])
    def double_value(x: int) -> int:
        return x * 2
    
    @op(output_names=['added'])
    def add_value(x: int, y: int) -> int:
        return x + y
    
    @op(output_names=['result'])
    def complex_process(x: int) -> int:
        doubled = double_value(x)
        result = add_value(doubled, x)
        return result
    
    with storage:
        for i in range(3):
            complex_process(i)
    
    # 创建不同级别的CF
    cf_double = storage.cf(double_value)
    cf_add = storage.cf(add_value)
    cf_complex = storage.cf(complex_process)
    
    print(f"\n1. 原始CF状态:")
    print(f"   double_value CF: {len(cf_double.nodes)} 个节点")
    print(f"   add_value CF: {len(cf_add.nodes)} 个节点")
    print(f"   complex_process CF: {len(cf_complex.nodes)} 个节点")
    
    print(f"\n2. 向后扩展 (expand_back):")
    
    # 向后扩展complex_process
    cf_complex_back = cf_complex.expand_back()
    print(f"   complex_process 向后扩展: {len(cf_complex_back.nodes)} 个节点")
    print(f"   扩展后节点: {cf_complex_back.nodes}")
    
    print(f"\n3. 向前扩展 (expand_forward):")
    
    # 向前扩展double_value
    cf_double_forward = cf_double.expand_forward()
    print(f"   double_value 向前扩展: {len(cf_double_forward.nodes)} 个节点")
    print(f"   扩展后节点: {cf_double_forward.nodes}")
    
    print(f"\n4. 全方向扩展 (expand_all):")
    
    # 全方向扩展
    cf_complex_all = cf_complex.expand_all()
    print(f"   complex_process 全扩展: {len(cf_complex_all.nodes)} 个节点")
    print(f"   扩展后节点: {cf_complex_all.nodes}")
    
    # 显示完整图结构
    print(f"\n5. 完整扩展后的图结构:")
    cf_complex_all.print_graph()
    
    return storage, cf_complex_all

def demo_union_operations():
    """演示联合操作"""
    print("\n" + "="*60)
    print("ComputationFrame联合操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建多个独立的计算图
    @op(output_names=['result1'])
    def operation1(x: int) -> int:
        return x * 2
    
    @op(output_names=['result2'])
    def operation2(x: int) -> int:
        return x + 5
    
    @op(output_names=['result3'])
    def operation3(x: int, y: int) -> int:
        return x * y
    
    with storage:
        # 创建第一组计算
        for i in range(3):
            operation1(i)
        
        # 创建第二组计算
        for i in range(2, 5):
            operation2(i)
        
        # 创建第三组计算
        for i in range(2):
            for j in range(2):
                operation3(i, j)
    
    # 创建多个CF
    cf1 = storage.cf(operation1)
    cf2 = storage.cf(operation2)
    cf3 = storage.cf(operation3)
    
    print(f"\n1. 原始CF状态:")
    print(f"   CF1 (operation1): {len(cf1.nodes)} 个节点")
    print(f"   CF2 (operation2): {len(cf2.nodes)} 个节点")
    print(f"   CF3 (operation3): {len(cf3.nodes)} 个节点")
    
    print(f"\n2. 联合操作:")
    
    # 二元联合
    cf_union_12 = cf1 | cf2
    print(f"   CF1 | CF2: {len(cf_union_12.nodes)} 个节点")
    print(f"   联合后节点: {cf_union_12.nodes}")
    
    # 多元联合
    cf_union_all = ComputationFrame.union(cf1, cf2, cf3)
    print(f"   CF1 ∪ CF2 ∪ CF3: {len(cf_union_all.nodes)} 个节点")
    print(f"   联合后节点: {cf_union_all.nodes}")
    
    print(f"\n3. 联合后的数据:")
    df_union = cf_union_all.df()
    print(f"   联合数据框架 (shape: {df_union.shape}):")
    print(df_union.head())
    
    return storage, cf_union_all

if __name__ == "__main__":
    print("开始ComputationFrame增加操作演示")
    
    # 运行各个演示
    storage1, cf1 = demo_add_variables()
    storage2, cf2 = demo_expand_operations()
    storage3, cf3 = demo_union_operations()
    
    print("\n" + "="*60)
    print("ComputationFrame增加操作总结")
    print("="*60)
    print("""
ComputationFrame提供了丰富的增加功能:

1. 添加基本元素:
   - 添加变量节点 (_add_var)
   - 添加函数节点 (_add_func)
   - 添加边 (_add_edge)

2. 扩展操作:
   - 向后扩展 (expand_back)
   - 向前扩展 (expand_forward)
   - 全方向扩展 (expand_all)

3. 联合操作:
   - 二元联合 (|运算符)
   - 多元联合 (union静态方法)
   - 从多个CF合并数据

这些功能支持灵活的计算图构建和扩展。
    """) 
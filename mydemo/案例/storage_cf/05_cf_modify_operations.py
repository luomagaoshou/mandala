#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComputationFrame修改操作详解
===========================

本文件详细展示ComputationFrame的各种修改操作，
包括重命名、移动、合并、分割等功能。
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from mandala1.imports import *
import pandas as pd
import numpy as np

def demo_rename_operations():
    """演示重命名操作"""
    print("="*60)
    print("ComputationFrame重命名操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建计算图
    @op(output_names=['result'])
    def calculate_value(x: int) -> int:
        return x * 2 + 1
    
    with storage:
        for i in range(4):
            calculate_value(i)
    
    # 创建CF
    cf = storage.cf(calculate_value)
    
    print(f"\n1. 原始CF状态:")
    print(f"   变量节点: {cf.vnames}")
    print(f"   函数节点: {cf.fnames}")
    print(f"   所有节点: {cf.nodes}")
    
    print(f"\n2. 重命名变量:")
    
    # 重命名变量
    if cf.vnames:
        old_vname = list(cf.vnames)[0]
        new_vname = "renamed_input"
        cf_renamed = cf.rename_var(old_vname, new_vname)
        
        print(f"   重命名变量: {old_vname} -> {new_vname}")
        print(f"   重命名后变量节点: {cf_renamed.vnames}")
        print(f"   重命名后所有节点: {cf_renamed.nodes}")
    
    print(f"\n3. 批量重命名:")
    
    # 批量重命名多个变量
    if len(cf.vnames) > 1:
        var_list = list(cf.vnames)
        rename_dict = {
            var_list[0]: "input_data",
            var_list[1]: "output_data"
        }
        cf_batch_renamed = cf.rename(vars=rename_dict)
        
        print(f"   批量重命名: {rename_dict}")
        print(f"   批量重命名后变量节点: {cf_batch_renamed.vnames}")
    
    print(f"\n4. 就地重命名:")
    
    # 就地重命名
    cf_copy = cf.copy()
    if cf_copy.vnames:
        old_vname = list(cf_copy.vnames)[0]
        new_vname = "inplace_renamed"
        cf_copy.rename_var(old_vname, new_vname, inplace=True)
        
        print(f"   就地重命名: {old_vname} -> {new_vname}")
        print(f"   就地重命名后变量节点: {cf_copy.vnames}")
    
    return storage, cf

def demo_move_operations():
    """演示移动操作"""
    print("\n" + "="*60)
    print("ComputationFrame移动操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建计算图
    @op(output_names=['result'])
    def generate_data(x: int) -> int:
        return x * 3
    
    with storage:
        for i in range(5):
            generate_data(i)
    
    # 创建CF并添加额外变量
    cf = storage.cf(generate_data)
    
    # 添加新变量
    new_var1 = cf._add_var("target_var1")
    new_var2 = cf._add_var("target_var2")
    
    print(f"\n1. 原始CF状态:")
    print(f"   变量节点: {cf.vnames}")
    
    # 显示每个变量的内容
    for vname in cf.vnames:
        print(f"   变量 {vname}: {len(cf.vs[vname])} 个元素")
    
    print(f"\n2. 移动引用:")
    
    # 移动引用从一个变量到另一个变量
    source_var = None
    target_var = new_var1
    
    for vname in cf.vnames:
        if cf.vs[vname]:  # 找到有引用的变量
            source_var = vname
            break
    
    if source_var and cf.vs[source_var]:
        ref_to_move = list(cf.vs[source_var])[0]
        print(f"   移动引用 {ref_to_move} 从 {source_var} 到 {target_var}")
        
        # 移动引用
        cf.move_ref(source_var, target_var, ref_to_move)
        
        print(f"   移动后状态:")
        print(f"   源变量 {source_var}: {len(cf.vs[source_var])} 个元素")
        print(f"   目标变量 {target_var}: {len(cf.vs[target_var])} 个元素")
    
    print(f"\n3. 就地移动:")
    
    # 就地移动另一个引用
    if source_var and cf.vs[source_var]:
        ref_to_move = list(cf.vs[source_var])[0]
        print(f"   就地移动引用 {ref_to_move} 从 {source_var} 到 {new_var2}")
        
        cf.move_ref(source_var, new_var2, ref_to_move, inplace=True)
        
        print(f"   就地移动后状态:")
        print(f"   源变量 {source_var}: {len(cf.vs[source_var])} 个元素")
        print(f"   目标变量 {new_var2}: {len(cf.vs[new_var2])} 个元素")
    
    return storage, cf

def demo_merge_operations():
    """演示合并操作"""
    print("\n" + "="*60)
    print("ComputationFrame合并操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建计算图
    @op(output_names=['result'])
    def process_item(x: int) -> int:
        return x * 2 + 1
    
    with storage:
        for i in range(3):
            process_item(i)
    
    # 创建CF
    cf = storage.cf(process_item)
    
    # 创建重复的变量（模拟需要合并的情况）
    duplicate_var = cf._add_var("duplicate_var")
    
    # 向重复变量添加一些相同的引用
    if cf.vnames:
        original_var = list(cf.vnames)[0]
        if cf.vs[original_var]:
            # 复制一个引用到重复变量
            ref_to_copy = list(cf.vs[original_var])[0]
            cf.add_ref(duplicate_var, cf.refs[ref_to_copy])
    
    print(f"\n1. 合并前状态:")
    print(f"   变量节点: {cf.vnames}")
    
    # 显示变量内容
    for vname in cf.vnames:
        print(f"   变量 {vname}: {len(cf.vs[vname])} 个元素")
    
    print(f"\n2. 合并变量:")
    
    # 合并变量
    if len(cf.vnames) > 1:
        var_list = list(cf.vnames)
        source_var = duplicate_var
        target_var = var_list[0] if var_list[0] != duplicate_var else var_list[1]
        
        print(f"   合并变量 {source_var} 到 {target_var}")
        
        # 合并操作
        cf_merged = cf.merge_into(source_var, target_var)
        
        print(f"   合并后变量节点: {cf_merged.vnames}")
        print(f"   合并后节点数: {len(cf_merged.nodes)}")
    
    print(f"\n3. 自动合并变量:")
    
    # 自动合并所有可以合并的变量
    cf_auto_merged = cf.merge_vars()
    print(f"   自动合并后变量节点: {cf_auto_merged.vnames}")
    print(f"   自动合并后节点数: {len(cf_auto_merged.nodes)}")
    
    return storage, cf

def demo_copy_operations():
    """演示复制操作"""
    print("\n" + "="*60)
    print("ComputationFrame复制操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建计算图
    @op(output_names=['result'])
    def transform_data(x: int) -> int:
        return x ** 2
    
    with storage:
        for i in range(4):
            transform_data(i)
    
    # 创建CF
    cf = storage.cf(transform_data)
    
    print(f"\n1. 原始CF状态:")
    print(f"   节点数: {len(cf.nodes)}")
    print(f"   变量节点: {cf.vnames}")
    print(f"   函数节点: {cf.fnames}")
    print(f"   CF对象ID: {id(cf)}")
    
    print(f"\n2. 浅复制:")
    
    # 浅复制
    cf_copy = cf.copy()
    print(f"   复制后CF对象ID: {id(cf_copy)}")
    print(f"   复制后节点数: {len(cf_copy.nodes)}")
    print(f"   复制后变量节点: {cf_copy.vnames}")
    
    # 验证是否是独立的副本
    print(f"\n3. 验证独立性:")
    
    # 修改原始CF
    original_node_count = len(cf.nodes)
    test_var = cf._add_var("test_independence")
    print(f"   原始CF添加变量后节点数: {len(cf.nodes)}")
    print(f"   复制CF节点数: {len(cf_copy.nodes)}")
    print(f"   是否独立: {len(cf.nodes) != len(cf_copy.nodes)}")
    
    # 修改复制CF
    cf_copy._add_var("copy_test_var")
    print(f"   复制CF添加变量后节点数: {len(cf_copy.nodes)}")
    print(f"   原始CF节点数: {len(cf.nodes)}")
    
    return storage, cf

def demo_apply_operations():
    """演示应用操作"""
    print("\n" + "="*60)
    print("ComputationFrame应用操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建计算图
    @op(output_names=['result'])
    def base_calculation(x: int) -> int:
        return x * 2
    
    with storage:
        for i in range(5):
            base_calculation(i)
    
    # 创建CF
    cf = storage.cf(base_calculation)
    
    print(f"\n1. 原始CF状态:")
    df_original = cf.df()
    print(f"   数据框架 (shape: {df_original.shape}):")
    print(df_original)
    
    print(f"\n2. 应用函数到值:")
    
    # 应用函数到值
    def add_one(x):
        return x + 1
    
    cf_applied = cf.apply(add_one, to="vals")
    print(f"   应用add_one函数到值:")
    df_applied = cf_applied.df()
    print(f"   应用后数据框架 (shape: {df_applied.shape}):")
    print(df_applied)
    
    print(f"\n3. 应用函数到引用:")
    
    # 应用函数到引用对象
    def modify_ref(ref):
        # 这里只是示例，实际修改引用对象需要谨慎
        return ref
    
    cf_ref_applied = cf.apply(modify_ref, to="refs")
    print(f"   应用函数到引用对象:")
    print(f"   应用后节点数: {len(cf_ref_applied.nodes)}")
    
    return storage, cf

def demo_unwrap_operations():
    """演示解包操作"""
    print("\n" + "="*60)
    print("ComputationFrame解包操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建计算图
    @op(output_names=['result'])
    def create_values(x: int) -> int:
        return x * 3 + 2
    
    with storage:
        for i in range(4):
            create_values(i)
    
    # 创建CF
    cf = storage.cf(create_values)
    
    print(f"\n1. 原始CF状态:")
    print(f"   节点数: {len(cf.nodes)}")
    
    # 显示引用形式的数据
    df_refs = cf.df(values="refs")
    print(f"   引用形式数据 (shape: {df_refs.shape}):")
    print(df_refs.head())
    
    print(f"\n2. 解包为实际值:")
    
    # 解包为实际值
    df_values = cf.df(values="objs")
    print(f"   实际值数据 (shape: {df_values.shape}):")
    print(df_values.head())
    
    print(f"\n3. 附加操作:")
    
    # 附加引用到内存
    for vname in cf.vnames:
        refs = cf.get_var_values(vname)
        print(f"   变量 {vname} 的引用状态:")
        for ref in list(refs)[:3]:  # 显示前3个
            print(f"     {ref.hid}: in_memory={ref.in_memory}")
    
    # 附加所有引用到内存
    cf.attach()
    
    print(f"   附加后的引用状态:")
    for vname in cf.vnames:
        refs = cf.get_var_values(vname)
        for ref in list(refs)[:3]:
            print(f"     {ref.hid}: in_memory={ref.in_memory}")
    
    return storage, cf

def demo_eval_operations():
    """演示评估操作"""
    print("\n" + "="*60)
    print("ComputationFrame评估操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建计算图
    @op(output_names=['squared'])
    def square_number(x: int) -> int:
        return x ** 2
    
    @op(output_names=['result'])
    def add_constant(x: int) -> int:
        return x + 10
    
    with storage:
        for i in range(3):
            squared = square_number(i)
            add_constant(squared)
    
    # 创建完整的CF
    cf = storage.cf(add_constant).expand_all()
    
    print(f"\n1. 原始CF状态:")
    print(f"   节点数: {len(cf.nodes)}")
    print(f"   变量节点: {cf.vnames}")
    print(f"   函数节点: {cf.fnames}")
    
    print(f"\n2. 评估操作:")
    
    # 评估所有数据
    df_evaluated = cf.eval()
    print(f"   评估结果 (shape: {df_evaluated.shape}):")
    print(df_evaluated)
    
    # 评估特定节点
    if len(cf.vnames) > 1:
        selected_vars = list(cf.vnames)[:2]
        df_selected = cf.eval(*selected_vars)
        print(f"   选择性评估 {selected_vars} (shape: {df_selected.shape}):")
        print(df_selected)
    
    print(f"\n3. 评估模式:")
    
    # 不同的评估模式
    df_refs = cf.eval(values="refs")
    print(f"   引用模式评估 (shape: {df_refs.shape}):")
    print(df_refs.head())
    
    df_objs = cf.eval(values="objs")
    print(f"   对象模式评估 (shape: {df_objs.shape}):")
    print(df_objs.head())
    
    return storage, cf

def demo_dataframe_operations():
    """演示数据框架操作"""
    print("\n" + "="*60)
    print("ComputationFrame数据框架操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建计算图
    @op(output_names=['processed'])
    def process_value(x: int) -> int:
        return x * 2 + 1
    
    with storage:
        for i in range(6):
            process_value(i)
    
    # 创建CF
    cf = storage.cf(process_value)
    
    print(f"\n1. 原始数据框架:")
    df_original = cf.df()
    print(f"   数据框架 (shape: {df_original.shape}):")
    print(df_original)
    
    print(f"\n2. 数据框架评估:")
    
    # 评估数据框架
    df_evaluated = cf.eval_df(df_original)
    print(f"   评估后数据框架 (shape: {df_evaluated.shape}):")
    print(df_evaluated)
    
    print(f"\n3. 选择性评估:")
    
    # 跳过某些列的评估
    if len(df_original.columns) > 1:
        skip_cols = [df_original.columns[0]]
        df_selective = cf.eval_df(df_original, skip_cols=skip_cols)
        print(f"   跳过列 {skip_cols} 的评估:")
        print(df_selective)
    
    print(f"\n4. 跳过调用评估:")
    
    # 跳过调用列
    df_no_calls = cf.eval_df(df_original, skip_calls=True)
    print(f"   跳过调用的评估 (shape: {df_no_calls.shape}):")
    print(df_no_calls)
    
    return storage, cf

if __name__ == "__main__":
    print("开始ComputationFrame修改操作演示")
    
    # 运行各个演示
    storage1, cf1 = demo_rename_operations()
    storage2, cf2 = demo_move_operations()
    storage3, cf3 = demo_merge_operations()
    storage4, cf4 = demo_copy_operations()
    storage5, cf5 = demo_apply_operations()
    storage6, cf6 = demo_unwrap_operations()
    storage7, cf7 = demo_eval_operations()
    storage8, cf8 = demo_dataframe_operations()
    
    print("\n" + "="*60)
    print("ComputationFrame修改操作总结")
    print("="*60)
    print("""
ComputationFrame提供了丰富的修改功能:

1. 重命名操作:
   - 重命名变量 (rename_var)
   - 批量重命名 (rename)
   - 支持就地重命名 (inplace=True)

2. 移动操作:
   - 移动引用 (move_ref)
   - 在变量间转移数据
   - 维护引用完整性

3. 合并操作:
   - 合并节点 (merge_into)
   - 自动合并变量 (merge_vars)
   - 减少冗余节点

4. 复制操作:
   - 深复制 (copy)
   - 创建独立副本
   - 支持并行修改

5. 应用操作:
   - 应用函数到值 (apply)
   - 应用函数到引用
   - 批量转换

6. 解包操作:
   - 解包引用 (unwrap)
   - 附加到内存 (attach)
   - 值形式转换

7. 评估操作:
   - 评估数据 (eval)
   - 数据框架评估 (eval_df)
   - 选择性评估

8. 数据框架操作:
   - 不同评估模式
   - 列选择控制
   - 调用过滤

这些功能支持灵活的计算图修改和数据转换，
可以根据需要调整图结构和数据表示形式。
    """) 
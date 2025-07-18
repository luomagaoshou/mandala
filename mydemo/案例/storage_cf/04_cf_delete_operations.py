#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComputationFrame删除操作详解
===========================

本文件详细展示ComputationFrame的各种删除操作，
包括删除节点、边、引用、调用等功能。
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from mandala1.imports import *
import pandas as pd
import numpy as np

def demo_drop_nodes():
    """演示删除节点操作"""
    print("="*60)
    print("ComputationFrame删除节点操作")
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
    
    # 创建完整的CF
    cf = storage.cf(complex_process).expand_all()
    print(f"\n1. 原始CF状态:")
    print(f"   节点数: {len(cf.nodes)}")
    print(f"   变量节点: {cf.vnames}")
    print(f"   函数节点: {cf.fnames}")
    print(f"   边数: {len(cf.edges())}")
    
    # 显示原始图结构
    print(f"\n2. 原始图结构:")
    cf.print_graph()
    
    print(f"\n3. 删除单个节点:")
    
    # 删除变量节点
    if cf.vnames:
        node_to_drop = list(cf.vnames)[0]
        cf_after_drop = cf.drop_node(node_to_drop)
        print(f"   删除变量节点: {node_to_drop}")
        print(f"   删除后节点数: {len(cf_after_drop.nodes)}")
        print(f"   删除后变量节点: {cf_after_drop.vnames}")
        print(f"   删除后边数: {len(cf_after_drop.edges())}")
    
    print(f"\n4. 批量删除节点:")
    
    # 批量删除多个节点
    if len(cf.nodes) > 2:
        nodes_to_drop = list(cf.nodes)[:2]
        cf_batch_drop = cf.drop(nodes_to_drop)
        print(f"   删除节点: {nodes_to_drop}")
        print(f"   删除后节点数: {len(cf_batch_drop.nodes)}")
        print(f"   删除后节点: {cf_batch_drop.nodes}")
    
    print(f"\n5. 就地删除:")
    
    # 就地删除操作
    cf_copy = cf.copy()
    if cf_copy.nodes:
        node_to_drop = list(cf_copy.nodes)[0]
        print(f"   就地删除节点: {node_to_drop}")
        cf_copy.drop_node(node_to_drop, inplace=True)
        print(f"   就地删除后节点数: {len(cf_copy.nodes)}")
    
    return storage, cf

def demo_drop_variables():
    """演示删除变量操作"""
    print("\n" + "="*60)
    print("ComputationFrame删除变量操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建计算图
    @op(output_names=['result'])
    def process_data(x: int) -> int:
        return x * 3
    
    with storage:
        for i in range(4):
            process_data(i)
    
    # 创建CF并手动添加变量
    cf = storage.cf(process_data)
    
    # 添加额外的变量
    extra_var1 = cf._add_var("extra_var1")
    extra_var2 = cf._add_var("extra_var2")
    
    print(f"\n1. 添加额外变量后的状态:")
    print(f"   变量节点: {cf.vnames}")
    print(f"   变量数量: {len(cf.vnames)}")
    
    # 显示每个变量的内容
    for vname in cf.vnames:
        print(f"   变量 {vname}: {len(cf.vs[vname])} 个元素")
    
    print(f"\n2. 删除变量:")
    
    # 删除额外添加的变量
    cf_after_drop = cf.drop_var(extra_var1)
    print(f"   删除变量: {extra_var1}")
    print(f"   删除后变量节点: {cf_after_drop.vnames}")
    print(f"   删除后变量数量: {len(cf_after_drop.vnames)}")
    
    print(f"\n3. 就地删除变量:")
    
    # 就地删除操作
    cf_copy = cf.copy()
    cf_copy.drop_var(extra_var2, inplace=True)
    print(f"   就地删除变量: {extra_var2}")
    print(f"   就地删除后变量节点: {cf_copy.vnames}")
    
    return storage, cf

def demo_drop_functions():
    """演示删除函数操作"""
    print("\n" + "="*60)
    print("ComputationFrame删除函数操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建多个函数的计算图
    @op(output_names=['result1'])
    def function1(x: int) -> int:
        return x * 2
    
    @op(output_names=['result2'])
    def function2(x: int) -> int:
        return x + 5
    
    @op(output_names=['result3'])
    def function3(x: int, y: int) -> int:
        return x * y
    
    with storage:
        for i in range(3):
            function1(i)
            function2(i)
            if i > 0:
                function3(i, i-1)
    
    # 创建联合CF
    cf1 = storage.cf(function1)
    cf2 = storage.cf(function2)
    cf3 = storage.cf(function3)
    cf_union = cf1 | cf2 | cf3
    
    print(f"\n1. 原始联合CF状态:")
    print(f"   函数节点: {cf_union.fnames}")
    print(f"   变量节点: {cf_union.vnames}")
    print(f"   节点总数: {len(cf_union.nodes)}")
    
    # 显示每个函数的调用数
    for fname in cf_union.fnames:
        print(f"   函数 {fname}: {len(cf_union.fs[fname])} 个调用")
    
    print(f"\n2. 删除函数:")
    
    # 删除一个函数
    if cf_union.fnames:
        func_to_drop = list(cf_union.fnames)[0]
        cf_after_drop = cf_union.drop_func(func_to_drop)
        print(f"   删除函数: {func_to_drop}")
        print(f"   删除后函数节点: {cf_after_drop.fnames}")
        print(f"   删除后节点总数: {len(cf_after_drop.nodes)}")
    
    print(f"\n3. 就地删除函数:")
    
    # 就地删除操作
    cf_copy = cf_union.copy()
    if len(cf_copy.fnames) > 1:
        func_to_drop = list(cf_copy.fnames)[1]
        cf_copy.drop_func(func_to_drop, inplace=True)
        print(f"   就地删除函数: {func_to_drop}")
        print(f"   就地删除后函数节点: {cf_copy.fnames}")
    
    return storage, cf_union

def demo_drop_refs():
    """演示删除引用操作"""
    print("\n" + "="*60)
    print("ComputationFrame删除引用操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建计算图
    @op(output_names=['result'])
    def generate_data(x: int) -> int:
        return x * 2
    
    with storage:
        for i in range(5):
            generate_data(i)
    
    # 创建CF
    cf = storage.cf(generate_data)
    
    print(f"\n1. 原始CF状态:")
    for vname in cf.vnames:
        refs = cf.get_var_values(vname)
        print(f"   变量 {vname}: {len(refs)} 个引用")
        for ref in list(refs)[:3]:  # 显示前3个
            print(f"     {ref.hid}: {storage.unwrap(ref)}")
    
    print(f"\n2. 删除引用:")
    
    # 从变量中删除引用
    for vname in cf.vnames:
        if cf.vs[vname]:  # 如果变量有引用
            ref_to_drop = list(cf.vs[vname])[0]  # 取第一个引用
            print(f"   从变量 {vname} 删除引用: {ref_to_drop}")
            cf.drop_ref(vname, ref_to_drop)
            
            # 显示删除后的状态
            print(f"   删除后变量 {vname}: {len(cf.vs[vname])} 个引用")
            break
    
    print(f"\n3. 验证引用删除:")
    
    # 显示所有变量的引用状态
    for vname in cf.vnames:
        refs = cf.get_var_values(vname)
        print(f"   变量 {vname}: {len(refs)} 个引用")
        for ref in list(refs)[:3]:
            print(f"     {ref.hid}: {storage.unwrap(ref)}")
    
    return storage, cf

def demo_drop_calls():
    """演示删除调用操作"""
    print("\n" + "="*60)
    print("ComputationFrame删除调用操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建计算图
    @op(output_names=['result'])
    def compute_value(x: int) -> int:
        return x ** 2
    
    with storage:
        for i in range(4):
            compute_value(i)
    
    # 创建CF
    cf = storage.cf(compute_value)
    
    print(f"\n1. 原始CF状态:")
    for fname in cf.fnames:
        calls = cf.calls_by_func()[fname]
        print(f"   函数 {fname}: {len(calls)} 个调用")
        for call in list(calls)[:3]:  # 显示前3个
            inputs_str = {k: storage.unwrap(v) for k, v in call.inputs.items()}
            outputs_str = {k: storage.unwrap(v) for k, v in call.outputs.items()}
            print(f"     {call.hid}: {inputs_str} -> {outputs_str}")
    
    print(f"\n2. 删除调用:")
    
    # 从函数中删除调用
    for fname in cf.fnames:
        if cf.fs[fname]:  # 如果函数有调用
            call_to_drop = list(cf.fs[fname])[0]  # 取第一个调用
            print(f"   从函数 {fname} 删除调用: {call_to_drop}")
            cf.drop_call(fname, call_to_drop)
            
            # 显示删除后的状态
            print(f"   删除后函数 {fname}: {len(cf.fs[fname])} 个调用")
            break
    
    print(f"\n3. 验证调用删除:")
    
    # 显示所有函数的调用状态
    for fname in cf.fnames:
        calls = cf.calls_by_func()[fname]
        print(f"   函数 {fname}: {len(calls)} 个调用")
        for call in list(calls)[:3]:
            inputs_str = {k: storage.unwrap(v) for k, v in call.inputs.items()}
            outputs_str = {k: storage.unwrap(v) for k, v in call.outputs.items()}
            print(f"     {call.hid}: {inputs_str} -> {outputs_str}")
    
    return storage, cf

def demo_filtering_operations():
    """演示过滤操作（另一种删除方式）"""
    print("\n" + "="*60)
    print("ComputationFrame过滤操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建计算图
    @op(output_names=['result'])
    def process_numbers(x: int) -> int:
        return x * 3 - 1
    
    with storage:
        for i in range(-2, 5):
            process_numbers(i)
    
    # 创建CF
    cf = storage.cf(process_numbers)
    
    print(f"\n1. 原始CF状态:")
    df_original = cf.df()
    print(f"   数据框架 (shape: {df_original.shape}):")
    print(df_original)
    
    print(f"\n2. 值过滤 (保留特定值):")
    
    # 过滤特定值
    values_to_keep = [2, 5, 8]
    cf_filtered = cf.isin(values_to_keep, by="val")
    print(f"   保留值 {values_to_keep} 的元素:")
    print(f"   过滤后节点数: {len(cf_filtered.nodes)}")
    
    df_filtered = cf_filtered.df()
    print(f"   过滤后数据框架 (shape: {df_filtered.shape}):")
    print(df_filtered)
    
    print(f"\n3. 条件过滤:")
    
    # 条件过滤
    try:
        cf_condition = cf < 5
        print(f"   保留值小于5的元素:")
        print(f"   过滤后节点数: {len(cf_condition.nodes)}")
        
        df_condition = cf_condition.df()
        print(f"   条件过滤后数据框架 (shape: {df_condition.shape}):")
        print(df_condition)
    except Exception as e:
        print(f"   条件过滤失败: {e}")
    
    return storage, cf

def demo_drop_unreachable():
    """演示删除不可达元素"""
    print("\n" + "="*60)
    print("ComputationFrame删除不可达元素")
    print("="*60)
    
    storage = Storage()
    
    # 创建复杂计算图
    @op(output_names=['result1'])
    def step1(x: int) -> int:
        return x * 2
    
    @op(output_names=['result2'])
    def step2(x: int) -> int:
        return x + 3
    
    @op(output_names=['final'])
    def final_step(x: int, y: int) -> int:
        return x * y
    
    with storage:
        for i in range(3):
            r1 = step1(i)
            r2 = step2(i)
            if i % 2 == 0:  # 只有部分数据参与最终计算
                final_step(r1, r2)
    
    # 创建完整的CF
    cf = storage.cf(final_step).expand_all()
    
    print(f"\n1. 原始CF状态:")
    print(f"   节点数: {len(cf.nodes)}")
    print(f"   节点: {cf.nodes}")
    
    # 显示源和汇元素
    source_elts = cf.get_source_elts()
    sink_elts = cf.get_sink_elts()
    
    print(f"\n2. 源和汇元素:")
    print(f"   源元素:")
    for node, elts in source_elts.items():
        print(f"     {node}: {len(elts)} 个元素")
    
    print(f"   汇元素:")
    for node, elts in sink_elts.items():
        print(f"     {node}: {len(elts)} 个元素")
    
    print(f"\n3. 删除不可达元素:")
    
    # 删除不可达元素
    cf_reachable = cf.drop_unreachable(direction="forward", how="strong")
    print(f"   删除不可达元素后节点数: {len(cf_reachable.nodes)}")
    print(f"   删除后节点: {cf_reachable.nodes}")
    
    # 显示删除后的数据
    df_reachable = cf_reachable.df()
    print(f"   删除后数据框架 (shape: {df_reachable.shape}):")
    print(df_reachable)
    
    return storage, cf

def demo_cleanup_operations():
    """演示清理操作"""
    print("\n" + "="*60)
    print("ComputationFrame清理操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建计算图
    @op(output_names=['result'])
    def simple_op(x: int) -> int:
        return x + 1
    
    with storage:
        for i in range(3):
            simple_op(i)
    
    # 创建CF并添加空节点
    cf = storage.cf(simple_op)
    
    # 添加一些空变量
    empty_var1 = cf._add_var("empty_var1")
    empty_var2 = cf._add_var("empty_var2")
    
    print(f"\n1. 添加空节点后的状态:")
    print(f"   节点数: {len(cf.nodes)}")
    print(f"   节点: {cf.nodes}")
    
    # 显示每个变量的内容
    for vname in cf.vnames:
        print(f"   变量 {vname}: {len(cf.vs[vname])} 个元素")
    
    print(f"\n2. 清理空节点:")
    
    # 清理操作
    cf_cleaned = cf.cleanup()
    print(f"   清理后节点数: {len(cf_cleaned.nodes)}")
    print(f"   清理后节点: {cf_cleaned.nodes}")
    
    # 显示清理后的变量
    for vname in cf_cleaned.vnames:
        print(f"   变量 {vname}: {len(cf_cleaned.vs[vname])} 个元素")
    
    print(f"\n3. 就地清理:")
    
    # 就地清理
    cf_copy = cf.copy()
    cf_copy.cleanup(inplace=True)
    print(f"   就地清理后节点数: {len(cf_copy.nodes)}")
    print(f"   就地清理后节点: {cf_copy.nodes}")
    
    return storage, cf

def demo_set_operations():
    """演示集合操作（删除的另一种形式）"""
    print("\n" + "="*60)
    print("ComputationFrame集合操作")
    print("="*60)
    
    storage = Storage()
    
    # 创建两个计算图
    @op(output_names=['result1'])
    def operation_a(x: int) -> int:
        return x * 2
    
    @op(output_names=['result2'])
    def operation_b(x: int) -> int:
        return x + 3
    
    with storage:
        for i in range(5):
            operation_a(i)
        for i in range(2, 7):
            operation_b(i)
    
    # 创建两个CF
    cf1 = storage.cf(operation_a)
    cf2 = storage.cf(operation_b)
    
    print(f"\n1. 原始CF状态:")
    print(f"   CF1 节点数: {len(cf1.nodes)}")
    print(f"   CF2 节点数: {len(cf2.nodes)}")
    
    # 显示数据
    df1 = cf1.df()
    df2 = cf2.df()
    print(f"   CF1 数据 (shape: {df1.shape}):")
    print(df1)
    print(f"   CF2 数据 (shape: {df2.shape}):")
    print(df2)
    
    print(f"\n2. 集合操作:")
    
    # 并集
    cf_union = cf1 | cf2
    print(f"   并集节点数: {len(cf_union.nodes)}")
    
    # 交集
    cf_intersection = cf1 & cf2
    print(f"   交集节点数: {len(cf_intersection.nodes)}")
    
    # 差集（类似删除）
    cf_difference = cf1 - cf2
    print(f"   差集节点数: {len(cf_difference.nodes)}")
    
    # 显示差集数据
    df_difference = cf_difference.df()
    print(f"   差集数据 (shape: {df_difference.shape}):")
    print(df_difference)
    
    return storage, cf1, cf2

if __name__ == "__main__":
    print("开始ComputationFrame删除操作演示")
    
    # 运行各个演示
    storage1, cf1 = demo_drop_nodes()
    storage2, cf2 = demo_drop_variables()
    storage3, cf3 = demo_drop_functions()
    storage4, cf4 = demo_drop_refs()
    storage5, cf5 = demo_drop_calls()
    storage6, cf6 = demo_filtering_operations()
    storage7, cf7 = demo_drop_unreachable()
    storage8, cf8 = demo_cleanup_operations()
    storage9, cf9a, cf9b = demo_set_operations()
    
    print("\n" + "="*60)
    print("ComputationFrame删除操作总结")
    print("="*60)
    print("""
ComputationFrame提供了多种删除和清理功能:

1. 节点删除:
   - 删除单个节点 (drop_node)
   - 批量删除节点 (drop)
   - 删除变量节点 (drop_var)
   - 删除函数节点 (drop_func)

2. 元素删除:
   - 删除引用 (drop_ref)
   - 删除调用 (drop_call)
   - 支持就地删除 (inplace=True)

3. 过滤操作:
   - 值过滤 (isin)
   - 条件过滤 (比较运算符)
   - 方向性过滤 (downstream, upstream)

4. 清理操作:
   - 删除不可达元素 (drop_unreachable)
   - 清理空节点 (cleanup)
   - 简化图结构 (simplify)

5. 集合操作:
   - 差集删除 (- 运算符)
   - 交集保留 (& 运算符)
   - 联合操作 (| 运算符)

6. 边删除:
   - 内部边删除 (_drop_edge)
   - 删除时自动维护图的一致性

这些功能支持灵活的计算图裁剪和清理，
可以根据需要移除不必要的节点和数据。
    """) 
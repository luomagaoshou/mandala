#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mandala框架运行内容捕获原理分析
=====================================

本文件详细分析mandala框架是如何将运行的内容捕获出来的，
包括Storage和ComputationFrame的配合工作原理。
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from mandala1.imports import *
import pandas as pd
import numpy as np

def analyze_capture_mechanism():
    """分析mandala框架的捕获机制"""
    
    print("="*60)
    print("mandala框架运行内容捕获原理分析")
    print("="*60)
    
    # 1. 创建Storage实例
    storage = Storage()
    print("\n1. 创建Storage实例")
    print(f"   Storage配置: {storage.dump_config()}")
    
    # 2. 定义被@op装饰的函数
    @op(output_names=['result'])
    def add_numbers(a: int, b: int) -> int:
        """简单的加法函数"""
        print(f"   执行加法: {a} + {b}")
        return a + b
    
    @op(output_names=['result'])
    def multiply_numbers(a: int, b: int) -> int:
        """简单的乘法函数"""
        print(f"   执行乘法: {a} * {b}")
        return a * b
    
    @op(output_names=['result']) 
    def power_function(base: int, exponent: int) -> int:
        """幂函数"""
        print(f"   执行幂运算: {base} ^ {exponent}")
        return base ** exponent
    
    print("\n2. 定义@op装饰的函数")
    print(f"   add_numbers: {add_numbers}")
    print(f"   multiply_numbers: {multiply_numbers}")
    print(f"   power_function: {power_function}")
    
    # 3. 在Storage上下文中运行函数
    print("\n3. 在Storage上下文中运行函数 - 捕获过程开始")
    print("   Storage会自动记录每次函数调用的:")
    print("   - 输入参数 (inputs)")
    print("   - 输出结果 (outputs)")
    print("   - 函数签名 (operation)")
    print("   - 调用历史 (call history)")
    
    with storage:
        # 第一轮计算
        print("\n   第一轮计算:")
        for i in range(3):
            result1 = add_numbers(i, i+1)
            result2 = multiply_numbers(i, 2)
            result3 = power_function(i, 2)
            print(f"   计算 {i}: add={result1}, multiply={result2}, power={result3}")
        
        # 第二轮计算 (部分重复)
        print("\n   第二轮计算 (测试记忆化):")
        for i in range(2, 5):
            result1 = add_numbers(i, i+1)  # 部分重复调用
            result2 = multiply_numbers(i, 3)  # 新的调用
            print(f"   计算 {i}: add={result1}, multiply={result2}")
    
    # 4. 分析Storage中捕获的内容
    print("\n4. 分析Storage中捕获的内容")
    print(f"   缓存信息:")
    storage.cache_info()
    
    # 查看atoms（原子对象）
    print(f"\n   原子对象数量: {len(storage.atoms.cache)}")
    
    # 查看calls（调用历史）
    print(f"   调用历史数量: {len(storage.calls.cache)}")
    
    # 查看ops（操作定义）
    print(f"   操作定义数量: {len(storage.ops.cache)}")
    print(f"   操作定义: {list(storage.ops.cache.keys())}")
    
    # 5. 创建ComputationFrame分析捕获的内容
    print("\n5. 创建ComputationFrame分析捕获的内容")
    
    # 从不同角度创建CF
    cf_add = storage.cf(add_numbers)
    cf_multiply = storage.cf(multiply_numbers)
    cf_power = storage.cf(power_function)
    
    print(f"\n   add_numbers的计算框架:")
    print(f"   {cf_add}")
    
    print(f"\n   multiply_numbers的计算框架:")
    print(f"   {cf_multiply}")
    
    print(f"\n   power_function的计算框架:")
    print(f"   {cf_power}")
    
    # 6. 分析数据血缘关系
    print("\n6. 分析数据血缘关系")
    
    # 扩展计算框架获取完整的计算图
    cf_add_expanded = cf_add.expand_all()
    print(f"\n   扩展后的add_numbers计算图:")
    print(f"   {cf_add_expanded}")
    
    # 获取数据框架
    df_add = cf_add.df()
    print(f"\n   add_numbers的数据框架 (shape: {df_add.shape}):")
    print(df_add)
    
    df_multiply = cf_multiply.df()
    print(f"\n   multiply_numbers的数据框架 (shape: {df_multiply.shape}):")
    print(df_multiply)
    
    # 7. 展示记忆化效果
    print("\n7. 展示记忆化效果")
    
    # 统计每个操作的调用次数
    print("\n   各操作的调用统计:")
    for op_name in storage.ops.cache.keys():
        cf_op = storage.cf(storage.ops.cache[op_name])
        op_calls = len(cf_op.fs.get(op_name, set()))
        print(f"   {op_name}: {op_calls} 次调用")
    
    # 8. 内部机制分析
    print("\n8. 内部机制分析")
    
    # 展示Call对象的结构
    if storage.calls.cache:
        first_call_hid = next(iter(storage.calls.cache.keys()))
        first_call = storage.calls.cache[first_call_hid]
        print(f"\n   Call对象示例 (hid: {first_call_hid}):")
        print(f"   - 操作名称: {first_call.op.name}")
        print(f"   - 输入参数: {list(first_call.inputs.keys())}")
        print(f"   - 输出结果: {list(first_call.outputs.keys())}")
        print(f"   - 内容ID: {first_call.cid}")
        print(f"   - 历史ID: {first_call.hid}")
    
    # 展示Ref对象的结构
    if storage.shapes.cache:
        first_ref_hid = next(iter(storage.shapes.cache.keys()))
        first_ref = storage.shapes.cache[first_ref_hid]
        print(f"\n   Ref对象示例 (hid: {first_ref_hid}):")
        print(f"   - 内容ID: {first_ref.cid}")
        print(f"   - 历史ID: {first_ref.hid}")
        print(f"   - 类型: {type(first_ref)}")
        print(f"   - 在内存: {first_ref.in_memory}")
    
    return storage

def analyze_computation_frame_creation():
    """分析ComputationFrame的创建过程"""
    
    print("\n" + "="*60)
    print("ComputationFrame创建过程分析")
    print("="*60)
    
    storage = Storage()
    
    @op(output_names=['doubled'])
    def double_value(x: int) -> int:
        return x * 2
    
    @op(output_names=['sum'])
    def add_values(a: int, b: int) -> int:
        return a + b
    
    @op(output_names=['result'])
    def complex_calculation(x: int) -> int:
        doubled = double_value(x)
        result = add_values(doubled, x)
        return result
    
    print("\n1. 创建计算链")
    with storage:
        for i in range(3):
            result = complex_calculation(i)
            print(f"   complex_calculation({i}) = {result}")
    
    print("\n2. 从不同角度创建ComputationFrame")
    
    # 从单个函数创建
    cf_double = storage.cf(double_value)
    cf_add = storage.cf(add_values)
    cf_complex = storage.cf(complex_calculation)
    
    print(f"\n   从double_value创建的CF:")
    print(f"   变量数量: {len(cf_double.vnames)}")
    print(f"   函数数量: {len(cf_double.fnames)}")
    print(f"   变量名称: {cf_double.vnames}")
    print(f"   函数名称: {cf_double.fnames}")
    
    print(f"\n   从complex_calculation创建的CF:")
    print(f"   变量数量: {len(cf_complex.vnames)}")
    print(f"   函数数量: {len(cf_complex.fnames)}")
    
    # 3. 扩展CF获取完整的计算图
    print("\n3. 扩展CF获取完整的计算图")
    cf_complex_expanded = cf_complex.expand_all()
    print(f"\n   扩展后的complex_calculation CF:")
    print(f"   变量数量: {len(cf_complex_expanded.vnames)}")
    print(f"   函数数量: {len(cf_complex_expanded.fnames)}")
    print(f"   变量名称: {cf_complex_expanded.vnames}")
    print(f"   函数名称: {cf_complex_expanded.fnames}")
    
    # 4. 分析计算图结构
    print("\n4. 分析计算图结构")
    print(f"\n   计算图描述:")
    cf_complex_expanded.print_graph()
    
    # 5. 获取数据框架
    print("\n5. 获取数据框架")
    df = cf_complex_expanded.df()
    print(f"\n   完整数据框架 (shape: {df.shape}):")
    print(df)
    
    return storage, cf_complex_expanded

def analyze_data_lineage():
    """分析数据血缘关系"""
    
    print("\n" + "="*60)
    print("数据血缘关系分析")
    print("="*60)
    
    storage = Storage()
    
    @op(output_names=['processed'])
    def process_data(data: int) -> int:
        """数据处理函数"""
        return data * 2 + 1
    
    @op(output_names=['filtered'])
    def filter_data(data: int) -> int:
        """数据过滤函数"""
        return data if data > 5 else 0
    
    @op(output_names=['aggregated'])
    def aggregate_data(data1: int, data2: int) -> int:
        """数据聚合函数"""
        return data1 + data2
    
    @op(output_names=['final'])
    def final_transform(data: int) -> int:
        """最终转换函数"""
        return data ** 2
    
    print("\n1. 创建复杂的数据流")
    with storage:
        for i in range(5):
            # 创建分支数据流
            processed = process_data(i)
            filtered = filter_data(processed)
            
            # 创建聚合
            if i > 0:
                prev_processed = process_data(i-1)
                aggregated = aggregate_data(filtered, prev_processed)
                final = final_transform(aggregated)
                print(f"   流程 {i}: 原始={i} -> 处理={processed} -> 过滤={filtered} -> 聚合={aggregated} -> 最终={final}")
            else:
                final = final_transform(filtered)
                print(f"   流程 {i}: 原始={i} -> 处理={processed} -> 过滤={filtered} -> 最终={final}")
    
    print("\n2. 分析数据血缘关系")
    
    # 从最终结果往回追踪
    cf_final = storage.cf(final_transform).expand_all()
    print(f"\n   final_transform的完整血缘:")
    print(f"   {cf_final}")
    
    # 获取血缘数据
    df_lineage = cf_final.df()
    print(f"\n   血缘数据框架 (shape: {df_lineage.shape}):")
    print(df_lineage)
    
    # 3. 分析特定变量的历史
    print("\n3. 分析特定变量的历史")
    
    # 获取某个变量的完整历史
    if 'var_0' in cf_final.vnames:
        var_history = cf_final.get_history_df('var_0')
        print(f"\n   变量 var_0 的历史:")
        print(var_history)
    
    # 4. 创建和分析子图
    print("\n4. 创建和分析子图")
    
    # 选择特定节点的子图
    if len(cf_final.vnames) > 1:
        selected_vars = list(cf_final.vnames)[:2]
        sub_cf = cf_final.select_nodes(selected_vars)
        print(f"\n   选择节点 {selected_vars} 的子图:")
        print(f"   {sub_cf}")
    
    return storage, cf_final

if __name__ == "__main__":
    # 运行分析
    storage1 = analyze_capture_mechanism()
    storage2, cf_expanded = analyze_computation_frame_creation()
    storage3, cf_lineage = analyze_data_lineage()
    
    print("\n" + "="*60)
    print("总结: mandala框架捕获机制")
    print("="*60)
    print("""
1. 函数装饰: @op装饰器将普通函数转换为可追踪的操作
2. 上下文管理: with storage 上下文自动记录所有函数调用
3. 自动记忆化: 相同输入的函数调用会被缓存，避免重复计算
4. 对象存储: 所有输入输出都被包装为Ref对象并存储
5. 调用历史: 每次函数调用都被记录为Call对象
6. 计算图构建: ComputationFrame从存储中重建计算图
7. 血缘追踪: 可以追踪数据的来源和去向
8. 图操作: 支持对计算图进行各种查询和操作

这种设计实现了:
- 透明的计算历史记录
- 自动的依赖跟踪
- 高效的重复计算避免
- 灵活的数据查询和分析
    """) 
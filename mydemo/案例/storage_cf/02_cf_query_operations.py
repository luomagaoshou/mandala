#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ComputationFrame查询操作详解
===========================

本文件详细展示ComputationFrame的各种查询操作，
包括数据提取、过滤、选择、遍历等功能。
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from mandala1.imports import *
import pandas as pd
import numpy as np

def setup_demo_data():
    """设置演示数据"""
    storage = Storage()
    
    @op(output_names=['processed'])
    def process_input(data: int) -> int:
        """处理输入数据"""
        return data * 2 + 1
    
    @op(output_names=['filtered'])
    def filter_positive(data: int) -> int:
        """过滤正数"""
        return data if data > 0 else 0
    
    @op(output_names=['squared'])
    def square_value(data: int) -> int:
        """平方运算"""
        return data ** 2
    
    @op(output_names=['combined'])
    def combine_values(a: int, b: int) -> int:
        """合并两个值"""
        return a + b
    
    @op(output_names=['result'])
    def final_computation(data: int) -> int:
        """最终计算"""
        return data * 3
    
    # 创建复杂的计算图
    with storage:
        for i in range(-2, 5):
            processed = process_input(i)
            filtered = filter_positive(processed)
            squared = square_value(filtered)
            
            if i > 0:
                prev_processed = process_input(i-1)
                combined = combine_values(squared, prev_processed)
                result = final_computation(combined)
            else:
                result = final_computation(squared)
            
            print(f"计算 {i}: {i} -> {processed} -> {filtered} -> {squared} -> {result}")
    
    return storage, {
        'process_input': process_input,
        'filter_positive': filter_positive,
        'square_value': square_value,
        'combine_values': combine_values,
        'final_computation': final_computation
    }

def demo_basic_queries():
    """演示基本查询操作"""
    print("="*60)
    print("ComputationFrame基本查询操作")
    print("="*60)
    
    storage, ops = setup_demo_data()
    
    print("\n1. 从不同函数创建ComputationFrame")
    
    # 从单个函数创建CF
    cf_process = storage.cf(ops['process_input'])
    cf_filter = storage.cf(ops['filter_positive'])
    cf_final = storage.cf(ops['final_computation'])
    
    print(f"\n   process_input CF:")
    print(f"   变量节点: {cf_process.vnames}")
    print(f"   函数节点: {cf_process.fnames}")
    print(f"   边数量: {len(cf_process.edges())}")
    
    print(f"\n   filter_positive CF:")
    print(f"   变量节点: {cf_filter.vnames}")
    print(f"   函数节点: {cf_filter.fnames}")
    
    print(f"\n   final_computation CF:")
    print(f"   变量节点: {cf_final.vnames}")
    print(f"   函数节点: {cf_final.fnames}")
    
    print("\n2. 扩展ComputationFrame获取完整图")
    cf_final_expanded = cf_final.expand_all()
    print(f"\n   扩展后的final_computation CF:")
    print(f"   变量节点: {cf_final_expanded.vnames}")
    print(f"   函数节点: {cf_final_expanded.fnames}")
    print(f"   边数量: {len(cf_final_expanded.edges())}")
    
    print("\n3. 图结构信息")
    print(f"\n   所有节点: {cf_final_expanded.nodes}")
    print(f"   源节点: {cf_final_expanded.sources}")
    print(f"   汇点节点: {cf_final_expanded.sinks}")
    
    print("\n4. 获取拓扑排序")
    topo_order = cf_final_expanded.topsort_modulo_sccs()
    print(f"\n   拓扑排序: {topo_order}")
    
    print("\n5. 图描述")
    cf_final_expanded.print_graph()
    
    return storage, cf_final_expanded

def demo_data_extraction():
    """演示数据提取操作"""
    print("\n" + "="*60)
    print("数据提取操作")
    print("="*60)
    
    storage, ops = setup_demo_data()
    cf = storage.cf(ops['final_computation']).expand_all()
    
    print("\n1. 基本数据提取")
    
    # 获取所有数据
    df_all = cf.df()
    print(f"\n   完整数据框架 (shape: {df_all.shape}):")
    print(df_all)
    
    # 获取特定列
    if len(cf.vnames) > 1:
        selected_vars = list(cf.vnames)[:3]
        df_selected = cf.df(*selected_vars)
        print(f"\n   选择变量 {selected_vars} 的数据:")
        print(df_selected)
    
    print("\n2. 不同值类型的提取")
    
    # 获取引用对象
    df_refs = cf.df(values="refs")
    print(f"\n   引用对象数据框架 (shape: {df_refs.shape}):")
    print(df_refs.head())
    
    # 获取实际值
    df_objs = cf.df(values="objs")
    print(f"\n   实际值数据框架 (shape: {df_objs.shape}):")
    print(df_objs.head())
    
    print("\n3. 包含/排除调用")
    
    # 不包含调用
    df_no_calls = cf.df(include_calls=False)
    print(f"\n   不包含调用的数据框架 (shape: {df_no_calls.shape}):")
    print(df_no_calls.head())
    
    # 包含调用
    df_with_calls = cf.df(include_calls=True)
    print(f"\n   包含调用的数据框架 (shape: {df_with_calls.shape}):")
    print(df_with_calls.head())
    
    print("\n4. 不同连接方式")
    
    # 内连接
    df_inner = cf.df(join_how="inner")
    print(f"\n   内连接数据框架 (shape: {df_inner.shape}):")
    print(df_inner.head())
    
    # 外连接
    df_outer = cf.df(join_how="outer")
    print(f"\n   外连接数据框架 (shape: {df_outer.shape}):")
    print(df_outer.head())
    
    return storage, cf

def demo_graph_traversal():
    """演示图遍历操作"""
    print("\n" + "="*60)
    print("图遍历操作")
    print("="*60)
    
    storage, ops = setup_demo_data()
    cf = storage.cf(ops['final_computation']).expand_all()
    
    print("\n1. 邻居查询")
    
    # 遍历所有节点的邻居
    for node in sorted(cf.nodes):
        in_neighbors = cf.in_neighbors(node)
        out_neighbors = cf.out_neighbors(node)
        print(f"\n   节点 {node}:")
        print(f"   输入邻居: {in_neighbors}")
        print(f"   输出邻居: {out_neighbors}")
    
    print("\n2. 边查询")
    
    # 查看所有边
    all_edges = cf.edges()
    print(f"\n   所有边 (共 {len(all_edges)} 条):")
    for src, dst, label in all_edges:
        print(f"   {src} --{label}--> {dst}")
    
    # 查看特定节点的边
    if cf.nodes:
        sample_node = list(cf.nodes)[0]
        in_edges = cf.in_edges(sample_node)
        out_edges = cf.out_edges(sample_node)
        print(f"\n   节点 {sample_node} 的边:")
        print(f"   输入边: {in_edges}")
        print(f"   输出边: {out_edges}")
    
    print("\n3. 可达性分析")
    
    # 获取源和汇元素
    source_elts = cf.get_source_elts()
    sink_elts = cf.get_sink_elts()
    
    print(f"\n   源元素:")
    for node, elts in source_elts.items():
        print(f"   {node}: {len(elts)} 个元素")
    
    print(f"\n   汇元素:")
    for node, elts in sink_elts.items():
        print(f"   {node}: {len(elts)} 个元素")
    
    # 分析可达性
    if source_elts:
        sample_sources = {k: v for k, v in list(source_elts.items())[:1]}
        reachable = cf.get_reachable_elts(
            initial_state=sample_sources,
            direction="forward",
            how="strong"
        )
        print(f"\n   从源元素可达的元素:")
        for node, elts in reachable.items():
            print(f"   {node}: {len(elts)} 个元素")
    
    return storage, cf

def demo_filtering_operations():
    """演示过滤操作"""
    print("\n" + "="*60)
    print("过滤操作")
    print("="*60)
    
    storage, ops = setup_demo_data()
    cf = storage.cf(ops['final_computation']).expand_all()
    
    print("\n1. 节点选择")
    
    # 选择特定节点
    if len(cf.vnames) > 2:
        selected_nodes = list(cf.vnames)[:2]
        cf_selected = cf.select_nodes(selected_nodes)
        print(f"\n   选择节点 {selected_nodes}:")
        print(f"   原始变量数: {len(cf.vnames)}")
        print(f"   选择后变量数: {len(cf_selected.vnames)}")
        print(f"   选择后的节点: {cf_selected.nodes}")
    
    print("\n2. 方向性选择")
    
    # 下游选择
    if cf.sources:
        sample_source = list(cf.sources)[0]
        cf_downstream = cf.downstream(sample_source)
        print(f"\n   从源节点 {sample_source} 的下游:")
        print(f"   下游节点: {cf_downstream.nodes}")
        print(f"   下游数据形状: {cf_downstream.df().shape}")
    
    # 上游选择
    if cf.sinks:
        sample_sink = list(cf.sinks)[0]
        cf_upstream = cf.upstream(sample_sink)
        print(f"\n   到汇节点 {sample_sink} 的上游:")
        print(f"   上游节点: {cf_upstream.nodes}")
        print(f"   上游数据形状: {cf_upstream.df().shape}")
    
    print("\n3. 值过滤")
    
    # 根据值过滤
    df_sample = cf.df()
    if len(df_sample) > 0:
        # 查找包含特定值的元素
        sample_values = [0, 1, 2, 3]
        cf_filtered = cf.isin(sample_values, by="val")
        print(f"\n   包含值 {sample_values} 的元素:")
        print(f"   过滤后节点: {cf_filtered.nodes}")
        print(f"   过滤后数据形状: {cf_filtered.df().shape}")
    
    print("\n4. 条件过滤")
    
    # 数值比较过滤
    try:
        cf_comparison = cf < 10
        print(f"\n   值小于10的元素:")
        print(f"   过滤后节点: {cf_comparison.nodes}")
        print(f"   过滤后数据形状: {cf_comparison.df().shape}")
    except Exception as e:
        print(f"\n   比较过滤失败: {e}")
    
    return storage, cf

def demo_history_queries():
    """演示历史查询"""
    print("\n" + "="*60)
    print("历史查询操作")
    print("="*60)
    
    storage, ops = setup_demo_data()
    cf = storage.cf(ops['final_computation']).expand_all()
    
    print("\n1. 变量历史查询")
    
    # 查看每个变量的历史
    for vname in sorted(cf.vnames):
        try:
            history_df = cf.get_history_df(vname)
            print(f"\n   变量 {vname} 的历史 (shape: {history_df.shape}):")
            print(history_df.head())
        except Exception as e:
            print(f"   变量 {vname} 历史查询失败: {e}")
    
    print("\n2. 联合历史查询")
    
    # 多变量联合历史
    if len(cf.vnames) > 1:
        selected_vars = list(cf.vnames)[:2]
        try:
            joint_history = cf.get_joint_history_df(selected_vars)
            print(f"\n   变量 {selected_vars} 的联合历史 (shape: {joint_history.shape}):")
            print(joint_history.head())
        except Exception as e:
            print(f"   联合历史查询失败: {e}")
    
    print("\n3. 函数调用表")
    
    # 查看函数调用表
    for fname in sorted(cf.fnames):
        try:
            func_table = cf.get_func_table(fname)
            print(f"\n   函数 {fname} 的调用表 (shape: {func_table.shape}):")
            print(func_table.head())
        except Exception as e:
            print(f"   函数 {fname} 调用表查询失败: {e}")
    
    return storage, cf

def demo_statistics_queries():
    """演示统计查询"""
    print("\n" + "="*60)
    print("统计查询操作")
    print("="*60)
    
    storage, ops = setup_demo_data()
    cf = storage.cf(ops['final_computation']).expand_all()
    
    print("\n1. 基本统计")
    
    # 变量统计
    var_stats = cf.get_var_stats()
    print(f"\n   变量统计:")
    print(var_stats)
    
    # 函数统计
    func_stats = cf.get_func_stats()
    print(f"\n   函数统计:")
    print(func_stats)
    
    print("\n2. 操作统计")
    
    # 操作信息
    ops_info = cf.ops()
    print(f"\n   操作信息:")
    for fname, op in ops_info.items():
        print(f"   {fname}: {op.name}")
    
    print("\n3. 引用和调用统计")
    
    # 引用统计
    refs_by_var = cf.refs_by_var()
    print(f"\n   各变量的引用数量:")
    for vname, refs in refs_by_var.items():
        print(f"   {vname}: {len(refs)} 个引用")
    
    # 调用统计
    calls_by_func = cf.calls_by_func()
    print(f"\n   各函数的调用数量:")
    for fname, calls in calls_by_func.items():
        print(f"   {fname}: {len(calls)} 个调用")
    
    print("\n4. 图统计")
    
    # 节点和边统计
    print(f"\n   图结构统计:")
    print(f"   变量节点数: {len(cf.vnames)}")
    print(f"   函数节点数: {len(cf.fnames)}")
    print(f"   总节点数: {len(cf.nodes)}")
    print(f"   边数: {len(cf.edges())}")
    print(f"   源节点数: {len(cf.sources)}")
    print(f"   汇节点数: {len(cf.sinks)}")
    
    return storage, cf

def demo_advanced_queries():
    """演示高级查询"""
    print("\n" + "="*60)
    print("高级查询操作")
    print("="*60)
    
    storage, ops = setup_demo_data()
    cf = storage.cf(ops['final_computation']).expand_all()
    
    print("\n1. 子图查询")
    
    # 中游子图
    if len(cf.nodes) > 2:
        node_list = list(cf.nodes)
        start_node = node_list[0]
        end_node = node_list[-1]
        try:
            cf_midstream = cf.midstream(start_node, end_node)
            print(f"\n   {start_node} 到 {end_node} 的中游子图:")
            print(f"   节点数: {len(cf_midstream.nodes)}")
            print(f"   数据形状: {cf_midstream.df().shape}")
        except Exception as e:
            print(f"   中游子图查询失败: {e}")
    
    print("\n2. 元素级查询")
    
    # 获取变量值
    for vname in list(cf.vnames)[:2]:
        try:
            var_values = cf.get_var_values(vname)
            print(f"\n   变量 {vname} 的值:")
            for i, ref in enumerate(var_values):
                if i < 3:  # 只显示前3个
                    print(f"   {ref.hid}: {storage.unwrap(ref)}")
                elif i == 3:
                    print(f"   ... 共 {len(var_values)} 个值")
                    break
        except Exception as e:
            print(f"   变量 {vname} 值查询失败: {e}")
    
    print("\n3. 路径查询")
    
    # 节点间路径
    if len(cf.nodes) > 1:
        node_list = list(cf.nodes)
        start_node = node_list[0]
        end_node = node_list[-1]
        try:
            path_edges = cf.get_all_edges_on_paths_between(start_node, end_node)
            print(f"\n   {start_node} 到 {end_node} 的路径边:")
            for edge in list(path_edges)[:5]:  # 只显示前5条
                print(f"   {edge}")
        except Exception as e:
            print(f"   路径查询失败: {e}")
    
    print("\n4. 复杂查询组合")
    
    # 组合查询示例
    try:
        # 获取特定条件的数据
        df_full = cf.df()
        if len(df_full) > 0:
            # 分析数据分布
            print(f"\n   数据分析:")
            print(f"   数据行数: {len(df_full)}")
            print(f"   数据列数: {len(df_full.columns)}")
            
            # 显示数据类型
            print(f"\n   数据类型:")
            for col in df_full.columns:
                col_type = type(df_full[col].iloc[0]) if len(df_full) > 0 else "unknown"
                print(f"   {col}: {col_type}")
    except Exception as e:
        print(f"   复杂查询失败: {e}")
    
    return storage, cf

if __name__ == "__main__":
    print("开始ComputationFrame查询操作演示")
    
    # 运行各个演示
    storage1, cf1 = demo_basic_queries()
    storage2, cf2 = demo_data_extraction()
    storage3, cf3 = demo_graph_traversal()
    storage4, cf4 = demo_filtering_operations()
    storage5, cf5 = demo_history_queries()
    storage6, cf6 = demo_statistics_queries()
    storage7, cf7 = demo_advanced_queries()
    
    print("\n" + "="*60)
    print("ComputationFrame查询操作总结")
    print("="*60)
    print("""
ComputationFrame提供了丰富的查询功能:

1. 基本查询:
   - 节点信息查询 (vnames, fnames, nodes)
   - 图结构查询 (edges, sources, sinks)
   - 拓扑排序 (topsort_modulo_sccs)

2. 数据提取:
   - 数据框架提取 (df, eval)
   - 引用/值选择 (values="refs"/"objs")
   - 列选择和连接方式控制

3. 图遍历:
   - 邻居查询 (in_neighbors, out_neighbors)
   - 边查询 (edges, in_edges, out_edges)
   - 可达性分析 (get_reachable_elts)

4. 过滤操作:
   - 节点选择 (select_nodes)
   - 方向性选择 (downstream, upstream, midstream)
   - 值过滤 (isin, 比较操作)

5. 历史查询:
   - 变量历史 (get_history_df)
   - 联合历史 (get_joint_history_df)
   - 函数调用表 (get_func_table)

6. 统计查询:
   - 基本统计 (get_var_stats, get_func_stats)
   - 引用和调用统计
   - 图结构统计

7. 高级查询:
   - 子图查询 (midstream, select_subsets)
   - 元素级查询 (get_var_values)
   - 路径查询 (get_all_edges_on_paths_between)

这些功能支持灵活的计算图分析和数据探索。
    """) 
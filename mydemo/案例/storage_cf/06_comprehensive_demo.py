#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mandala框架综合演示
===================

本文件展示mandala框架的综合使用，包括Storage和ComputationFrame的
完整工作流程，以及增删查改操作的组合使用。
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from mandala1.imports import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def comprehensive_data_pipeline():
    """综合数据处理流水线演示"""
    print("="*80)
    print("mandala框架综合数据处理流水线演示")
    print("="*80)
    
    # 创建存储
    storage = Storage()
    
    # 第一阶段：数据生成和预处理
    print("\n第一阶段：数据生成和预处理")
    print("-" * 40)
    
    @op(output_names=['raw_data'])
    def generate_raw_data(seed: int) -> int:
        """生成原始数据"""
        np.random.seed(seed)
        return int(np.random.randint(1, 100))
    
    @op(output_names=['cleaned_data'])
    def clean_data(raw_data: int) -> int:
        """清理数据"""
        return max(0, raw_data)  # 确保非负
    
    @op(output_names=['normalized_data'])
    def normalize_data(cleaned_data: int) -> float:
        """归一化数据"""
        return cleaned_data / 100.0
    
    # 第二阶段：特征工程
    print("\n第二阶段：特征工程")
    print("-" * 40)
    
    @op(output_names=['feature1'])
    def create_feature1(normalized_data: float) -> float:
        """创建特征1：平方特征"""
        return normalized_data ** 2
    
    @op(output_names=['feature2'])
    def create_feature2(normalized_data: float) -> float:
        """创建特征2：对数特征"""
        return np.log(normalized_data + 1e-8)
    
    @op(output_names=['combined_features'])
    def combine_features(feature1: float, feature2: float) -> float:
        """组合特征"""
        return feature1 + feature2
    
    # 第三阶段：模型处理
    print("\n第三阶段：模型处理")
    print("-" * 40)
    
    @op(output_names=['model_input'])
    def prepare_model_input(combined_features: float) -> float:
        """准备模型输入"""
        return combined_features * 10
    
    @op(output_names=['prediction'])
    def simple_model(model_input: float) -> float:
        """简单模型预测"""
        return 1.0 / (1.0 + np.exp(-model_input))  # sigmoid
    
    @op(output_names=['final_result'])
    def post_process(prediction: float) -> str:
        """后处理"""
        return "high" if prediction > 0.5 else "low"
    
    # 执行数据处理流水线
    print("\n执行数据处理流水线:")
    print("-" * 40)
    
    results = []
    with storage:
        for i in range(10):
            # 执行完整的数据处理流水线
            raw = generate_raw_data(i)
            cleaned = clean_data(raw)
            normalized = normalize_data(cleaned)
            
            feat1 = create_feature1(normalized)
            feat2 = create_feature2(normalized)
            combined = combine_features(feat1, feat2)
            
            model_input = prepare_model_input(combined)
            pred = simple_model(model_input)
            result = post_process(pred)
            
            results.append({
                'seed': i,
                'raw': storage.unwrap(raw),
                'prediction': storage.unwrap(pred),
                'result': storage.unwrap(result)
            })
            
            print(f"  样本 {i}: 原始={storage.unwrap(raw)}, 预测={storage.unwrap(pred):.4f}, 结果={storage.unwrap(result)}")
    
    return storage, results

def computation_graph_analysis():
    """计算图分析演示"""
    print("\n" + "="*80)
    print("计算图分析演示")
    print("="*80)
    
    storage, results = comprehensive_data_pipeline()
    
    print("\n1. 从不同角度创建ComputationFrame:")
    print("-" * 40)
    
    # 获取操作对象
    ops = list(storage.ops.cache.values())
    
    # 从不同操作创建CF
    cf_raw = storage.cf(ops[0])  # generate_raw_data
    cf_final = storage.cf(ops[-1])  # post_process
    
    print(f"原始数据生成CF: {len(cf_raw.nodes)} 个节点")
    print(f"最终结果CF: {len(cf_final.nodes)} 个节点")
    
    # 扩展到完整图
    cf_full = cf_final.expand_all()
    print(f"完整扩展CF: {len(cf_full.nodes)} 个节点")
    
    print("\n2. 查询操作演示:")
    print("-" * 40)
    
    # 基本查询
    print(f"变量节点: {cf_full.vnames}")
    print(f"函数节点: {cf_full.fnames}")
    print(f"源节点: {cf_full.sources}")
    print(f"汇点节点: {cf_full.sinks}")
    
    # 图结构查询
    print(f"\n图结构:")
    cf_full.print_graph()
    
    # 统计信息
    print(f"\n统计信息:")
    var_stats = cf_full.get_var_stats()
    func_stats = cf_full.get_func_stats()
    print(f"变量统计:\n{var_stats}")
    print(f"函数统计:\n{func_stats}")
    
    print("\n3. 数据提取演示:")
    print("-" * 40)
    
    # 提取完整数据
    df_full = cf_full.df()
    print(f"完整数据框架 (shape: {df_full.shape}):")
    print(df_full.head())
    
    # 提取特定变量
    if len(cf_full.vnames) > 3:
        selected_vars = list(cf_full.vnames)[:3]
        df_selected = cf_full.df(*selected_vars)
        print(f"\n选择变量 {selected_vars} 的数据 (shape: {df_selected.shape}):")
        print(df_selected)
    
    return storage, cf_full

def graph_modification_demo():
    """图修改操作演示"""
    print("\n" + "="*80)
    print("图修改操作演示")
    print("="*80)
    
    storage, cf_full = computation_graph_analysis()
    
    print("\n1. 重命名操作:")
    print("-" * 40)
    
    # 重命名变量
    cf_renamed = cf_full.copy()
    if cf_renamed.vnames:
        old_names = list(cf_renamed.vnames)[:3]
        new_names = ['input_data', 'processed_data', 'output_data']
        
        for old_name, new_name in zip(old_names, new_names):
            cf_renamed = cf_renamed.rename_var(old_name, new_name)
        
        print(f"重命名前: {old_names}")
        print(f"重命名后: {list(cf_renamed.vnames)[:3]}")
    
    print("\n2. 删除操作:")
    print("-" * 40)
    
    # 删除部分节点
    cf_filtered = cf_full.copy()
    if len(cf_filtered.nodes) > 5:
        nodes_to_remove = list(cf_filtered.nodes)[::2]  # 每隔一个删除
        cf_filtered = cf_filtered.drop(nodes_to_remove)
        
        print(f"删除前节点数: {len(cf_full.nodes)}")
        print(f"删除后节点数: {len(cf_filtered.nodes)}")
    
    print("\n3. 过滤操作:")
    print("-" * 40)
    
    # 值过滤
    try:
        df_sample = cf_full.df()
        if len(df_sample) > 0:
            # 获取某列的值范围
            first_col = df_sample.columns[0]
            sample_values = df_sample[first_col].tolist()[:3]
            
            cf_value_filtered = cf_full.isin(sample_values, by="val")
            print(f"值过滤前数据量: {len(cf_full.df())}")
            print(f"值过滤后数据量: {len(cf_value_filtered.df())}")
    except Exception as e:
        print(f"值过滤演示失败: {e}")
    
    print("\n4. 方向性选择:")
    print("-" * 40)
    
    # 下游和上游选择
    if cf_full.sources and cf_full.sinks:
        source_node = list(cf_full.sources)[0]
        sink_node = list(cf_full.sinks)[0]
        
        cf_downstream = cf_full.downstream(source_node)
        cf_upstream = cf_full.upstream(sink_node)
        
        print(f"从源节点 {source_node} 的下游: {len(cf_downstream.nodes)} 个节点")
        print(f"到汇节点 {sink_node} 的上游: {len(cf_upstream.nodes)} 个节点")
    
    return storage, cf_full

def data_lineage_analysis():
    """数据血缘分析演示"""
    print("\n" + "="*80)
    print("数据血缘分析演示")
    print("="*80)
    
    storage, cf_full = graph_modification_demo()
    
    print("\n1. 血缘追踪:")
    print("-" * 40)
    
    # 追踪特定变量的血缘
    if cf_full.vnames:
        target_var = list(cf_full.vnames)[-1]  # 选择最后一个变量
        print(f"追踪变量 {target_var} 的血缘:")
        
        try:
            history_df = cf_full.get_history_df(target_var)
            print(f"血缘历史 (shape: {history_df.shape}):")
            print(history_df.head())
        except Exception as e:
            print(f"血缘追踪失败: {e}")
    
    print("\n2. 多变量联合血缘:")
    print("-" * 40)
    
    # 多变量联合血缘分析
    if len(cf_full.vnames) > 1:
        vars_to_analyze = list(cf_full.vnames)[:2]
        try:
            joint_history = cf_full.get_joint_history_df(vars_to_analyze)
            print(f"联合血缘 {vars_to_analyze} (shape: {joint_history.shape}):")
            print(joint_history.head())
        except Exception as e:
            print(f"联合血缘分析失败: {e}")
    
    print("\n3. 函数调用分析:")
    print("-" * 40)
    
    # 分析函数调用
    for fname in list(cf_full.fnames)[:3]:  # 只分析前3个函数
        try:
            func_table = cf_full.get_func_table(fname)
            print(f"函数 {fname} 的调用表 (shape: {func_table.shape}):")
            print(func_table.head())
        except Exception as e:
            print(f"函数 {fname} 分析失败: {e}")
    
    return storage, cf_full

def advanced_operations_demo():
    """高级操作演示"""
    print("\n" + "="*80)
    print("高级操作演示")
    print("="*80)
    
    storage, cf_full = data_lineage_analysis()
    
    print("\n1. 图集合操作:")
    print("-" * 40)
    
    # 创建多个CF进行集合操作
    if len(cf_full.fnames) > 2:
        ops = list(storage.ops.cache.values())
        cf1 = storage.cf(ops[0])
        cf2 = storage.cf(ops[1])
        cf3 = storage.cf(ops[2])
        
        # 并集
        cf_union = cf1 | cf2
        print(f"CF1 ∪ CF2: {len(cf_union.nodes)} 个节点")
        
        # 交集
        cf_intersection = cf1 & cf2
        print(f"CF1 ∩ CF2: {len(cf_intersection.nodes)} 个节点")
        
        # 差集
        cf_difference = cf1 - cf2
        print(f"CF1 - CF2: {len(cf_difference.nodes)} 个节点")
        
        # 多元并集
        cf_multi_union = ComputationFrame.union(cf1, cf2, cf3)
        print(f"CF1 ∪ CF2 ∪ CF3: {len(cf_multi_union.nodes)} 个节点")
    
    print("\n2. 复杂查询:")
    print("-" * 40)
    
    # 复杂查询组合
    if len(cf_full.nodes) > 3:
        # 中游分析
        nodes_list = list(cf_full.nodes)
        start_node = nodes_list[0]
        end_node = nodes_list[-1]
        
        try:
            cf_midstream = cf_full.midstream(start_node, end_node)
            print(f"{start_node} 到 {end_node} 的中游: {len(cf_midstream.nodes)} 个节点")
        except Exception as e:
            print(f"中游分析失败: {e}")
    
    print("\n3. 性能优化:")
    print("-" * 40)
    
    # 清理和优化
    cf_optimized = cf_full.copy()
    
    # 清理空节点
    cf_optimized = cf_optimized.cleanup()
    print(f"清理后节点数: {len(cf_optimized.nodes)}")
    
    # 合并变量
    cf_optimized = cf_optimized.merge_vars()
    print(f"合并变量后节点数: {len(cf_optimized.nodes)}")
    
    # 删除不可达元素
    cf_optimized = cf_optimized.drop_unreachable(direction="forward", how="strong")
    print(f"删除不可达元素后节点数: {len(cf_optimized.nodes)}")
    
    return storage, cf_full

def practical_use_cases():
    """实际应用场景演示"""
    print("\n" + "="*80)
    print("实际应用场景演示")
    print("="*80)
    
    storage, cf_full = advanced_operations_demo()
    
    print("\n场景1: 数据质量分析")
    print("-" * 40)
    
    # 分析数据质量
    df_quality = cf_full.df()
    print(f"数据质量分析:")
    print(f"- 总数据量: {len(df_quality)}")
    print(f"- 数据列数: {len(df_quality.columns)}")
    print(f"- 缺失值统计:")
    print(df_quality.isnull().sum())
    
    print("\n场景2: 计算性能分析")
    print("-" * 40)
    
    # 分析计算性能
    print(f"计算性能分析:")
    print(f"- 函数调用次数:")
    for fname in cf_full.fnames:
        call_count = len(cf_full.fs[fname])
        print(f"  {fname}: {call_count} 次")
    
    print(f"- 引用对象数量:")
    for vname in cf_full.vnames:
        ref_count = len(cf_full.vs[vname])
        print(f"  {vname}: {ref_count} 个")
    
    print("\n场景3: 调试和故障排查")
    print("-" * 40)
    
    # 调试信息
    print(f"调试信息:")
    print(f"- 图完整性检查: ", end="")
    try:
        cf_full._check()
        print("通过")
    except Exception as e:
        print(f"失败 - {e}")
    
    # 存储信息
    print(f"- 存储状态:")
    storage.cache_info()
    
    print("\n场景4: 结果导出和报告")
    print("-" * 40)
    
    # 导出结果
    final_results = cf_full.df()
    
    print(f"导出结果:")
    print(f"- 数据形状: {final_results.shape}")
    print(f"- 数据预览:")
    print(final_results.head())
    
    # 生成报告
    print(f"\n执行报告:")
    print(f"- 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"- 计算图节点数: {len(cf_full.nodes)}")
    print(f"- 计算图边数: {len(cf_full.edges())}")
    print(f"- 数据记录数: {len(final_results)}")
    
    return storage, cf_full, final_results

def main():
    """主函数"""
    print("mandala框架完整演示")
    print("=" * 80)
    
    # 运行完整演示
    storage, cf_full, results = practical_use_cases()
    
    # 最终总结
    print("\n" + "="*80)
    print("总结")
    print("="*80)
    
    print(f"""
mandala框架演示完成！

关键特性展示:
1. 透明的计算历史记录
2. 自动记忆化避免重复计算
3. 灵活的计算图查询和操作
4. 强大的数据血缘追踪
5. 丰富的图操作（增删查改）
6. 高效的数据管理和存储

技术统计:
- 存储对象: {len(storage.atoms.cache)} 个原子, {len(storage.calls.cache)} 个调用
- 计算图: {len(cf_full.nodes)} 个节点, {len(cf_full.edges())} 条边
- 数据记录: {len(results)} 行 × {len(results.columns)} 列

框架优势:
- 无侵入式: 只需@op装饰器即可开始使用
- 高性能: 智能缓存和记忆化
- 可扩展: 支持复杂的计算图操作
- 易调试: 完整的计算历史追踪
- 生产就绪: 支持持久化存储和版本控制

这个框架特别适合:
- 数据科学和机器学习工作流
- 复杂的计算管道
- 需要重现性的科学计算
- 计算密集型应用的优化
    """)
    
    return storage, cf_full, results

if __name__ == "__main__":
    storage, cf_full, results = main()
    
    # 可选：保存结果
    print("\n保存结果到文件...")
    try:
        results.to_csv("mandala_demo_results.csv", index=False)
        print("结果已保存到 mandala_demo_results.csv")
    except Exception as e:
        print(f"保存结果失败: {e}")
    
    print("\n演示完成！") 
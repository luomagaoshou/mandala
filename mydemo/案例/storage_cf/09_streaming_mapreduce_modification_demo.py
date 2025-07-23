#!/usr/bin/env python3
"""
流式计算Map-Reduce精确节点修改演示
==================================

本示例演示如何在流式计算的Map-Reduce流程中实现精确的节点修改：
1. 实现完整的Map-Reduce数据处理管道
2. 在每个处理阶段进行精确参数修改
3. 展示流式计算中的增量更新和重新计算
4. 保持计算图的一致性和完整性

流程设计：
- 数据源生成：生成大量原始数据
- 数据分块：将数据分成多个块进行并行处理
- Map阶段：对每个数据块进行映射变换
- Shuffle阶段：按key重新分组数据
- Reduce阶段：对分组数据进行聚合计算
- 后处理：对最终结果进行格式化和验证
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from mandala1.imports import *
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Any, Set, TYPE_CHECKING
import time
import copy
import random
from collections import defaultdict
import math

if TYPE_CHECKING:
    from mandala1.cf import ComputationFrame
    from mandala1.core import Call

# 创建存储实例（使用内存数据库）
storage = Storage(db_path=":memory:")

# ==================== 数据源和分块阶段 ====================

@op
def generate_data_source(size: int = 1000, seed: int = 42, value_range: Tuple[float, float] = (0.0, 100.0)) -> List[Dict[str, Any]]:
    """
    生成数据源：模拟大量的原始数据
    """
    print(f"生成数据源 - 大小: {size}, 随机种子: {seed}, 值范围: {value_range}")
    
    random.seed(seed)
    np.random.seed(seed)
    
    data = []
    categories = ['A', 'B', 'C', 'D', 'E']
    
    for i in range(size):
        record = {
            'id': i,
            'category': random.choice(categories),
            'value': random.uniform(value_range[0], value_range[1]),
            'timestamp': time.time() + i,
            'metadata': {
                'source': f'sensor_{i % 10}',
                'quality': random.uniform(0.7, 1.0)
            }
        }
        data.append(record)
    
    print(f"   生成了 {len(data)} 条记录")
    return data

@op
def partition_data(data: List[Dict[str, Any]], num_partitions: int = 4, 
                  partition_strategy: str = "hash") -> Dict[int, List[Dict[str, Any]]]:
    """
    数据分块：将数据分成多个分区用于并行处理
    """
    print(f"数据分块 - 分区数: {num_partitions}, 策略: {partition_strategy}")
    
    partitions = defaultdict(list)
    
    for record in data:
        if partition_strategy == "hash":
            # 基于ID的哈希分区
            partition_id = record['id'] % num_partitions
        elif partition_strategy == "category":
            # 基于类别的分区
            partition_id = hash(record['category']) % num_partitions
        elif partition_strategy == "range":
            # 基于值范围的分区
            value = record['value']
            partition_id = min(int(value / (100.0 / num_partitions)), num_partitions - 1)
        else:
            partition_id = record['id'] % num_partitions
        
        partitions[partition_id].append(record)
    
    result = dict(partitions)
    for pid, partition in result.items():
        print(f"   分区 {pid}: {len(partition)} 条记录")
    
    return result

# ==================== Map阶段 ====================

@op
def map_transform_partition(partition_data: List[Dict[str, Any]], 
                           transform_type: str = "normalize",
                           scale_factor: float = 1.0,
                           filter_threshold: float = 0.0) -> List[Dict[str, Any]]:
    """
    Map阶段：对分区数据进行变换处理
    """
    print(f"Map变换 - 类型: {transform_type}, 缩放: {scale_factor}, 过滤阈值: {filter_threshold}")
    print(f"   处理 {len(partition_data)} 条记录")
    
    transformed = []
    
    for record in partition_data:
        # 计算变换后的值
        if transform_type == "normalize":
            # 归一化处理
            transformed_value = (record['value'] / 100.0) * scale_factor
        elif transform_type == "logarithm":
            # 对数变换
            transformed_value = math.log(record['value'] + 1) * scale_factor
        elif transform_type == "square":
            # 平方变换
            transformed_value = (record['value'] ** 2) * scale_factor
        else:
            transformed_value = record['value'] * scale_factor
        
        # 应用过滤条件
        if transformed_value >= filter_threshold:
            new_record = {
                'id': record['id'],
                'category': record['category'],
                'original_value': record['value'],
                'transformed_value': transformed_value,
                'quality_score': record['metadata']['quality'],
                'source': record['metadata']['source'],
                'timestamp': record['timestamp']
            }
            transformed.append(new_record)
    
    print(f"   变换后保留 {len(transformed)} 条记录")
    return transformed

@op
def map_compute_features(partition_data: List[Dict[str, Any]], 
                        feature_types: List[str] = ["mean", "variance"],
                        window_size: int = 10) -> Dict[str, List[Dict[str, Any]]]:
    """
    Map阶段：计算特征向量
    """
    print(f"Map特征计算 - 特征类型: {feature_types}, 窗口大小: {window_size}")
    
    features_by_category = defaultdict(list)
    
    # 按类别分组
    category_groups = defaultdict(list)
    for record in partition_data:
        category_groups[record['category']].append(record)
    
    # 为每个类别计算特征
    for category, records in category_groups.items():
        records.sort(key=lambda x: x['timestamp'])  # 按时间排序
        
        # 滑动窗口计算特征
        for i in range(0, len(records), window_size):
            window_records = records[i:i + window_size]
            if len(window_records) < window_size // 2:  # 跳过太小的窗口
                continue
            
            values = [r['transformed_value'] for r in window_records]
            qualities = [r['quality_score'] for r in window_records]
            
            feature_record = {
                'category': category,
                'window_start': i,
                'window_size': len(window_records),
                'features': {}
            }
            
            # 计算不同类型的特征
            if "mean" in feature_types:
                feature_record['features']['mean'] = np.mean(values)
            if "variance" in feature_types:
                feature_record['features']['variance'] = np.var(values)
            if "median" in feature_types:
                feature_record['features']['median'] = np.median(values)
            if "quality_avg" in feature_types:
                feature_record['features']['quality_avg'] = np.mean(qualities)
            
            features_by_category[category].append(feature_record)
    
    result = dict(features_by_category)
    for cat, features in result.items():
        print(f"   类别 {cat}: 计算了 {len(features)} 个特征窗口")
    
    return result

# ==================== Shuffle阶段 ====================

@op
def shuffle_merge_partitions(partition_results: List[Dict[str, List[Dict[str, Any]]]], 
                           merge_strategy: str = "category",
                           sort_by: str = "category") -> Dict[str, List[Dict[str, Any]]]:
    """
    Shuffle阶段：合并和重新分组来自不同分区的结果
    """
    print(f"Shuffle合并 - 策略: {merge_strategy}, 排序: {sort_by}")
    
    merged_data = defaultdict(list)
    
    # 合并所有分区的结果
    for partition_result in partition_results:
        for category, features in partition_result.items():
            merged_data[category].extend(features)
    
    # 对每个类别的数据进行排序
    for category in merged_data:
        if sort_by == "category":
            merged_data[category].sort(key=lambda x: x['category'])
        elif sort_by == "window_start":
            merged_data[category].sort(key=lambda x: x['window_start'])
        elif sort_by == "mean_value" and 'mean' in merged_data[category][0]['features']:
            merged_data[category].sort(key=lambda x: x['features']['mean'])
    
    result = dict(merged_data)
    total_records = sum(len(features) for features in result.values())
    print(f"   合并完成，总共 {total_records} 个特征窗口，分布在 {len(result)} 个类别中")
    
    return result

# ==================== Reduce阶段 ====================

@op
def reduce_aggregate_features(shuffled_data: Dict[str, List[Dict[str, Any]]], 
                             aggregation_functions: List[str] = ["sum", "avg", "max"],
                             min_window_count: int = 2) -> Dict[str, Dict[str, float]]:
    """
    Reduce阶段：对每个类别的特征进行聚合
    """
    print(f"Reduce聚合 - 函数: {aggregation_functions}, 最小窗口数: {min_window_count}")
    
    aggregated_results = {}
    
    for category, feature_windows in shuffled_data.items():
        if len(feature_windows) < min_window_count:
            print(f"   跳过类别 {category}，窗口数不足 ({len(feature_windows)} < {min_window_count})")
            continue
        
        category_aggregation = {}
        
        # 提取所有特征值
        feature_names = set()
        for window in feature_windows:
            feature_names.update(window['features'].keys())
        
        # 对每种特征类型进行聚合
        for feature_name in feature_names:
            feature_values = [w['features'][feature_name] for w in feature_windows 
                             if feature_name in w['features']]
            
            if not feature_values:
                continue
            
            feature_agg = {}
            
            if "sum" in aggregation_functions:
                feature_agg['sum'] = sum(feature_values)
            if "avg" in aggregation_functions:
                feature_agg['avg'] = np.mean(feature_values)
            if "max" in aggregation_functions:
                feature_agg['max'] = max(feature_values)
            if "min" in aggregation_functions:
                feature_agg['min'] = min(feature_values)
            if "std" in aggregation_functions:
                feature_agg['std'] = np.std(feature_values)
            
            category_aggregation[feature_name] = feature_agg
        
        aggregated_results[category] = category_aggregation
        print(f"   类别 {category}: 聚合了 {len(feature_names)} 种特征类型")
    
    return aggregated_results

@op
def reduce_compute_statistics(aggregated_data: Dict[str, Dict[str, Dict[str, float]]], 
                             stat_types: List[str] = ["correlation", "ranking"],
                             ranking_metric: str = "avg") -> Dict[str, Any]:
    """
    Reduce阶段：计算跨类别的统计信息
    """
    print(f"Reduce统计计算 - 统计类型: {stat_types}, 排名指标: {ranking_metric}")
    
    statistics = {}
    
    # 计算类别排名
    if "ranking" in stat_types:
        category_scores = {}
        for category, features in aggregated_data.items():
            # 计算类别的综合得分
            total_score = 0
            feature_count = 0
            
            for feature_name, agg_values in features.items():
                if ranking_metric in agg_values:
                    total_score += agg_values[ranking_metric]
                    feature_count += 1
            
            if feature_count > 0:
                category_scores[category] = total_score / feature_count
        
        # 按得分排序
        ranked_categories = sorted(category_scores.items(), 
                                 key=lambda x: x[1], reverse=True)
        statistics['category_ranking'] = ranked_categories
        print(f"   类别排名: {[cat for cat, score in ranked_categories]}")
    
    # 计算特征相关性
    if "correlation" in stat_types:
        # 简化的相关性计算
        feature_correlations = {}
        all_categories = list(aggregated_data.keys())
        
        if len(all_categories) >= 2:
            for i, cat1 in enumerate(all_categories):
                for cat2 in all_categories[i+1:]:
                    # 计算两个类别间的特征相似度
                    common_features = set(aggregated_data[cat1].keys()) & set(aggregated_data[cat2].keys())
                    if common_features:
                        correlations = []
                        for feature in common_features:
                            if ranking_metric in aggregated_data[cat1][feature] and ranking_metric in aggregated_data[cat2][feature]:
                                val1 = aggregated_data[cat1][feature][ranking_metric]
                                val2 = aggregated_data[cat2][feature][ranking_metric]
                                # 简化的相关性度量
                                correlation = 1.0 / (1.0 + abs(val1 - val2))
                                correlations.append(correlation)
                        
                        if correlations:
                            feature_correlations[f"{cat1}-{cat2}"] = np.mean(correlations)
        
        statistics['feature_correlations'] = feature_correlations
        print(f"   计算了 {len(feature_correlations)} 对类别的相关性")
    
    # 全局统计
    statistics['total_categories'] = len(aggregated_data)
    statistics['total_features'] = sum(len(features) for features in aggregated_data.values())
    
    return statistics

# ==================== 后处理阶段 ====================

@op
def post_process_results(statistics: Dict[str, Any], 
                        format_type: str = "summary",
                        top_n: int = 3,
                        include_details: bool = True) -> Dict[str, Any]:
    """
    后处理阶段：格式化和验证最终结果
    """
    print(f"后处理 - 格式: {format_type}, Top-N: {top_n}, 包含详情: {include_details}")
    
    processed_results = {
        'summary': {},
        'metadata': {
            'processing_time': time.time(),
            'format_type': format_type,
            'top_n': top_n
        }
    }
    
    # 生成摘要
    if 'category_ranking' in statistics:
        top_categories = statistics['category_ranking'][:top_n]
        processed_results['summary']['top_categories'] = [
            {'category': cat, 'score': score, 'rank': i+1} 
            for i, (cat, score) in enumerate(top_categories)
        ]
    
    if 'feature_correlations' in statistics:
        # 找出最高相关性的类别对
        correlations = statistics['feature_correlations']
        if correlations:
            max_correlation = max(correlations.items(), key=lambda x: x[1])
            processed_results['summary']['highest_correlation'] = {
                'category_pair': max_correlation[0],
                'correlation_score': max_correlation[1]
            }
    
    # 添加详细信息
    if include_details:
        processed_results['details'] = statistics
    
    processed_results['summary']['total_categories'] = statistics.get('total_categories', 0)
    processed_results['summary']['total_features'] = statistics.get('total_features', 0)
    
    print(f"   生成摘要包含 {len(processed_results['summary'])} 项指标")
    
    return processed_results

# ==================== 流式修改器类 ====================

class StreamingModifier:
    """
    流式计算修改器：专门处理流式计算流程中的参数修改
    """
    
    def __init__(self, storage: Storage):
        self.storage = storage
        self.modification_history = []
        
    def locate_call_by_context(self, cf: "ComputationFrame", function_name: str, 
                              input_context: Dict[str, Any] = None) -> List[Tuple[str, "Call"]]:
        """
        在流式计算的CF中定位特定函数调用
        """
        print(f"\n🔍 定位流式调用 - 函数: {function_name}")
        if input_context:
            print(f"   上下文条件: {input_context}")
        
        matching_calls = []
        
        if function_name not in cf.fs:
            print(f"❌ 函数 '{function_name}' 未在计算图中找到")
            return matching_calls
        
        call_hids = cf.fs[function_name]
        print(f"   找到 {len(call_hids)} 个调用")
        
        for call_hid in call_hids:
            call = cf.calls[call_hid]
            
            if not input_context:
                matching_calls.append((call_hid, call))
                continue
            
            call_inputs = {k: self.storage.unwrap(v) for k, v in call.inputs.items()}
            match = True
            
            for param_name, expected_value in input_context.items():
                if param_name not in call_inputs:
                    match = False
                    break
                if call_inputs[param_name] != expected_value:
                    match = False
                    break
            
            if match:
                matching_calls.append((call_hid, call))
                print(f"   ✅ 匹配调用 {call_hid[:8]}...")
        
        print(f"🎯 共找到 {len(matching_calls)} 个匹配的调用")
        return matching_calls
    
    def modify_and_reexecute_stage(self, cf: "ComputationFrame", 
                                  stage_function: str, 
                                  param_modifications: Dict[str, Any],
                                  context_filter: Dict[str, Any] = None) -> "ComputationFrame":
        """
        修改特定阶段的参数并重新执行，使用更安全的节点替换策略
        """
        print(f"\n🔄 修改执行阶段 - {stage_function}")
        print(f"   参数修改: {param_modifications}")
        
        # 定位目标函数调用
        matching_calls = self.locate_call_by_context(cf, stage_function, context_filter)
        
        if not matching_calls:
            print("❌ 未找到匹配的调用")
            return cf
        
        # 选择第一个匹配的调用进行修改
        call_hid, call = matching_calls[0]
        
        # 获取原始参数并应用修改
        original_inputs = {k: self.storage.unwrap(v) for k, v in call.inputs.items()}
        print(f"   原始参数: {list(original_inputs.keys())}")
        
        modified_inputs = original_inputs.copy()
        for param_name, new_value in param_modifications.items():
            if param_name in modified_inputs:
                old_value = modified_inputs[param_name]
                modified_inputs[param_name] = new_value
                print(f"   📝 {param_name}: {old_value} -> {new_value}")
                
                # 记录修改历史
                self.modification_history.append({
                    "stage": stage_function,
                    "call_hid": call_hid,
                    "param_name": param_name,
                    "old_value": old_value,
                    "new_value": new_value,
                    "timestamp": time.time()
                })
            else:
                print(f"   ⚠️  参数 {param_name} 不存在，跳过")
        
        # 找到目标函数节点
        target_func_name = None
        for fname in cf.fnames:
            if call_hid in cf.fs[fname]:
                target_func_name = fname
                break
                
        if not target_func_name:
            print(f"❌ 无法找到调用对应的函数节点")
            return cf
            
        print(f"   🎯 目标函数节点: {target_func_name}")
        
        # 记录原始统计信息
        original_var_count = len(cf.vnames)
        original_func_count = len(cf.fnames)
        print(f"   📊 原始图统计 - 变量: {original_var_count}, 函数: {original_func_count}")
        
        # 重新执行修改的函数获取新结果
        with self.storage:
            print(f"   ⚡ 重新执行 {stage_function}...")
            
            if stage_function == "generate_data_source":
                new_result = generate_data_source(**modified_inputs)
            elif stage_function == "partition_data":
                new_result = partition_data(**modified_inputs)
            elif stage_function == "map_transform_partition":
                new_result = map_transform_partition(**modified_inputs)
            elif stage_function == "map_compute_features":
                new_result = map_compute_features(**modified_inputs)
            elif stage_function == "shuffle_merge_partitions":
                new_result = shuffle_merge_partitions(**modified_inputs)
            elif stage_function == "reduce_aggregate_features":
                new_result = reduce_aggregate_features(**modified_inputs)
            elif stage_function == "reduce_compute_statistics":
                new_result = reduce_compute_statistics(**modified_inputs)
            elif stage_function == "post_process_results":
                new_result = post_process_results(**modified_inputs)
            else:
                raise ValueError(f"不支持的函数: {stage_function}")
            
            print(f"   ✅ 重新执行 {stage_function} 成功")
            
        # 获取新调用
        new_call = self.storage.get_ref_creator(new_result)
        if not new_call:
            print(f"❌ 无法获取新调用")
            return cf
            
        print(f"   📋 新调用 ID: {new_call.hid[:8]}...")
        
        # 策略：创建新的 ComputationFrame 并使用集合操作来替换
        print(f"   🔄 构建替换后的计算图...")
        
        # 1. 创建包含新结果的 ComputationFrame
        new_cf = self.storage.cf(new_result)
        
        # 2. 如果需要扩展以包含下游依赖
        if target_func_name == "generate_data_source":
            # 对于数据源，可能需要扩展前向以包含数据分区
            new_cf = new_cf.expand_forward()
        
        # 3. 使用选择操作来保持与原始CF相同的节点结构
        if len(new_cf.vnames) != original_var_count or len(new_cf.fnames) != original_func_count:
            print(f"   🔧 调整计算图结构以匹配原始...")
            
            # 确保包含原始的函数节点
            if target_func_name not in new_cf.fnames:
                # 手动重建相同结构的CF
                result_cf = cf.copy()
                
                # 安全地移除旧调用：使用 select_subsets 来排除特定调用
                old_call_hids = {call_hid}
                new_fs = {}
                for fname, call_hids in result_cf.fs.items():
                    filtered_calls = call_hids - old_call_hids
                    if fname == target_func_name:
                        # 为目标函数添加新调用
                        filtered_calls.add(new_call.hid)
                        # 添加新调用到存储
                        result_cf.calls[new_call.hid] = new_call
                        if new_call.hid not in result_cf.callinv:
                            result_cf.callinv[new_call.hid] = set()
                        result_cf.callinv[new_call.hid].add(fname)
                    new_fs[fname] = filtered_calls
                
                # 更新函数集合
                result_cf.fs = new_fs
                
                # 清理孤立的调用引用
                if call_hid in result_cf.calls:
                    del result_cf.calls[call_hid]
                if call_hid in result_cf.callinv:
                    del result_cf.callinv[call_hid]
                
                # 更新引用映射
                for output_name, output_ref in new_call.outputs.items():
                    result_cf.refs[output_ref.hid] = output_ref
                    result_cf.creator[output_ref.hid] = new_call.hid
                    
                    # 找到对应的输出变量并更新引用
                    for src, dst, label in result_cf.out_edges(target_func_name):
                        if dst in result_cf.vnames:
                            # 移除旧引用
                            old_refs = set()
                            for old_out_name, old_out_ref in call.outputs.items():
                                if old_out_ref.hid in result_cf.vs[dst]:
                                    old_refs.add(old_out_ref.hid)
                            
                            for old_ref_hid in old_refs:
                                result_cf.vs[dst].discard(old_ref_hid)
                                if old_ref_hid in result_cf.refs:
                                    del result_cf.refs[old_ref_hid]
                                if old_ref_hid in result_cf.creator:
                                    del result_cf.creator[old_ref_hid]
                                if old_ref_hid in result_cf.refinv:
                                    del result_cf.refinv[old_ref_hid]
                            
                            # 添加新引用
                            result_cf.vs[dst].add(output_ref.hid)
                            if output_ref.hid not in result_cf.refinv:
                                result_cf.refinv[output_ref.hid] = set()
                            result_cf.refinv[output_ref.hid].add(dst)
                            break
                
                # 更新输入引用的消费者映射
                for input_name, input_ref in new_call.inputs.items():
                    if input_ref.hid not in result_cf.consumers:
                        result_cf.consumers[input_ref.hid] = set()
                    result_cf.consumers[input_ref.hid].add(new_call.hid)
            else:
                result_cf = new_cf
        else:
            result_cf = new_cf
        
        # 验证节点数量一致性
        final_var_count = len(result_cf.vnames)
        final_func_count = len(result_cf.fnames)
        
        print(f"   📊 最终图统计 - 变量: {final_var_count}, 函数: {final_func_count}")
        
        if final_var_count == original_var_count and final_func_count == original_func_count:
            print(f"   ✅ 计算图结构保持完全一致")
        else:
            print(f"   ⚠️  计算图结构发生变化")
            print(f"   变量数量: {original_var_count} -> {final_var_count}")
            print(f"   函数数量: {original_func_count} -> {final_func_count}")
        
        print(f"   ✅ 节点替换完成")
        return result_cf
    
    def get_modification_summary(self) -> Dict[str, Any]:
        """
        获取修改摘要
        """
        if not self.modification_history:
            return {}
        
        summary = {
            "total_modifications": len(self.modification_history),
            "modified_stages": {},
            "modified_parameters": {},
            "timeline": []
        }
        
        for mod in self.modification_history:
            stage = mod['stage']
            param = mod['param_name']
            
            summary["modified_stages"][stage] = summary["modified_stages"].get(stage, 0) + 1
            summary["modified_parameters"][param] = summary["modified_parameters"].get(param, 0) + 1
            
            summary["timeline"].append({
                "timestamp": mod['timestamp'],
                "stage": stage,
                "parameter": param,
                "change": f"{mod['old_value']} -> {mod['new_value']}"
            })
        
        return summary

# ==================== 主演示流程 ====================

def run_complete_streaming_pipeline():
    """
    运行完整的流式计算管道
    """
    print("=" * 80)
    print("1. 运行完整的流式Map-Reduce计算管道")
    print("=" * 80)
    
    with storage:
        # 阶段1：生成数据源
        print("\n--- 阶段1: 数据源生成 ---")
        raw_data = generate_data_source(size=500, seed=42, value_range=(1.0, 100.0))
        
        # 阶段2：数据分区
        print("\n--- 阶段2: 数据分区 ---")
        partitioned_data = partition_data(raw_data, num_partitions=4, partition_strategy="hash")
        
        # 阶段3：Map变换（并行处理每个分区）
        print("\n--- 阶段3: Map变换处理 ---")
        map_results = []
        partitioned_data_unwrapped = storage.unwrap(partitioned_data)
        for partition_id, partition_records in partitioned_data_unwrapped.items():
            print(f"\n处理分区 {partition_id}:")
            # 变换数据
            transformed_partition = map_transform_partition(
                partition_records, 
                transform_type="normalize", 
                scale_factor=1.0, 
                filter_threshold=0.1
            )
            
            # 计算特征
            partition_features = map_compute_features(
                transformed_partition, 
                feature_types=["mean", "variance", "quality_avg"], 
                window_size=8
            )
            
            map_results.append(partition_features)
        
        # 阶段4：Shuffle合并
        print("\n--- 阶段4: Shuffle合并 ---")
        shuffled_data = shuffle_merge_partitions(
            map_results, 
            merge_strategy="category", 
            sort_by="window_start"
        )
        
        # 阶段5：Reduce聚合
        print("\n--- 阶段5: Reduce聚合 ---")
        aggregated_features = reduce_aggregate_features(
            shuffled_data, 
            aggregation_functions=["sum", "avg", "max", "std"], 
            min_window_count=2
        )
        
        # 阶段6：统计计算
        print("\n--- 阶段6: 统计计算 ---")
        statistics = reduce_compute_statistics(
            aggregated_features, 
            stat_types=["correlation", "ranking"], 
            ranking_metric="avg"
        )
        
        # 阶段7：后处理
        print("\n--- 阶段7: 后处理 ---")
        final_results = post_process_results(
            statistics, 
            format_type="summary", 
            top_n=3, 
            include_details=True
        )
        
        print(f"\n🎉 流式计算管道执行完成！")
        final_results_unwrapped = storage.unwrap(final_results)
        print(f"最终结果摘要: {final_results_unwrapped['summary']}")
        
    return final_results

def demonstrate_streaming_modifications():
    """
    演示流式计算中的各阶段参数修改
    """
    print("\n" + "=" * 80)
    print("2. 演示流式计算各阶段的精确参数修改")
    print("=" * 80)
    
    # 创建修改器
    modifier = StreamingModifier(storage)
    
    # 获取完整的计算图（包含所有函数）
    print("\n构建完整的计算图...")
    full_cf = storage.cf(generate_data_source).expand_all()
    print(f"计算图统计 - 变量: {len(full_cf.vnames)}, 函数: {len(full_cf.fnames)}")
    print(f"函数列表: {list(full_cf.fnames)}")
    
    current_cf = full_cf
    
    # 修改场景1：调整数据源参数
    print(f"\n" + "-" * 60)
    print("场景1: 修改数据源生成参数")
    print("-" * 60)
    
    current_cf = modifier.modify_and_reexecute_stage(
        cf=current_cf,
        stage_function="generate_data_source",
        param_modifications={
            "size": 300,  # 从500减少到300
            "value_range": (5.0, 95.0)  # 调整值范围
        }
    )
    
    # 修改场景2：调整数据分区参数
    print(f"\n" + "-" * 60)
    print("场景2: 修改数据分区参数")
    print("-" * 60)
    
    current_cf = modifier.modify_and_reexecute_stage(
        cf=current_cf,
        stage_function="partition_data",
        param_modifications={
            "num_partitions": 6,  # 从4改为6
            "partition_strategy": "category"  # 从hash改为category
        }
    )
    
    # 显示修改摘要
    print(f"\n" + "=" * 80)
    print("3. 流式计算修改摘要")
    print("=" * 80)
    
    summary = modifier.get_modification_summary()
    
    print(f"总修改次数: {summary.get('total_modifications', 0)}")
    print(f"\n各阶段修改统计:")
    for stage, count in summary.get('modified_stages', {}).items():
        print(f"  - {stage}: {count} 次修改")
    
    print(f"\n参数修改统计:")
    for param, count in summary.get('modified_parameters', {}).items():
        print(f"  - {param}: {count} 次修改")
    
    # 显示最终结果
    print(f"\n最终计算图统计:")
    print(f"  变量节点: {len(current_cf.vnames)}")
    print(f"  函数节点: {len(current_cf.fnames)}")
    
    # 安全地获取最终结果
    print(f"\n修改后的最终结果:")
    
    # 检查是否有空函数节点
    empty_functions = []
    for fname in current_cf.fnames:
        if not current_cf.fs[fname]:
            empty_functions.append(fname)
    
    if empty_functions:
        print(f"⚠️  发现空函数节点: {empty_functions}")
        print("直接获取汇点变量的值")
    else:
        print("✅ 计算图完整，获取最终结果")
    
    # 直接获取汇点变量的值，避免 eval() 的复杂性
    if current_cf.sinks:
        sink_var = list(current_cf.sinks)[0]
        sink_values = current_cf.get_var_values(sink_var)
        if sink_values:
            sample_value = next(iter(sink_values))
            result = storage.unwrap(sample_value)
            print(f"汇点变量 '{sink_var}' 的结果: {str(result)[:300]}...")
        else:
            print("汇点变量无内容")
    else:
        # 如果没有汇点变量，获取所有变量的值
        print("无汇点变量，显示所有变量的值:")
        for vname in current_cf.vnames:
            values = current_cf.get_var_values(vname)
            if values:
                sample_value = next(iter(values))
                result = storage.unwrap(sample_value)
                print(f"变量 '{vname}': {str(result)[:100]}...")
            else:
                print(f"变量 '{vname}': 无内容")
    
    return current_cf, modifier

def analyze_streaming_performance():
    """
    分析流式计算的性能和修改影响
    """
    print(f"\n" + "=" * 80)
    print("4. 流式计算性能分析")
    print("=" * 80)
    
    print("流式Map-Reduce计算的优势:")
    print("✅ 数据分区并行处理，提升计算效率")
    print("✅ 阶段化处理，便于调试和优化")
    print("✅ 精确参数修改，避免全量重计算")
    print("✅ 增量更新支持，适应数据流变化")
    
    print("\n参数修改的影响分析:")
    print("🔄 数据源修改 -> 影响整个管道")
    print("🔄 Map阶段修改 -> 影响下游聚合和统计")
    print("🔄 Reduce阶段修改 -> 影响最终结果格式")
    print("🔄 后处理修改 -> 仅影响输出展示")
    
    print("\nMandala框架在流式计算中的作用:")
    print("📊 自动记录计算图依赖关系")
    print("💾 智能缓存中间结果")
    print("🔍 支持精确的节点定位")
    print("⚡ 高效的增量重新计算")

def main():
    """
    主函数：演示完整的流式计算Map-Reduce修改流程
    """
    print("流式计算Map-Reduce精确节点修改演示")
    print("使用mandala框架实现大规模数据处理管道的参数调优")
    
    # 1. 运行完整的流式计算管道
    initial_results = run_complete_streaming_pipeline()
    
    # 2. 演示各阶段的参数修改
    final_cf, modifier = demonstrate_streaming_modifications()
    
    # 3. 性能分析
    analyze_streaming_performance()
    
    print(f"\n" + "=" * 80)
    print("流式计算Map-Reduce修改演示完成！")
    print("=" * 80)
    
    print("\n核心特性展示:")
    print("🌊 完整的流式Map-Reduce计算管道")
    print("🎯 多阶段精确参数修改")
    print("🔄 智能增量重新计算")
    print("📈 实时性能监控和分析")
    print("💡 基于Mandala框架的高效实现")

if __name__ == "__main__":
    main() 
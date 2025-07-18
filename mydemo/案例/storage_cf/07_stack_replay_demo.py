#!/usr/bin/env python3
"""
栈回放（函数再执行）最小用例演示
=================================

本示例演示如何利用mandala框架实现栈回放功能：
1. 运行两层函数，形成计算图
2. 分析计算图，找到需要重新执行的函数
3. 修改参数，重新执行特定函数
4. 用新结果替换旧节点，生成新的ComputationFrame

主要功能：
- 两层函数调用（第二层有循环复杂度）
- 基于上下文和参数的函数重新执行
- 计算图节点的替换和更新
- 使用mandala已有功能避免重复实现
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from mandala1.imports import *
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
import time

# 创建存储实例
storage = Storage(db_path="mydemo/mandala_storage/stack_replay_demo.db")

@op
def preprocess_data(data: List[float], multiplier: float = 1.0) -> List[float]:
    """
    第一层函数：数据预处理
    """
    print(f"预处理数据: {data}, 乘数: {multiplier}")
    return [x * multiplier for x in data]

@op 
def analyze_batch(batch_data: List[float], threshold: float = 5.0) -> Dict[str, Any]:
    """
    第二层函数：批量分析（包含循环复杂度）
    """
    print(f"分析批次数据: {batch_data}, 阈值: {threshold}")
    
    # 循环处理每个数据点
    results = []
    stats = {"above_threshold": 0, "total": len(batch_data)}
    
    for i, value in enumerate(batch_data):
        # 模拟复杂处理
        processed = value ** 2
        if processed > threshold:
            stats["above_threshold"] += 1
            results.append({"index": i, "value": value, "processed": processed, "status": "high"})
        else:
            results.append({"index": i, "value": value, "processed": processed, "status": "low"})
    
    return {
        "results": results,
        "stats": stats,
        "summary": f"处理了{stats['total']}个数据点，{stats['above_threshold']}个超过阈值"
    }

def run_initial_computation():
    """
    运行初始计算，形成计算图
    """
    print("=" * 50)
    print("1. 运行初始计算")
    print("=" * 50)
    
    with storage:
        # 第一层：数据预处理
        raw_data = [1.0, 2.0, 3.0, 4.0, 5.0]
        preprocessed = preprocess_data(raw_data, multiplier=2.0)
        
        # 第二层：批量分析
        analysis_result = analyze_batch(preprocessed, threshold=10.0)
        
        print(f"预处理结果: {storage.unwrap(preprocessed)}")
        print(f"分析结果: {storage.unwrap(analysis_result)}")
        
    return preprocessed, analysis_result

def analyze_computation_graph():
    """
    分析计算图，找到需要重新执行的函数
    """
    print("\n" + "=" * 50)
    print("2. 分析计算图")
    print("=" * 50)
    
    # 创建包含所有函数的计算图
    cf = storage.cf(preprocess_data).expand_all()
    
    print("\n计算图结构:")
    cf.print_graph()
    
    print(f"\n计算图统计:")
    print(f"- 变量节点数: {len(cf.vnames)}")
    print(f"- 函数节点数: {len(cf.fnames)}")
    print(f"- 引用数: {len(cf.refs)}")
    print(f"- 调用数: {len(cf.calls)}")
    
    # 获取函数调用的详细信息
    print("\n函数调用详情:")
    for fname, call_hids in cf.fs.items():
        print(f"- {fname}: {len(call_hids)} 次调用")
        for call_hid in call_hids:
            call = cf.calls[call_hid]
            inputs = {k: storage.unwrap(v) for k, v in call.inputs.items()}
            outputs = {k: storage.unwrap(v) for k, v in call.outputs.items()}
            print(f"  调用 {call_hid[:8]}...")
            print(f"    输入: {inputs}")
            print(f"    输出: {outputs}")
    
    return cf

def replay_function_with_new_params(cf, target_function: str, new_params: Dict[str, Any]):
    """
    重新执行指定函数，使用新参数
    """
    print(f"\n" + "=" * 50)
    print(f"3. 重新执行函数: {target_function}")
    print("=" * 50)
    
    # 找到目标函数的调用
    target_calls = []
    if target_function in cf.fs:
        for call_hid in cf.fs[target_function]:
            call = cf.calls[call_hid]
            target_calls.append(call)
    
    if not target_calls:
        print(f"未找到函数 {target_function} 的调用")
        return {}
    
    print(f"找到 {len(target_calls)} 个 {target_function} 的调用")
    
    # 重新执行调用（只执行第一个调用，避免重复）
    new_refs = {}
    with storage:
        # 只重新执行第一个调用，因为相同参数的调用会被memoized
        call = target_calls[0]
        print(f"\n重新执行调用 {call.hid[:8]}...")
        
        # 获取原始输入
        original_inputs = {k: storage.unwrap(v) for k, v in call.inputs.items()}
        print(f"原始输入: {original_inputs}")
        
        # 应用新参数
        updated_inputs = original_inputs.copy()
        updated_inputs.update(new_params)
        print(f"新参数: {updated_inputs}")
        
        # 重新执行函数
        try:
            if target_function == "preprocess_data":
                new_result = preprocess_data(**updated_inputs)
            elif target_function == "analyze_batch":
                new_result = analyze_batch(**updated_inputs)
            else:
                print(f"不支持的函数: {target_function}")
                return {}
            
            # 存储新结果的引用
            new_refs[call.hid] = new_result
            print(f"新结果: {storage.unwrap(new_result)}")
            
            # 如果新参数导致的结果不同，继续执行下游函数
            # 这里可以扩展为自动执行下游函数
            if target_function == "preprocess_data":
                print("自动执行下游函数 analyze_batch...")
                # 使用新的预处理结果执行分析
                analysis_result = analyze_batch(new_result, threshold=10.0)
                print(f"下游分析结果: {storage.unwrap(analysis_result)}")
                new_refs[f"{call.hid}_downstream"] = analysis_result
                
        except Exception as e:
            print(f"重新执行函数时出错: {e}")
            return {}
    
    return new_refs

def update_computation_graph(cf, target_function: str, new_refs: Dict[str, Any]):
    """
    更新计算图，替换旧节点
    使用更安全的方法：创建新的计算图而不是修改旧的
    """
    print(f"\n" + "=" * 50)
    print(f"4. 更新计算图")
    print("=" * 50)
    
    # 找到需要更新的函数节点
    if target_function not in cf.fs:
        print(f"目标函数 {target_function} 不在计算图中")
        return cf
    
    try:
        # 创建包含新结果的计算图
        print("创建包含新结果的计算图...")
        new_result_refs = list(new_refs.values())
        
        # 从新结果开始创建计算图
        new_cf = storage.cf(new_result_refs[0])
        
        # 扩展计算图以包含所有相关的计算
        print("扩展计算图以包含相关计算...")
        new_cf.expand_back(inplace=True, verbose=True)
        new_cf.expand_forward(inplace=True, verbose=True)
        
        # 清理空节点
        new_cf.cleanup(inplace=True)
        
        print(f"更新后的计算图包含:")
        print(f"- 变量节点: {len(new_cf.vnames)}")
        print(f"- 函数节点: {len(new_cf.fnames)}")
        print(f"- 引用数: {len(new_cf.refs)}")
        print(f"- 调用数: {len(new_cf.calls)}")
        
        return new_cf
        
    except Exception as e:
        print(f"更新计算图时出错: {e}")
        print("使用原始计算图...")
        return cf

def compare_results(original_cf, updated_cf):
    """
    比较原始和更新后的计算图
    """
    print(f"\n" + "=" * 50)
    print("5. 比较结果")
    print("=" * 50)
    
    print("原始计算图:")
    original_cf.print_graph()
    
    print("\n更新后的计算图:")
    updated_cf.print_graph()
    
    print(f"\n统计比较:")
    print(f"原始 - 变量: {len(original_cf.vnames)}, 函数: {len(original_cf.fnames)}, 引用: {len(original_cf.refs)}")
    print(f"更新 - 变量: {len(updated_cf.vnames)}, 函数: {len(updated_cf.fnames)}, 引用: {len(updated_cf.refs)}")
    
    # 获取最终结果进行比较
    try:
        print(f"\n最终结果比较:")
        print("原始结果:")
        
        # 尝试获取原始计算图的最终结果
        try:
            original_data = original_cf.eval()
            print(original_data)
        except Exception as e:
            print(f"无法获取原始结果: {e}")
            
        print("\n更新结果:")
        
        # 尝试获取更新后计算图的最终结果
        try:
            updated_data = updated_cf.eval()
            print(updated_data)
        except Exception as e:
            print(f"无法获取更新结果: {e}")
            
        # 手动比较关键变量的值
        print("\n关键变量值比较:")
        
        # 比较预处理结果
        for vname in original_cf.vnames:
            if "var_0" in vname:  # 这通常是预处理结果
                try:
                    original_values = [storage.unwrap(ref) for ref in original_cf.get_var_values(vname)]
                    print(f"原始 {vname}: {original_values}")
                except Exception as e:
                    print(f"无法获取原始 {vname}: {e}")
                    
        for vname in updated_cf.vnames:
            if "var_0" in vname:  # 这通常是预处理结果
                try:
                    updated_values = [storage.unwrap(ref) for ref in updated_cf.get_var_values(vname)]
                    print(f"更新 {vname}: {updated_values}")
                except Exception as e:
                    print(f"无法获取更新 {vname}: {e}")
        
    except Exception as e:
        print(f"结果比较时出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    """
    主函数：演示完整的栈回放流程
    """
    print("栈回放（函数再执行）演示")
    print("使用mandala框架实现函数重新执行和计算图更新")
    
    try:
        # 1. 运行初始计算
        preprocessed, analysis_result = run_initial_computation()
        
        # 2. 分析计算图
        original_cf = analyze_computation_graph()
        
        # 3. 重新执行preprocess_data函数，使用新的multiplier参数
        new_params = {"multiplier": 3.0}  # 从2.0改为3.0
        new_refs = replay_function_with_new_params(original_cf, "preprocess_data", new_params)
        
        # 4. 更新计算图
        updated_cf = update_computation_graph(original_cf, "preprocess_data", new_refs)
        
        # 5. 比较结果
        compare_results(original_cf, updated_cf)
        
        print(f"\n" + "=" * 50)
        print("栈回放演示完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"演示过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
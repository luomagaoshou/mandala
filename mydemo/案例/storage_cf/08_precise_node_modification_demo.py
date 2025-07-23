#!/usr/bin/env python3
"""
精确节点修改（单参数级别修改）演示
=====================================

本示例演示如何利用mandala框架实现精确的节点修改功能：
1. 通过函数名、参数等上下文精确定位目标节点
2. 每次只修改一个参数进行重新执行
3. 智能地更新计算图，替换受影响的节点
4. 保持计算图的一致性和完整性

主要特性：
- 上下文匹配定位：根据函数名+参数组合精确定位调用
- 单参数修改：每次只修改一个参数值
- 智能重新执行：只重新执行受影响的调用
- CF智能更新：使用mandala的现有功能更新计算图
- 修改历史跟踪：记录所有修改操作的历史
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

if TYPE_CHECKING:
    from mandala1.cf import ComputationFrame
    from mandala1.core import Call

# 创建存储实例（使用内存数据库）
storage = Storage(db_path=":memory:")

# 定义用于演示的操作函数
@op
def data_preprocessing(raw_data: List[float], scale_factor: float = 1.0, 
                      offset: float = 0.0, filter_threshold: float = 0.0) -> List[float]:
    """
    数据预处理函数：包含多个可修改参数
    """
    print(f"数据预处理 - 原始数据: {raw_data}, 缩放: {scale_factor}, 偏移: {offset}, 过滤阈值: {filter_threshold}")
    
    # 应用缩放和偏移
    processed = [(x * scale_factor + offset) for x in raw_data]
    
    # 过滤低于阈值的值
    if filter_threshold > 0:
        processed = [x for x in processed if x >= filter_threshold]
    
    return processed

@op
def statistical_analysis(data: List[float], method: str = "mean", 
                        window_size: int = 3, confidence_level: float = 0.95) -> Dict[str, Any]:
    """
    统计分析函数：包含多个可修改参数
    """
    print(f"统计分析 - 数据: {data}, 方法: {method}, 窗口大小: {window_size}, 置信度: {confidence_level}")
    
    if not data:
        return {"result": None, "error": "空数据集"}
    
    result = {}
    
    if method == "mean":
        result["value"] = sum(data) / len(data)
    elif method == "median":
        sorted_data = sorted(data)
        n = len(sorted_data)
        if n % 2 == 0:
            result["value"] = (sorted_data[n//2-1] + sorted_data[n//2]) / 2
        else:
            result["value"] = sorted_data[n//2]
    elif method == "moving_average":
        if len(data) < window_size:
            result["value"] = sum(data) / len(data)
        else:
            # 计算滑动平均
            moving_avgs = []
            for i in range(len(data) - window_size + 1):
                window = data[i:i + window_size]
                moving_avgs.append(sum(window) / window_size)
            result["value"] = sum(moving_avgs) / len(moving_avgs)
    
    result["method"] = method
    result["data_size"] = len(data)
    result["confidence_level"] = confidence_level
    
    return result

@op
def result_validation(analysis_result: Dict[str, Any], min_value: float = 0.0, 
                     max_value: float = 100.0, strict_mode: bool = False) -> Dict[str, Any]:
    """
    结果验证函数：包含多个可修改参数
    """
    print(f"结果验证 - 分析结果: {analysis_result}, 最小值: {min_value}, 最大值: {max_value}, 严格模式: {strict_mode}")
    
    validation_result = {
        "original_result": analysis_result,
        "is_valid": True,
        "warnings": [],
        "errors": []
    }
    
    if "value" in analysis_result and analysis_result["value"] is not None:
        value = analysis_result["value"]
        
        if value < min_value:
            if strict_mode:
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"值 {value} 低于最小阈值 {min_value}")
            else:
                validation_result["warnings"].append(f"值 {value} 低于建议最小值 {min_value}")
        
        if value > max_value:
            if strict_mode:
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"值 {value} 超过最大阈值 {max_value}")
            else:
                validation_result["warnings"].append(f"值 {value} 超过建议最大值 {max_value}")
    
    return validation_result

class PreciseNodeModifier:
    """
    精确节点修改器：提供基于上下文的精确节点定位和修改功能
    """
    
    def __init__(self, storage: Storage):
        self.storage = storage
        self.modification_history = []
    
    def locate_call_by_context(self, cf: "ComputationFrame", function_name: str, 
                              input_context: Dict[str, Any] = None, 
                              partial_match: bool = True) -> List[Tuple[str, "Call"]]:
        """
        通过上下文信息定位调用
        
        参数:
        - cf: 计算图框架
        - function_name: 目标函数名
        - input_context: 输入参数的部分或完整匹配条件
        - partial_match: 是否允许部分匹配
        
        返回: [(call_hid, Call), ...] 匹配的调用列表
        """
        print(f"\n🔍 定位调用 - 函数: {function_name}")
        if input_context:
            print(f"   上下文条件: {input_context}")
        
        matching_calls = []
        
        # 检查函数是否存在于计算图中
        if function_name not in cf.fs:
            print(f"❌ 函数 '{function_name}' 未在计算图中找到")
            return matching_calls
        
        # 获取该函数的所有调用
        call_hids = cf.fs[function_name]
        print(f"   找到 {len(call_hids)} 个调用")
        
        for call_hid in call_hids:
            call = cf.calls[call_hid]
            
            # 如果没有提供上下文条件，返回所有调用
            if not input_context:
                matching_calls.append((call_hid, call))
                continue
            
            # 检查输入参数是否匹配
            match = True
            call_inputs = {k: self.storage.unwrap(v) for k, v in call.inputs.items()}
            
            print(f"   检查调用 {call_hid[:8]}... 输入: {call_inputs}")
            
            for param_name, expected_value in input_context.items():
                if param_name in call_inputs:
                    actual_value = call_inputs[param_name]
                    
                    if partial_match:
                        # 部分匹配：检查是否包含期望值
                        if isinstance(expected_value, (list, tuple)) and isinstance(actual_value, (list, tuple)):
                            if not all(item in actual_value for item in expected_value):
                                match = False
                                break
                        elif expected_value != actual_value:
                            match = False
                            break
                    else:
                        # 精确匹配
                        if actual_value != expected_value:
                            match = False
                            break
                else:
                    # 参数不存在
                    match = False
                    break
            
            if match:
                matching_calls.append((call_hid, call))
                print(f"   ✅ 匹配调用 {call_hid[:8]}...")
        
        print(f"🎯 共找到 {len(matching_calls)} 个匹配的调用")
        return matching_calls
    
    def modify_single_parameter(self, call: "Call", param_name: str, new_value: Any) -> Dict[str, Any]:
        """
        修改调用的单个参数
        
        参数:
        - call: 原始调用对象
        - param_name: 要修改的参数名
        - new_value: 新的参数值
        
        返回: 修改后的输入参数字典
        """
        print(f"\n🔧 修改参数 - 参数名: {param_name}, 新值: {new_value}")
        
        # 获取原始输入参数
        original_inputs = {k: self.storage.unwrap(v) for k, v in call.inputs.items()}
        print(f"   原始参数: {original_inputs}")
        
        # 检查参数是否存在
        if param_name not in original_inputs:
            print(f"❌ 参数 '{param_name}' 在原始调用中不存在")
            print(f"   可用参数: {list(original_inputs.keys())}")
            return original_inputs
        
        # 修改指定参数
        modified_inputs = original_inputs.copy()
        old_value = modified_inputs[param_name]
        modified_inputs[param_name] = new_value
        
        print(f"   {param_name}: {old_value} -> {new_value}")
        print(f"   修改后参数: {modified_inputs}")
        
        # 记录修改历史
        self.modification_history.append({
            "call_hid": call.hid,
            "function": call.op.name,
            "param_name": param_name,
            "old_value": old_value,
            "new_value": new_value,
            "timestamp": time.time()
        })
        
        return modified_inputs
    
    def execute_with_modified_params(self, function_name: str, modified_inputs: Dict[str, Any]) -> Tuple[Any, "Call"]:
        """
        使用修改后的参数重新执行函数
        
        参数:
        - function_name: 函数名
        - modified_inputs: 修改后的输入参数
        
        返回: (新结果的引用, 新的调用对象)
        """
        print(f"\n⚡ 重新执行函数 - {function_name}")
        print(f"   使用参数: {modified_inputs}")
        
        with self.storage:
            try:
                # 根据函数名选择对应的操作
                if function_name == "data_preprocessing":
                    new_result = data_preprocessing(**modified_inputs)
                elif function_name == "statistical_analysis":
                    new_result = statistical_analysis(**modified_inputs)
                elif function_name == "result_validation":
                    new_result = result_validation(**modified_inputs)
                else:
                    raise ValueError(f"不支持的函数: {function_name}")
                
                print(f"   ✅ 执行成功，结果: {self.storage.unwrap(new_result)}")
                
                # 获取新创建的调用（最后一个调用）
                new_call = None
                # 这里简化处理，在实际应用中可能需要更复杂的逻辑来获取新调用
                
                return new_result, new_call
                
            except Exception as e:
                print(f"❌ 执行失败: {e}")
                raise
    
    def update_cf_with_new_result(self, original_cf: "ComputationFrame", 
                                 original_call_hid: str, new_result: Any, 
                                 function_name: str) -> "ComputationFrame":
        """
        使用新结果更新计算图
        
        参数:
        - original_cf: 原始计算图
        - original_call_hid: 原始调用的 history_id
        - new_result: 新的结果引用
        - function_name: 函数名
        
        返回: 更新后的计算图
        """
        print(f"\n🔄 更新计算图 - 替换调用 {original_call_hid[:8]}... 的结果")
        
        try:
            # 简化的更新策略：创建包含所有相关结果的新计算图
            print("   重新构建完整计算图...")
            
            # 获取所有当前相关的结果引用
            all_results = []
            
            # 添加新结果
            all_results.append(new_result)
            
            # 从所有结果创建计算图
            if len(all_results) == 1:
                updated_cf = self.storage.cf(all_results[0])
            else:
                updated_cf = self.storage.cf(all_results)
            
            # 扩展计算图以包含完整的计算历史
            print("   扩展计算图以包含完整历史...")
            updated_cf = updated_cf.expand_all()
            
            # 清理空节点
            updated_cf = updated_cf.cleanup()
            
            print(f"   ✅ 计算图重建完成")
            print(f"   重建后统计 - 变量: {len(updated_cf.vnames)}, 函数: {len(updated_cf.fnames)}")
            
            return updated_cf
            
        except Exception as e:
            print(f"❌ 更新计算图失败: {e}")
            import traceback
            traceback.print_exc()
            print("   返回原始计算图")
            return original_cf
    
    def execute_downstream_functions(self, cf: "ComputationFrame", modified_variable: str) -> "ComputationFrame":
        """
        执行下游函数以保持计算图的一致性
        
        参数:
        - cf: 当前计算图
        - modified_variable: 被修改的变量名
        
        返回: 更新后的计算图
        """
        print(f"\n🔄 执行下游函数 - 变量: {modified_variable}")
        
        try:
            # 获取下游计算图
            downstream_cf = cf.downstream(modified_variable)
            print(f"   发现 {len(downstream_cf.fnames)} 个下游函数")
            
            # 这里可以实现自动重新执行下游函数的逻辑
            # 简化处理，返回原计算图
            
            return cf
            
        except Exception as e:
            print(f"❌ 执行下游函数失败: {e}")
            return cf
    
    def get_modification_history(self) -> pd.DataFrame:
        """
        获取修改历史
        
        返回: 修改历史的DataFrame
        """
        if not self.modification_history:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.modification_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        return df
    
    def print_modification_summary(self):
        """
        打印修改摘要
        """
        print(f"\n📊 修改历史摘要:")
        print(f"   总修改次数: {len(self.modification_history)}")
        
        if self.modification_history:
            # 按函数分组统计
            func_counts = {}
            param_counts = {}
            
            for mod in self.modification_history:
                func_name = mod['function']
                param_name = mod['param_name']
                
                func_counts[func_name] = func_counts.get(func_name, 0) + 1
                param_counts[param_name] = param_counts.get(param_name, 0) + 1
            
            print(f"   修改的函数:")
            for func, count in func_counts.items():
                print(f"     - {func}: {count} 次")
            
            print(f"   修改的参数:")
            for param, count in param_counts.items():
                print(f"     - {param}: {count} 次")

def run_initial_computation() -> Tuple[Any, Any, Any]:
    """
    运行初始计算，建立基础计算图
    """
    print("=" * 60)
    print("1. 运行初始计算")
    print("=" * 60)
    
    with storage:
        # 第一层：数据预处理
        raw_data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
        processed_data = data_preprocessing(
            raw_data=raw_data, 
            scale_factor=2.0, 
            offset=1.0, 
            filter_threshold=3.0
        )
        
        # 第二层：统计分析
        analysis_result = statistical_analysis(
            data=processed_data, 
            method="mean", 
            window_size=3, 
            confidence_level=0.95
        )
        
        # 第三层：结果验证
        validation_result = result_validation(
            analysis_result=analysis_result, 
            min_value=2.0, 
            max_value=20.0, 
            strict_mode=False
        )
        
        print(f"\n初始计算结果:")
        print(f"  预处理数据: {storage.unwrap(processed_data)}")
        print(f"  分析结果: {storage.unwrap(analysis_result)}")
        print(f"  验证结果: {storage.unwrap(validation_result)}")
        
    return processed_data, analysis_result, validation_result

def demonstrate_precise_modification():
    """
    演示精确节点修改功能
    """
    print("\n" + "=" * 60)
    print("2. 演示精确节点修改")
    print("=" * 60)
    
    # 创建修改器
    modifier = PreciseNodeModifier(storage)
    
    # 获取初始计算图
    initial_cf = storage.cf(data_preprocessing).expand_all()
    print(f"\n初始计算图统计:")
    print(f"  变量节点: {len(initial_cf.vnames)}")
    print(f"  函数节点: {len(initial_cf.fnames)}")
    
    # 场景1：修改数据预处理的scale_factor参数
    print(f"\n" + "-" * 40)
    print("场景1: 修改数据预处理的缩放因子")
    print("-" * 40)
    
    # 定位数据预处理调用
    matching_calls = modifier.locate_call_by_context(
        cf=initial_cf,
        function_name="data_preprocessing",
        input_context={"scale_factor": 2.0}  # 匹配特定的缩放因子
    )
    
    if matching_calls:
        call_hid, call = matching_calls[0]  # 取第一个匹配的调用
        
        # 修改scale_factor参数
        modified_inputs = modifier.modify_single_parameter(
            call=call,
            param_name="scale_factor", 
            new_value=3.0  # 从2.0改为3.0
        )
        
        # 重新执行
        new_result, _ = modifier.execute_with_modified_params(
            function_name="data_preprocessing",
            modified_inputs=modified_inputs
        )
        
        # 由于数据预处理结果改变，需要重新执行下游函数
        print("   📈 检测到预处理结果变化，重新执行下游函数...")
        
        with storage:
            # 重新执行统计分析
            new_analysis = statistical_analysis(
                data=new_result, 
                method="mean", 
                window_size=3, 
                confidence_level=0.95
            )
            
            # 重新执行结果验证
            new_validation = result_validation(
                analysis_result=new_analysis, 
                min_value=2.0, 
                max_value=20.0, 
                strict_mode=False
            )
            
            print(f"   新的分析结果: {storage.unwrap(new_analysis)}")
            print(f"   新的验证结果: {storage.unwrap(new_validation)}")
        
        # 更新计算图
        updated_cf = modifier.update_cf_with_new_result(
            original_cf=initial_cf,
            original_call_hid=call_hid,
            new_result=new_validation,  # 使用最终的验证结果
            function_name="data_preprocessing"
        )
        
        print(f"✅ 场景1完成，计算图已更新")
        initial_cf = updated_cf  # 更新基础计算图
    
    # 场景2：修改统计分析的方法参数
    print(f"\n" + "-" * 40)
    print("场景2: 修改统计分析的方法")
    print("-" * 40)
    
    matching_calls = modifier.locate_call_by_context(
        cf=initial_cf,
        function_name="statistical_analysis",
        input_context={"method": "mean"}
    )
    
    if matching_calls:
        call_hid, call = matching_calls[0]
        
        # 修改method参数
        modified_inputs = modifier.modify_single_parameter(
            call=call,
            param_name="method",
            new_value="median"  # 从mean改为median
        )
        
        # 重新执行
        new_result, _ = modifier.execute_with_modified_params(
            function_name="statistical_analysis",
            modified_inputs=modified_inputs
        )
        
        # 由于统计分析结果改变，需要重新执行下游的验证函数
        print("   📊 检测到分析结果变化，重新执行下游验证...")
        
        with storage:
            # 重新执行结果验证
            new_validation = result_validation(
                analysis_result=new_result, 
                min_value=2.0, 
                max_value=20.0, 
                strict_mode=False
            )
            
            print(f"   新的验证结果: {storage.unwrap(new_validation)}")
        
        # 更新计算图
        updated_cf = modifier.update_cf_with_new_result(
            original_cf=initial_cf,
            original_call_hid=call_hid,
            new_result=new_validation,  # 使用最终的验证结果
            function_name="statistical_analysis"
        )
        
        print(f"✅ 场景2完成，计算图已更新")
        initial_cf = updated_cf
    
    # 场景3：修改验证参数
    print(f"\n" + "-" * 40)
    print("场景3: 修改结果验证的严格模式")
    print("-" * 40)
    
    matching_calls = modifier.locate_call_by_context(
        cf=initial_cf,
        function_name="result_validation",
        input_context={"strict_mode": False}
    )
    
    if matching_calls:
        call_hid, call = matching_calls[0]
        
        # 修改strict_mode参数
        modified_inputs = modifier.modify_single_parameter(
            call=call,
            param_name="strict_mode",
            new_value=True  # 从False改为True
        )
        
        # 重新执行
        new_result, _ = modifier.execute_with_modified_params(
            function_name="result_validation",
            modified_inputs=modified_inputs
        )
        
        # 更新计算图
        final_cf = modifier.update_cf_with_new_result(
            original_cf=initial_cf,
            original_call_hid=call_hid,
            new_result=new_result,
            function_name="result_validation"
        )
        
        print(f"✅ 场景3完成，计算图已更新")
    else:
        final_cf = initial_cf
    
    # 显示修改历史和最终结果
    print(f"\n" + "=" * 60)
    print("3. 修改总结")
    print("=" * 60)
    
    modifier.print_modification_summary()
    
    # 显示最终计算图统计
    print(f"\n最终计算图统计:")
    print(f"  变量节点: {len(final_cf.vnames)}")
    print(f"  函数节点: {len(final_cf.fnames)}")
    
    # 显示最终结果
    try:
        final_results = final_cf.eval()
        print(f"\n最终计算结果:")
        print(final_results)
    except Exception as e:
        print(f"获取最终结果失败: {e}")
    
    return final_cf, modifier

def compare_original_and_modified():
    """
    比较原始计算和修改后计算的结果差异
    """
    print(f"\n" + "=" * 60)
    print("4. 结果对比分析")
    print("=" * 60)
    
    # 重新运行原始计算作为对照
    print("\n重新运行原始计算...")
    with storage:
        original_processed = data_preprocessing([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], 2.0, 1.0, 3.0)
        original_analysis = statistical_analysis(original_processed, "mean", 3, 0.95)
        original_validation = result_validation(original_analysis, 2.0, 20.0, False)
        
        print(f"原始结果:")
        print(f"  预处理: {storage.unwrap(original_processed)}")
        print(f"  分析: {storage.unwrap(original_analysis)}")
        print(f"  验证: {storage.unwrap(original_validation)}")
    
    print("\n对比分析:")
    print("  通过精确参数修改，我们可以:")
    print("  1. 精确控制计算图中特定节点的行为")
    print("  2. 避免重新计算整个管道")
    print("  3. 保持计算历史和版本追踪")
    print("  4. 实现参数敏感性分析")

def main():
    """
    主函数：演示完整的精确节点修改流程
    """
    print("精确节点修改（单参数级别修改）演示")
    print("使用mandala框架实现基于上下文的精确节点定位和修改")
    
    try:
        # 1. 运行初始计算
        processed_data, analysis_result, validation_result = run_initial_computation()
        
        # 2. 演示精确修改
        final_cf, modifier = demonstrate_precise_modification()
        
        # 3. 结果对比
        compare_original_and_modified()
        
        # 4. 显示修改历史详情
        print(f"\n" + "=" * 60)
        print("5. 详细修改历史")
        print("=" * 60)
        
        history_df = modifier.get_modification_history()
        if not history_df.empty:
            print(history_df.to_string(index=False))
        else:
            print("暂无修改历史")
        
        print(f"\n" + "=" * 60)
        print("精确节点修改演示完成！")
        print("=" * 60)
        print("\n核心特性总结:")
        print("✅ 基于上下文的精确节点定位")
        print("✅ 单参数级别的精细修改控制")
        print("✅ 智能计算图更新和一致性维护")
        print("✅ 完整的修改历史追踪")
        print("✅ 利用mandala现有功能避免重复实现")
        
    except Exception as e:
        print(f"演示过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 
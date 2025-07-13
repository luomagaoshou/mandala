"""
文件: cf_node_manipulation_example.py
位置: mydemo/案例/
目的: 综合演示 ComputationFrame 的节点遍历、操作和可视化功能

功能特性:
1. 封装的 @op 和 @track 函数管理
2. ComputationFrame 的深度遍历和分析
3. 节点信息的提取和更新
4. SVG 图形的生成和可视化
5. 节点替换和图形重构的实际应用

本示例整合了之前所有的功能，提供了一个完整的节点操作工作流。
"""

from mandala1.imports import Storage, op, track
import time
import pandas as pd
import hashlib
from pathlib import Path

class ComputationFrameManager:
    """ComputationFrame 管理器类，封装所有相关操作"""
    
    def __init__(self, storage_path=None):
        """初始化管理器
        
        参数:
            storage_path: 存储路径，默认使用内存存储
        """
        self.storage = Storage(storage_path) if storage_path else Storage()
        self.svg_output_dir = Path("mydemo/svg")
        self.svg_output_dir.mkdir(exist_ok=True)
    
    def create_computation_history(self):
        """创建一个复杂的计算历史用于演示"""
        print("创建计算历史...")
        
        # 定义基础计算函数
        @track
        def get_multiplier(base: int = 10) -> int:
            """获取乘数配置"""
            return base + 5
        
        @op
        def process_numbers(numbers: list, operation: str = "multiply") -> list:
            """处理数字列表"""
            multiplier = get_multiplier()
            if operation == "multiply":
                return [x * multiplier for x in numbers]
            elif operation == "square":
                return [x ** 2 for x in numbers]
            else:
                return [x + multiplier for x in numbers]
        
        @op
        def aggregate_results(data: list, method: str = "sum") -> float:
            """聚合计算结果"""
            if method == "sum":
                return sum(data)
            elif method == "mean":
                return sum(data) / len(data)
            else:
                return max(data)
        
        @op
        def final_computation(value: float, factor: int = 2) -> dict:
            """最终计算步骤"""
            return {
                "result": value * factor,
                "metadata": {"processed_at": time.time(), "factor": factor}
            }
        
        # 存储函数引用以便后续使用
        self.get_multiplier = get_multiplier
        self.process_numbers = process_numbers
        self.aggregate_results = aggregate_results
        self.final_computation = final_computation
        
        # 执行计算创建历史
        with self.storage:
            # 创建多个计算分支
            inputs = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
            operations = ["multiply", "square", "add"]
            
            results = []
            for i, (input_data, operation) in enumerate(zip(inputs, operations)):
                processed = process_numbers(input_data, operation=operation)
                aggregated = aggregate_results(processed, method="sum" if i % 2 == 0 else "mean")
                final = final_computation(aggregated, factor=i + 1)
                results.append(final)
            
            # 创建一个综合结果
            all_values = [aggregate_results([1, 2, 3, 4, 5], method="max")]
            comprehensive_result = final_computation(all_values[0], factor=10)
            
        self.computation_results = results + [comprehensive_result]
        print(f"创建了 {len(self.computation_results)} 个计算结果")
        
        return self.computation_results
    
    def traverse_computation_frame(self, cf, detailed=True):
        """遍历 ComputationFrame 并提取详细信息
        
        参数:
            cf: ComputationFrame 对象
            detailed: 是否提取详细信息
        
        返回:
            包含节点信息的字典
        """
        print("\n=== 遍历 ComputationFrame ===")
        
        # 基本信息
        info = {
            "function_names": list(cf.fnames),
            "variable_names": list(cf.vnames),
            "all_nodes": list(cf.fnames | cf.vnames),
            "node_count": len(cf.fnames | cf.vnames)
        }
        
        print(f"函数节点数: {len(cf.fnames)}")
        print(f"变量节点数: {len(cf.vnames)}")
        print(f"总节点数: {info['node_count']}")
        
        if detailed:
            # 详细分析每个函数节点
            function_details = {}
            for fname in cf.fnames:
                try:
                    func_table = cf.get_func_table(fname)
                    function_details[fname] = {
                        "call_count": len(func_table),
                        "columns": list(func_table.columns),
                        "sample_data": func_table.head(3).to_dict() if not func_table.empty else {}
                    }
                    print(f"\n函数 '{fname}' 的调用信息:")
                    print(f"  调用次数: {len(func_table)}")
                    print(f"  参数列: {list(func_table.columns)}")
                except Exception as e:
                    print(f"  获取函数 '{fname}' 信息失败: {e}")
                    function_details[fname] = {"error": str(e)}
            
            info["function_details"] = function_details
            
            # 变量引用信息
            try:
                var_refs = cf.refs_by_var()
                variable_details = {}
                for vname, refs in var_refs.items():
                    if isinstance(refs, list):
                        variable_details[vname] = {
                            "ref_count": len(refs),
                            "sample_values": [self.storage.unwrap(ref) for ref in refs[:3]]
                        }
                    else:
                        variable_details[vname] = {
                            "ref_count": 1,
                            "sample_values": [self.storage.unwrap(refs)]
                        }
                
                info["variable_details"] = variable_details
                
                print(f"\n变量引用信息:")
                for vname, details in variable_details.items():
                    print(f"  {vname}: {details['ref_count']} 个引用")
                    
            except Exception as e:
                print(f"获取变量引用信息失败: {e}")
        
        return info
    
    def traverse_cf_hierarchical(self, cf, show_details=True):
        """按照调用顺序与层级遍历 ComputationFrame
        
        参数:
            cf: ComputationFrame 对象
            show_details: 是否显示详细信息
        
        返回:
            层级结构信息字典
        """
        print("\n=== 按层级和调用顺序遍历 ComputationFrame ===")
        
        # 获取所有函数的调用表
        func_call_info = {}
        for fname in cf.fnames:
            try:
                func_table = cf.get_func_table(fname)
                if not func_table.empty:
                    func_call_info[fname] = {
                        "table": func_table,
                        "call_count": len(func_table)
                    }
            except Exception as e:
                print(f"获取函数 '{fname}' 调用表失败: {e}")
        
        # 分析依赖关系构建层级结构
        hierarchy = self._build_dependency_hierarchy(cf, func_call_info)
        
        # 按层级打印
        self._print_hierarchy(hierarchy, show_details)
        
        return hierarchy
    
    def _build_dependency_hierarchy(self, cf, func_call_info):
        """构建依赖关系层级结构"""
        hierarchy = {
            "levels": [],
            "dependencies": {},
            "call_order": []
        }
        
        try:
            # 获取变量引用关系
            var_refs = cf.refs_by_var()
            
            # 分析每个函数的输入输出依赖
            func_dependencies = {}
            func_outputs = {}
            
            for fname, info in func_call_info.items():
                table = info["table"]
                
                # 分析函数的输入参数（依赖）
                input_vars = []
                for col in table.columns:
                    if col.startswith('input_') or col in var_refs:
                        input_vars.append(col)
                
                # 分析函数的输出（产生的变量）
                output_vars = []
                for col in table.columns:
                    if col.startswith('output_'):
                        output_vars.append(col)
                
                func_dependencies[fname] = {
                    "inputs": input_vars,
                    "outputs": output_vars,
                    "calls": []
                }
                
                # 记录每次调用的详细信息
                for idx, row in table.iterrows():
                    call_info = {
                        "call_id": idx,
                        "inputs": {},
                        "outputs": {},
                        "timestamp": getattr(row, 'timestamp', None)
                    }
                    
                    # 提取输入参数值
                    for col in input_vars:
                        if col in row:
                            try:
                                call_info["inputs"][col] = self.storage.unwrap(row[col]) if hasattr(row[col], '__call__') else row[col]
                            except:
                                call_info["inputs"][col] = str(row[col])
                    
                    # 提取输出值
                    for col in output_vars:
                        if col in row:
                            try:
                                call_info["outputs"][col] = self.storage.unwrap(row[col]) if hasattr(row[col], '__call__') else row[col]
                            except:
                                call_info["outputs"][col] = str(row[col])
                    
                    func_dependencies[fname]["calls"].append(call_info)
            
            # 基于依赖关系构建层级
            levels = self._compute_dependency_levels(func_dependencies)
            
            hierarchy["levels"] = levels
            hierarchy["dependencies"] = func_dependencies
            hierarchy["call_order"] = self._compute_call_order(func_dependencies)
            
        except Exception as e:
            print(f"构建层级结构失败: {e}")
            hierarchy["error"] = str(e)
        
        return hierarchy
    
    def _compute_dependency_levels(self, func_dependencies):
        """计算函数的依赖层级"""
        levels = []
        remaining_funcs = set(func_dependencies.keys())
        current_level = 0
        
        while remaining_funcs:
            current_level_funcs = []
            
            for fname in list(remaining_funcs):
                # 检查是否所有依赖都已在前面的层级中
                dependencies_satisfied = True
                for input_var in func_dependencies[fname]["inputs"]:
                    # 检查是否有其他函数产生这个输入变量
                    has_producer = False
                    for other_fname in func_dependencies:
                        if other_fname != fname and input_var in func_dependencies[other_fname]["outputs"]:
                            if other_fname in remaining_funcs:
                                dependencies_satisfied = False
                                break
                            has_producer = True
                    
                    if not dependencies_satisfied:
                        break
                
                if dependencies_satisfied:
                    current_level_funcs.append(fname)
            
            if not current_level_funcs:
                # 如果没有找到可以放在当前层级的函数，说明有循环依赖或其他问题
                # 将剩余的函数都放在当前层级
                current_level_funcs = list(remaining_funcs)
            
            levels.append({
                "level": current_level,
                "functions": current_level_funcs
            })
            
            for fname in current_level_funcs:
                remaining_funcs.remove(fname)
            
            current_level += 1
            
            # 防止无限循环
            if current_level > 10:
                break
        
        return levels
    
    def _compute_call_order(self, func_dependencies):
        """计算函数调用的时间顺序"""
        call_order = []
        
        for fname, info in func_dependencies.items():
            for call in info["calls"]:
                call_order.append({
                    "function": fname,
                    "call_id": call["call_id"],
                    "timestamp": call.get("timestamp"),
                    "inputs": call["inputs"],
                    "outputs": call["outputs"]
                })
        
        # 如果有时间戳，按时间排序；否则按函数名和调用ID排序
        if any(call.get("timestamp") for call in call_order):
            call_order.sort(key=lambda x: x.get("timestamp", 0))
        else:
            call_order.sort(key=lambda x: (x["function"], x["call_id"]))
        
        return call_order
    
    def _print_hierarchy(self, hierarchy, show_details):
        """打印层级结构"""
        if "error" in hierarchy:
            print(f"❌ 层级分析失败: {hierarchy['error']}")
            return
        
        print(f"📊 计算图层级结构:")
        print(f"   总层级数: {len(hierarchy['levels'])}")
        print(f"   总调用次数: {len(hierarchy['call_order'])}")
        
        # 打印每个层级
        for level_info in hierarchy["levels"]:
            level = level_info["level"]
            functions = level_info["functions"]
            
            print(f"\n🔹 层级 {level} ({len(functions)} 个函数):")
            
            for fname in functions:
                if fname in hierarchy["dependencies"]:
                    func_info = hierarchy["dependencies"][fname]
                    call_count = len(func_info["calls"])
                    
                    print(f"   📋 {fname}: {call_count} 次调用")
                    
                    if show_details:
                        # 显示输入输出依赖
                        if func_info["inputs"]:
                            print(f"      ⬇️  输入: {', '.join(func_info['inputs'])}")
                        if func_info["outputs"]:
                            print(f"      ⬆️  输出: {', '.join(func_info['outputs'])}")
                        
                        # 显示前几次调用的详细信息
                        for i, call in enumerate(func_info["calls"][:3]):  # 只显示前3次
                            print(f"      📞 调用 {i+1}:")
                            if call["inputs"]:
                                print(f"         输入: {self._format_call_data(call['inputs'])}")
                            if call["outputs"]:
                                print(f"         输出: {self._format_call_data(call['outputs'])}")
                        
                        if len(func_info["calls"]) > 3:
                            print(f"      ... 还有 {len(func_info['calls']) - 3} 次调用")
        
        # 打印调用时间顺序
        if show_details and hierarchy["call_order"]:
            print(f"\n🕐 调用时间顺序:")
            for i, call in enumerate(hierarchy["call_order"][:10]):  # 只显示前10次
                print(f"   {i+1:2d}. {call['function']} (调用ID: {call['call_id']})")
                if call["inputs"]:
                    print(f"       输入: {self._format_call_data(call['inputs'])}")
            
            if len(hierarchy["call_order"]) > 10:
                print(f"   ... 还有 {len(hierarchy['call_order']) - 10} 次调用")
    
    def _format_call_data(self, data):
        """格式化调用数据以便显示"""
        if not data:
            return "无"
        
        formatted = []
        for key, value in data.items():
            if isinstance(value, (list, tuple)):
                if len(value) <= 3:
                    formatted.append(f"{key}={value}")
                else:
                    formatted.append(f"{key}=[{len(value)} 个元素]")
            elif isinstance(value, dict):
                formatted.append(f"{key}={{dict: {len(value)} 个键}}")
            elif isinstance(value, str) and len(value) > 20:
                formatted.append(f"{key}={value[:20]}...")
            else:
                formatted.append(f"{key}={value}")
        
        return ", ".join(formatted)
    
    def generate_svg_visualization(self, cf, filename, verbose=True):
        """生成 ComputationFrame 的 SVG 可视化
        
        参数:
            cf: ComputationFrame 对象
            filename: 输出文件名
            verbose: 是否显示详细信息
        
        返回:
            生成的 SVG 文件路径
        """
        svg_path = self.svg_output_dir / filename
        
        try:
            cf.draw(verbose=verbose, path=str(svg_path))
            print(f"SVG 图形已保存到: {svg_path}")
            return svg_path
        except Exception as e:
            print(f"生成 SVG 失败: {e}")
            return None
    
    def update_node_and_regenerate(self, original_cf, update_strategy="version_control"):
        """更新节点并重新生成计算图
        
        参数:
            original_cf: 原始的 ComputationFrame
            update_strategy: 更新策略 ("version_control", "parameter_hash", "logic_branch")
        
        返回:
            更新后的 ComputationFrame 和相关信息
        """
        print(f"\n=== 使用 '{update_strategy}' 策略更新节点 ===")
        
        if update_strategy == "version_control":
            return self._update_with_version_control()
        elif update_strategy == "parameter_hash":
            return self._update_with_parameter_hash()
        elif update_strategy == "logic_branch":
            return self._update_with_logic_branch()
        else:
            raise ValueError(f"未知的更新策略: {update_strategy}")
    
    def _update_with_version_control(self):
        """使用版本控制策略更新节点"""
        
        @op
        def enhanced_process_numbers(numbers: list, operation: str = "multiply", version: str = "v2") -> list:
            """增强版的数字处理函数"""
            multiplier = self.get_multiplier()
            
            if operation == "multiply":
                return [x * multiplier * 2 for x in numbers]  # 增强逻辑
            elif operation == "square":
                return [(x ** 2) + multiplier for x in numbers]  # 混合操作
            else:
                return [x + multiplier + len(numbers) for x in numbers]  # 考虑列表长度
        
        # 执行新版本的计算
        with self.storage:
            updated_results = []
            for i, input_data in enumerate([[1, 2, 3], [10, 20, 30]]):
                processed = enhanced_process_numbers(input_data, operation="multiply", version=f"v2_{i}")
                aggregated = self.aggregate_results(processed, method="sum")
                final = self.final_computation(aggregated, factor=5)
                updated_results.append(final)
        
        # 获取更新后的 ComputationFrame
        updated_cf = self.storage.cf(enhanced_process_numbers).expand_all()
        
        return updated_cf, updated_results, "version_control"
    
    def _update_with_parameter_hash(self):
        """使用参数哈希策略更新节点"""
        
        def get_param_hash(data):
            """生成参数哈希"""
            return hashlib.md5(str(data).encode()).hexdigest()[:8]
        
        @op
        def hash_controlled_computation(data: list, param_hash: str = None, force_update: bool = False) -> dict:
            """基于哈希控制的计算函数"""
            if param_hash is None:
                param_hash = get_param_hash(data)
            
            if force_update:
                param_hash = f"updated_{param_hash}"
            
            multiplier = self.get_multiplier()
            processed = [x * multiplier for x in data]
            
            return {
                "data": processed,
                "hash": param_hash,
                "sum": sum(processed),
                "updated": force_update
            }
        
        # 执行哈希控制的计算
        with self.storage:
            test_data = [1, 2, 3, 4, 5]
            
            # 原始计算
            original = hash_controlled_computation(test_data)
            
            # 强制更新的计算
            updated = hash_controlled_computation(test_data, force_update=True)
            
            # 不同数据的计算
            different = hash_controlled_computation([10, 20, 30])
        
        updated_cf = self.storage.cf(hash_controlled_computation).expand_all()
        
        return updated_cf, [original, updated, different], "parameter_hash"
    
    def _update_with_logic_branch(self):
        """使用逻辑分支策略更新节点"""
        
        @op
        def branching_computation(data: list, branch: str = "standard", enhancement_level: int = 1) -> dict:
            """分支计算函数"""
            multiplier = self.get_multiplier()
            
            if branch == "standard":
                result = [x * multiplier for x in data]
            elif branch == "enhanced":
                result = [x * multiplier * enhancement_level + x for x in data]
            elif branch == "experimental":
                result = [x ** 2 + multiplier * enhancement_level for x in data]
            else:
                result = [x + multiplier for x in data]
            
            return {
                "result": result,
                "branch": branch,
                "enhancement_level": enhancement_level,
                "total": sum(result)
            }
        
        # 执行不同分支的计算
        with self.storage:
            branches = ["standard", "enhanced", "experimental"]
            branch_results = []
            
            for branch in branches:
                for level in [1, 2, 3]:
                    result = branching_computation([1, 2, 3, 4], branch=branch, enhancement_level=level)
                    branch_results.append(result)
        
        updated_cf = self.storage.cf(branching_computation).expand_all()
        
        return updated_cf, branch_results, "logic_branch"
    
    def comprehensive_analysis(self):
        """进行全面的 ComputationFrame 分析"""
        print("\n" + "="*60)
        print("综合 ComputationFrame 分析")
        print("="*60)
        
        # 1. 创建计算历史
        results = self.create_computation_history()
        
        # 2. 分析原始计算框架
        print("\n--- 原始计算框架分析 ---")
        original_cf = self.storage.cf(self.final_computation).expand_all()
        original_info = self.traverse_computation_frame(original_cf)
        
        # 2.1 按层级和调用顺序分析
        print("\n--- 层级和调用顺序分析 ---")
        hierarchy_info = self.traverse_cf_hierarchical(original_cf, show_details=True)
        
        # 3. 生成原始 SVG
        original_svg = self.generate_svg_visualization(
            original_cf, 
            "original_computation_graph.svg"
        )
        
        # 4. 测试不同的更新策略
        strategies = ["version_control", "parameter_hash", "logic_branch"]
        
        for strategy in strategies:
            print(f"\n--- {strategy.upper()} 策略测试 ---")
            
            try:
                updated_cf, updated_results, strategy_name = self.update_node_and_regenerate(
                    original_cf, 
                    update_strategy=strategy
                )
                
                # 分析更新后的计算框架
                updated_info = self.traverse_computation_frame(updated_cf, detailed=False)
                
                # 生成更新后的 SVG
                updated_svg = self.generate_svg_visualization(
                    updated_cf,
                    f"updated_{strategy}_computation_graph.svg"
                )
                
                print(f"策略 '{strategy}' 执行成功:")
                print(f"  新增节点数: {updated_info['node_count']}")
                print(f"  生成结果数: {len(updated_results)}")
                
            except Exception as e:
                print(f"策略 '{strategy}' 执行失败: {e}")
        
        # 5. 创建组合视图
        print("\n--- 创建组合计算框架 ---")
        try:
            # 获取所有函数的计算框架并组合
            all_functions = [self.process_numbers, self.aggregate_results, self.final_computation]
            combined_cf = None
            
            for func in all_functions:
                func_cf = self.storage.cf(func)
                if combined_cf is None:
                    combined_cf = func_cf
                else:
                    try:
                        combined_cf = combined_cf.union(func_cf)
                    except:
                        # 如果无法合并，则扩展现有的框架
                        combined_cf = combined_cf.expand_all()
                        break
            
            if combined_cf:
                combined_cf = combined_cf.expand_all()
                combined_info = self.traverse_computation_frame(combined_cf, detailed=False)
                combined_svg = self.generate_svg_visualization(
                    combined_cf,
                    "combined_computation_graph.svg"
                )
                print(f"组合计算框架创建成功，包含 {combined_info['node_count']} 个节点")
            
        except Exception as e:
            print(f"创建组合计算框架失败: {e}")
        
        print("\n" + "="*60)
        print("分析完成！请查看 mydemo/svg/ 目录下的 SVG 文件")
        print("="*60)

def main():
    """主函数"""
    print("ComputationFrame 节点操作综合示例")
    print("="*50)
    
    # 创建管理器实例
    manager = ComputationFrameManager()
    
    # 执行综合分析
    manager.comprehensive_analysis()

if __name__ == "__main__":
    main() 
"""
文件: test_hierarchical_traverse.py
位置: mydemo/案例/
目的: 测试新实现的层级遍历功能

这个脚本专门用于测试和演示 traverse_cf_hierarchical 方法的功能。
"""

from cf_node_manipulation_example import ComputationFrameManager
from mandala1.imports import Storage, op, track

def create_simple_computation_chain():
    """创建一个简单的计算链用于测试层级遍历"""
    print("🔧 创建简单的计算链...")
    
    storage = Storage()
    
    @track
    def get_config() -> dict:
        """获取配置信息"""
        return {"multiplier": 10, "offset": 5}
    
    @op
    def step1_process(data: list) -> list:
        """第一步：基础处理"""
        config = get_config()
        return [x * config["multiplier"] for x in data]
    
    @op
    def step2_transform(processed_data: list) -> list:
        """第二步：数据转换"""
        config = get_config()
        return [x + config["offset"] for x in processed_data]
    
    @op
    def step3_aggregate(transformed_data: list) -> dict:
        """第三步：聚合结果"""
        return {
            "sum": sum(transformed_data),
            "count": len(transformed_data),
            "avg": sum(transformed_data) / len(transformed_data)
        }
    
    @op
    def step4_finalize(aggregated: dict, metadata: str = "test") -> dict:
        """第四步：最终处理"""
        return {
            "result": aggregated,
            "metadata": metadata,
            "status": "completed"
        }
    
    # 执行计算链
    with storage:
        # 创建多个计算分支
        test_datasets = [
            [1, 2, 3],
            [4, 5, 6, 7],
            [8, 9]
        ]
        
        results = []
        for i, dataset in enumerate(test_datasets):
            # 按顺序执行计算链
            processed = step1_process(dataset)
            transformed = step2_transform(processed)
            aggregated = step3_aggregate(transformed)
            final = step4_finalize(aggregated, metadata=f"dataset_{i}")
            results.append(final)
    
    return storage, step4_finalize, results

def test_hierarchical_traverse():
    """测试层级遍历功能"""
    print("🚀 测试层级遍历功能")
    print("=" * 50)
    
    # 创建计算历史
    storage, final_func, results = create_simple_computation_chain()
    
    # 创建 ComputationFrameManager 实例
    manager = ComputationFrameManager()
    manager.storage = storage  # 使用我们创建的存储
    
    # 获取完整的计算框架
    cf = storage.cf(final_func).expand_all()
    
    print(f"✅ 创建了 {len(results)} 个计算结果")
    print(f"📊 计算框架包含 {len(cf.fnames)} 个函数节点和 {len(cf.vnames)} 个变量节点")
    
    # 使用新的层级遍历方法
    print("\n" + "="*60)
    hierarchy_info = manager.traverse_cf_hierarchical(cf, show_details=True)
    print("="*60)
    
    # 生成 SVG 可视化
    svg_path = manager.generate_svg_visualization(cf, "hierarchical_test.svg")
    
    return hierarchy_info

def test_complex_dependencies():
    """测试复杂依赖关系的层级遍历"""
    print("\n🔬 测试复杂依赖关系")
    print("=" * 50)
    
    storage = Storage()
    
    @track
    def get_params() -> dict:
        return {"factor": 2, "threshold": 10}
    
    @op
    def branch_a(data: list) -> list:
        """分支A处理"""
        params = get_params()
        return [x * params["factor"] for x in data]
    
    @op
    def branch_b(data: list) -> list:
        """分支B处理"""
        params = get_params()
        return [x + params["threshold"] for x in data]
    
    @op
    def merge_branches(data_a: list, data_b: list) -> list:
        """合并分支结果"""
        return data_a + data_b
    
    @op
    def final_process(merged_data: list, mode: str = "standard") -> dict:
        """最终处理"""
        if mode == "standard":
            result = sum(merged_data)
        else:
            result = max(merged_data)
        
        return {
            "result": result,
            "mode": mode,
            "count": len(merged_data)
        }
    
    # 执行复杂的计算图
    with storage:
        input_data = [1, 2, 3, 4, 5]
        
        # 并行分支
        result_a = branch_a(input_data)
        result_b = branch_b(input_data)
        
        # 合并结果
        merged = merge_branches(result_a, result_b)
        
        # 不同模式的最终处理
        final_standard = final_process(merged, mode="standard")
        final_max = final_process(merged, mode="max")
    
    # 分析复杂依赖
    manager = ComputationFrameManager()
    manager.storage = storage
    
    cf = storage.cf(final_process).expand_all()
    
    print(f"📊 复杂计算框架包含 {len(cf.fnames)} 个函数节点和 {len(cf.vnames)} 个变量节点")
    
    # 层级遍历分析
    hierarchy_info = manager.traverse_cf_hierarchical(cf, show_details=True)
    
    # 生成可视化
    manager.generate_svg_visualization(cf, "complex_dependencies_test.svg")
    
    return hierarchy_info

def main():
    """主函数"""
    print("🧪 ComputationFrame 层级遍历测试")
    print("=" * 60)
    
    # 测试1：简单的计算链
    simple_hierarchy = test_hierarchical_traverse()
    
    # 测试2：复杂的依赖关系
    complex_hierarchy = test_complex_dependencies()
    
    print("\n" + "="*60)
    print("🎉 测试完成！")
    print("📁 查看生成的 SVG 文件:")
    print("   - mydemo/svg/hierarchical_test.svg")
    print("   - mydemo/svg/complex_dependencies_test.svg")
    print("="*60)

if __name__ == "__main__":
    main() 
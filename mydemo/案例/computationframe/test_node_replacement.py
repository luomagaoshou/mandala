"""
测试节点替换功能的正确性
验证所有核心功能是否按预期工作
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# 导入演示模块的函数
import importlib.util
spec = importlib.util.spec_from_file_location("node_replacement_demo", 
                                            os.path.join(os.path.dirname(__file__), "11_node_replacement_demo.py"))
node_replacement_demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(node_replacement_demo)

# 导入需要的函数
demonstrate_node_replacement = node_replacement_demo.demonstrate_node_replacement
calculate_mean = node_replacement_demo.calculate_mean
calculate_std = node_replacement_demo.calculate_std
calculate_score = node_replacement_demo.calculate_score
Storage = node_replacement_demo.Storage

def test_node_replacement_functionality():
    """测试节点替换功能"""
    print("=== 测试节点替换功能 ===\n")
    
    # 运行主要的演示功能
    results = demonstrate_node_replacement()
    
    # 验证结果
    assert 'original_score' in results, "缺少原始分数结果"
    assert 'new_score' in results, "缺少新分数结果"
    assert 'modified_score' in results, "缺少修改后分数结果"
    
    print("✅ 所有关键结果都已生成")
    
    # 验证计算框架
    assert results['original_cf'] is not None, "原始计算框架为空"
    assert results['new_cf'] is not None, "新计算框架为空"
    assert results['combined_cf'] is not None, "合并计算框架为空"
    
    print("✅ 所有计算框架都已正确创建")
    
    # 验证分数变化
    original = results['original_score']
    new = results['new_score']
    modified = results['modified_score']
    
    print(f"原始分数: {original}")
    print(f"权重修改后分数: {new}")
    print(f"数据修改后分数: {modified}")
    
    # 验证权重修改的影响
    if abs(original) > 1e-10:  # 避免除零错误
        weight_change = abs((new - original) / original)
        print(f"权重修改影响: {weight_change:.2%}")
    
    print("✅ 节点替换功能测试通过")
    
    return True

def test_computation_frame_operations():
    """测试计算框架操作"""
    print("\n=== 测试计算框架操作 ===\n")
    
    storage = Storage()
    
    # 创建测试数据
    with storage:
        test_data = [1, 2, 3, 4, 5]
        mean_result = calculate_mean(test_data)
        std_result = calculate_std(test_data)
        
        print(f"测试数据: {test_data}")
        print(f"平均值: {storage.unwrap(mean_result)}")
        print(f"标准差: {storage.unwrap(std_result)}")
    
    # 测试计算框架创建
    cf = storage.cf(mean_result)
    assert cf is not None, "计算框架创建失败"
    print("✅ 计算框架创建成功")
    
    # 测试扩展功能
    cf.expand_back(inplace=True, recursive=True)
    assert len(cf.nodes) > 0, "计算框架扩展失败"
    print(f"✅ 计算框架扩展成功，节点数: {len(cf.nodes)}")
    
    # 测试函数表获取
    if 'calculate_mean' in cf.fnames:
        func_table = cf.get_func_table('calculate_mean')
        assert func_table is not None, "函数表获取失败"
        print("✅ 函数表获取成功")
    
    # 测试调用信息获取
    calls_by_func = cf.calls_by_func()
    assert isinstance(calls_by_func, dict), "调用信息获取失败"
    print("✅ 调用信息获取成功")
    
    return True

def test_parameter_modification():
    """测试参数修改功能"""
    print("\n=== 测试参数修改功能 ===\n")
    
    storage = Storage()
    
    # 创建原始计算
    with storage:
        data = [10, 20, 30, 40, 50]
        original_score = calculate_score(data, weight=1.0)
        original_value = storage.unwrap(original_score)
        print(f"原始分数 (权重=1.0): {original_value}")
    
    # 修改参数重新计算
    with storage:
        modified_score = calculate_score(data, weight=2.0)
        modified_value = storage.unwrap(modified_score)
        print(f"修改后分数 (权重=2.0): {modified_value}")
    
    # 验证参数修改的效果
    expected_ratio = 2.0
    actual_ratio = modified_value / original_value if original_value != 0 else 0
    
    print(f"预期比例: {expected_ratio}")
    print(f"实际比例: {actual_ratio}")
    
    # 允许小的数值误差
    assert abs(actual_ratio - expected_ratio) < 0.001, "参数修改效果不正确"
    print("✅ 参数修改功能测试通过")
    
    return True

def test_computation_frame_merging():
    """测试计算框架合并功能"""
    print("\n=== 测试计算框架合并功能 ===\n")
    
    storage = Storage()
    
    # 创建两个不同的计算
    with storage:
        data1 = [1, 2, 3]
        data2 = [4, 5, 6]
        
        mean1 = calculate_mean(data1)
        mean2 = calculate_mean(data2)
    
    # 创建两个计算框架
    cf1 = storage.cf(mean1).expand_back(recursive=True)
    cf2 = storage.cf(mean2).expand_back(recursive=True)
    
    print(f"计算框架1节点数: {len(cf1.nodes)}")
    print(f"计算框架2节点数: {len(cf2.nodes)}")
    
    # 合并计算框架
    merged_cf = cf1 | cf2
    
    print(f"合并后节点数: {len(merged_cf.nodes)}")
    
    # 验证合并结果
    assert len(merged_cf.nodes) >= max(len(cf1.nodes), len(cf2.nodes)), "合并后节点数不正确"
    print("✅ 计算框架合并功能测试通过")
    
    return True

def run_all_tests():
    """运行所有测试"""
    print("开始运行所有测试...\n")
    
    tests = [
        test_node_replacement_functionality,
        test_computation_frame_operations,
        test_parameter_modification,
        test_computation_frame_merging
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"✅ {test_func.__name__} 通过\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test_func.__name__} 失败: {e}\n")
    
    print("=== 测试总结 ===")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"总计: {passed + failed}")
    
    if failed == 0:
        print("🎉 所有测试都通过了！")
    else:
        print(f"⚠️  有 {failed} 个测试失败")
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1) 
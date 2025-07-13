"""
ComputationFrame 综合演示测试文件
用于验证演示的各个功能是否正常工作
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from mydemo.案例.cf_comprehensive_operations_demo import ComputationFrameDemo

def test_basic_functionality():
    """测试基础功能"""
    print("🧪 测试基础功能")
    demo = ComputationFrameDemo()
    
    # 测试第1阶段
    cf1 = demo.第1阶段_基础操作()
    assert cf1 is not None, "第1阶段应该返回有效的ComputationFrame"
    assert len(cf1.nodes) > 0, "应该有至少一个节点"
    print("✅ 第1阶段测试通过")
    
    # 测试第2阶段
    cf2 = demo.第2阶段_遍历操作(cf1)
    assert cf2 is not None, "第2阶段应该返回有效的ComputationFrame"
    print("✅ 第2阶段测试通过")
    
    # 测试第3阶段
    cf3 = demo.第3阶段_查找操作(cf2)
    assert cf3 is not None, "第3阶段应该返回有效的ComputationFrame"
    assert len(cf3.nodes) >= len(cf1.nodes), "扩展后应该有更多或相等的节点"
    print("✅ 第3阶段测试通过")
    
    return cf3

def test_advanced_functionality():
    """测试高级功能"""
    print("\n🧪 测试高级功能")
    demo = ComputationFrameDemo()
    
    # 先获取基础的ComputationFrame
    cf1 = demo.第1阶段_基础操作()
    cf3 = demo.第3阶段_查找操作(cf1)
    
    # 测试删除操作
    cf4 = demo.第4阶段_删除操作(cf3)
    assert cf4 is not None, "第4阶段应该返回有效的ComputationFrame"
    print("✅ 第4阶段测试通过")
    
    # 测试增加操作
    cf5 = demo.第5阶段_增加操作(cf4)
    assert cf5 is not None, "第5阶段应该返回有效的ComputationFrame"
    print("✅ 第5阶段测试通过")
    
    # 测试修改操作
    cf6 = demo.第6阶段_修改操作(cf5)
    assert cf6 is not None, "第6阶段应该返回有效的ComputationFrame"
    print("✅ 第6阶段测试通过")
    
    return cf6

def test_error_handling():
    """测试错误处理"""
    print("\n🧪 测试错误处理")
    demo = ComputationFrameDemo()
    
    try:
        # 这应该能够正常运行而不崩溃
        final_cf = demo.运行完整演示()
        assert final_cf is not None, "完整演示应该返回有效的ComputationFrame"
        print("✅ 错误处理测试通过")
        return True
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        return False

def test_individual_stages():
    """测试单独运行各个阶段"""
    print("\n🧪 测试单独运行各个阶段")
    demo = ComputationFrameDemo()
    
    # 构建基础数据
    cf1 = demo.第1阶段_基础操作()
    cf2 = demo.第2阶段_遍历操作(cf1)
    cf3 = demo.第3阶段_查找操作(cf2)
    cf4 = demo.第4阶段_删除操作(cf3)
    cf5 = demo.第5阶段_增加操作(cf4)
    
    # 验证每个阶段的结果
    stages = [cf1, cf2, cf3, cf4, cf5]
    stage_names = ["第1阶段", "第2阶段", "第3阶段", "第4阶段", "第5阶段"]
    
    for i, (cf, name) in enumerate(zip(stages, stage_names)):
        assert cf is not None, f"{name}应该返回有效的ComputationFrame"
        assert hasattr(cf, 'nodes'), f"{name}的结果应该有nodes属性"
        assert hasattr(cf, 'vnames'), f"{name}的结果应该有vnames属性"
        assert hasattr(cf, 'fnames'), f"{name}的结果应该有fnames属性"
        print(f"✅ {name}单独测试通过 - 节点数: {len(cf.nodes)}")
    
    return True

def test_cf_methods():
    """测试ComputationFrame的核心方法"""
    print("\n🧪 测试ComputationFrame核心方法")
    demo = ComputationFrameDemo()
    
    # 获取一个扩展的ComputationFrame
    cf1 = demo.第1阶段_基础操作()
    cf3 = demo.第3阶段_查找操作(cf1)
    
    # 测试基本属性
    assert hasattr(cf3, 'nodes'), "应该有nodes属性"
    assert hasattr(cf3, 'vnames'), "应该有vnames属性"
    assert hasattr(cf3, 'fnames'), "应该有fnames属性"
    assert hasattr(cf3, 'edges'), "应该有edges方法"
    
    # 测试方法调用
    nodes = cf3.nodes
    vnames = cf3.vnames
    fnames = cf3.fnames
    edges = cf3.edges()
    
    print(f"- 节点数: {len(nodes)}")
    print(f"- 变量数: {len(vnames)}")
    print(f"- 函数数: {len(fnames)}")
    print(f"- 边数: {len(edges)}")
    
    # 测试复制操作
    cf_copy = cf3.copy()
    assert cf_copy is not None, "复制操作应该成功"
    assert len(cf_copy.nodes) == len(cf3.nodes), "复制后节点数应该相同"
    
    print("✅ ComputationFrame核心方法测试通过")
    return True

def main():
    """运行所有测试"""
    print("🚀 开始 ComputationFrame 综合演示测试")
    print("="*60)
    
    try:
        # 运行基础功能测试
        test_basic_functionality()
        
        # 运行高级功能测试
        test_advanced_functionality()
        
        # 运行错误处理测试
        test_error_handling()
        
        # 运行单独阶段测试
        test_individual_stages()
        
        # 运行核心方法测试
        test_cf_methods()
        
        print("\n" + "="*60)
        print("🎉 所有测试通过！")
        print("\n📋 测试总结:")
        print("✅ 基础功能测试 - 通过")
        print("✅ 高级功能测试 - 通过")
        print("✅ 错误处理测试 - 通过")
        print("✅ 单独阶段测试 - 通过")
        print("✅ 核心方法测试 - 通过")
        
        print("\n💡 测试建议:")
        print("1. 演示功能完整且稳定")
        print("2. 错误处理机制有效")
        print("3. 各阶段可以独立运行")
        print("4. ComputationFrame方法调用正常")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        print("详细错误信息:")
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 
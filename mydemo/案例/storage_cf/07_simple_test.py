#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mandala框架简化测试
==================

这是一个简化的测试文件，用于验证mandala框架的基本功能。
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

# 简化的导入，避免复杂的类型检查
try:
    from mandala1.storage import Storage
    from mandala1.core import op, wrap_atom
    from mandala1.cf import ComputationFrame
    print("成功导入mandala1模块")
except ImportError as e:
    print(f"导入mandala1失败: {e}")
    # 尝试直接导入基础模块
    try:
        import mandala1.storage as storage_module
        Storage = storage_module.Storage
        print("成功导入Storage类")
    except ImportError as e2:
        print(f"直接导入Storage失败: {e2}")
        sys.exit(1)

def simple_test():
    """简单测试mandala框架功能"""
    print("="*60)
    print("mandala框架简化测试")
    print("="*60)
    
    # 测试1：创建Storage
    print("\n1. 创建Storage:")
    try:
        storage = Storage()
        print("   Storage创建成功")
        print(f"   Storage类型: {type(storage)}")
        print(f"   Storage配置: {storage.dump_config()}")
    except Exception as e:
        print(f"   Storage创建失败: {e}")
        return
    
    # 测试2：定义简单操作
    print("\n2. 定义操作:")
    try:
        # 尝试定义一个简单的操作
        def simple_add(x, y):
            """简单的加法操作"""
            return x + y
        
        # 手动装饰操作
        try:
            simple_add_op = op(output_names=['result'])(simple_add)
            print("   操作定义成功")
        except Exception as e:
            print(f"   操作装饰失败: {e}")
            # 如果装饰失败，就直接使用普通函数
            simple_add_op = simple_add
    except Exception as e:
        print(f"   操作定义失败: {e}")
        return
    
    # 测试3：执行操作
    print("\n3. 执行操作:")
    try:
        with storage:
            result = simple_add_op(3, 5)
            print(f"   计算结果: {result}")
            
            # 解包结果
            actual_result = storage.unwrap(result)
            print(f"   实际结果: {actual_result}")
            
    except Exception as e:
        print(f"   操作执行失败: {e}")
        return
    
    # 测试4：访问存储信息
    print("\n4. 存储信息:")
    try:
        print(f"   原子缓存: {len(storage.atoms.cache) if hasattr(storage, 'atoms') else 'N/A'}")
        print(f"   调用缓存: {len(storage.calls.cache) if hasattr(storage, 'calls') else 'N/A'}")
        print(f"   操作缓存: {len(storage.ops.cache) if hasattr(storage, 'ops') else 'N/A'}")
    except Exception as e:
        print(f"   获取存储信息失败: {e}")
    
    # 测试5：创建ComputationFrame
    print("\n5. 创建ComputationFrame:")
    try:
        cf = storage.cf(simple_add_op)
        print(f"   ComputationFrame创建成功")
        print(f"   节点数: {len(cf.nodes) if hasattr(cf, 'nodes') else 'N/A'}")
        print(f"   变量节点: {cf.vnames if hasattr(cf, 'vnames') else 'N/A'}")
        print(f"   函数节点: {cf.fnames if hasattr(cf, 'fnames') else 'N/A'}")
        
        # 尝试生成数据框
        try:
            df = cf.df()
            print(f"   数据框形状: {df.shape}")
            print(f"   数据框内容:")
            print(df.head())
        except Exception as e:
            print(f"   数据框生成失败: {e}")
            
    except Exception as e:
        print(f"   ComputationFrame创建失败: {e}")
    
    print("\n" + "="*60)
    print("简化测试完成")
    print("="*60)

if __name__ == "__main__":
    simple_test() 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版栈回放（函数再执行）演示系统

这个演示展示了如何使用mandala框架实现函数的栈回放功能：
1. 创建两层函数的计算历史（第二层包含循环）
2. 查找和分析特定的函数调用
3. 修改函数参数并重新执行
4. 替换节点生成新的ComputationFrame

作者: AI Assistant
日期: 2025-01-18
"""

import sys
import os
from pathlib import Path

# 添加mandala路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 尝试导入必要的模块
try:
    # 直接导入需要的类，避免复杂的导入链
    import sqlite3
    import pandas as pd
    import numpy as np
    from typing import List, Dict, Any
    
    # 手动导入mandala组件
    from mandala1.storage import Storage
    from mandala1.model import op, Call, Ref
    from mandala1.cf import ComputationFrame
    
    print("✅ 成功导入所有必要模块")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请检查Python环境和依赖包")
    sys.exit(1)


@op
def 数据处理(数据: List[int], 乘数: int = 2) -> List[int]:
    """
    第一层函数：简单的数据处理
    对输入数据中的每个元素乘以指定的乘数
    """
    print(f"执行数据处理: 数据={数据}, 乘数={乘数}")
    结果 = [x * 乘数 for x in 数据]
    print(f"数据处理结果: {结果}")
    return 结果


@op
def 批量计算(输入列表: List[List[int]], 处理参数: int = 2) -> Dict[str, Any]:
    """
    第二层函数：包含循环的批量计算
    对输入列表中的每个子列表进行数据处理，然后汇总结果
    """
    print(f"开始批量计算: 输入列表长度={len(输入列表)}, 处理参数={处理参数}")
    
    所有结果 = []
    总和 = 0
    
    # 循环处理每个子列表（这里体现了第二层函数的循环复杂度）
    for i, 子列表 in enumerate(输入列表):
        print(f"处理第{i+1}个子列表: {子列表}")
        
        # 调用第一层函数
        处理结果 = 数据处理(子列表, 处理参数)
        所有结果.append(处理结果)
        
        # 计算当前结果的总和
        当前总和 = sum(处理结果)
        总和 += 当前总和
        
        print(f"第{i+1}个子列表处理完成，结果: {处理结果}, 总和: {当前总和}")
    
    最终结果 = {
        "所有结果": 所有结果,
        "总和": 总和,
        "平均值": 总和 / len(所有结果) if 所有结果 else 0,
        "处理数量": len(所有结果)
    }
    
    print(f"批量计算完成: {最终结果}")
    return 最终结果


def 演示栈回放():
    """演示栈回放功能"""
    print("🚀 开始栈回放演示")
    print("=" * 50)
    
    # 初始化存储
    storage = Storage(db_path=":memory:")
    print("✅ 存储初始化完成")
    
    # 步骤1: 创建计算历史
    print("\n📊 步骤1: 创建计算历史")
    测试数据 = [
        [1, 2, 3],
        [4, 5, 6], 
        [7, 8, 9]
    ]
    
    with storage:
        print("执行原始计算...")
        原始结果 = 批量计算(测试数据, 处理参数=2)
    
    print(f"原始计算完成，结果: {原始结果}")
    
    # 步骤2: 创建ComputationFrame
    print("\n🔍 步骤2: 创建ComputationFrame")
    try:
        原始cf = storage.cf(原始结果).expand_back(recursive=True)
        print(f"原始ComputationFrame创建完成，包含 {len(原始cf.nodes)} 个节点")
        print(f"变量节点: {len(原始cf.vnames)}, 函数节点: {len(原始cf.fnames)}")
    except Exception as e:
        print(f"❌ ComputationFrame创建失败: {e}")
        return
    
    # 步骤3: 查找目标函数
    print("\n🎯 步骤3: 查找目标函数")
    if "批量计算" in 原始cf.fnames:
        批量计算调用 = list(原始cf.calls_by_func()["批量计算"])
        print(f"找到 {len(批量计算调用)} 个批量计算调用")
        
        # 获取第一个调用的详细信息
        原始调用 = 批量计算调用[0]
        print("原始调用参数:")
        for 参数名, ref in 原始调用.inputs.items():
            原始值 = storage.unwrap(ref)
            print(f"  {参数名}: {原始值}")
    else:
        print("❌ 未找到批量计算函数")
        return
    
    # 步骤4: 修改参数重新执行
    print("\n🔄 步骤4: 修改参数重新执行")
    
    # 获取原始参数
    原始参数 = {}
    for 参数名, ref in 原始调用.inputs.items():
        原始参数[参数名] = storage.unwrap(ref)
    
    # 修改处理参数
    新参数 = 原始参数.copy()
    新参数["处理参数"] = 3  # 从2改为3
    
    print(f"参数修改: 处理参数 {原始参数['处理参数']} -> {新参数['处理参数']}")
    
    # 重新执行
    with storage:
        print("重新执行批量计算...")
        新结果 = 批量计算(**新参数)
    
    print(f"新计算完成，结果: {新结果}")
    
    # 步骤5: 创建新的ComputationFrame
    print("\n🆕 步骤5: 创建新的ComputationFrame")
    try:
        新cf = storage.cf(新结果).expand_back(recursive=True)
        print(f"新ComputationFrame创建完成，包含 {len(新cf.nodes)} 个节点")
    except Exception as e:
        print(f"❌ 新ComputationFrame创建失败: {e}")
        return
    
    # 步骤6: 合并ComputationFrame
    print("\n🔗 步骤6: 合并ComputationFrame")
    try:
        合并cf = 原始cf | 新cf
        print(f"ComputationFrame合并成功，包含 {len(合并cf.nodes)} 个节点")
    except Exception as e:
        print(f"⚠️ ComputationFrame合并失败: {e}")
        print("使用新的ComputationFrame作为替代")
        合并cf = 新cf
    
    # 步骤7: 结果分析
    print("\n📈 步骤7: 结果分析")
    print("原始结果 vs 新结果:")
    print(f"  总和: {原始结果['总和']} -> {新结果['总和']}")
    print(f"  平均值: {原始结果['平均值']:.2f} -> {新结果['平均值']:.2f}")
    print(f"  处理数量: {原始结果['处理数量']} -> {新结果['处理数量']}")
    
    # 计算变化
    总和变化 = 新结果['总和'] - 原始结果['总和']
    平均值变化 = 新结果['平均值'] - 原始结果['平均值']
    print(f"  变化: 总和+{总和变化}, 平均值+{平均值变化:.2f}")
    
    # 步骤8: 可视化（可选）
    print("\n🎨 步骤8: 可视化")
    try:
        输出目录 = Path(__file__).parent
        
        # 保存原始计算图
        原始cf.draw(path=str(输出目录 / "原始计算图.svg"), verbose=True)
        print("✅ 原始计算图已保存")
        
        # 保存新计算图
        新cf.draw(path=str(输出目录 / "新计算图.svg"), verbose=True)
        print("✅ 新计算图已保存")
        
        # 保存合并计算图
        合并cf.draw(path=str(输出目录 / "合并计算图.svg"), verbose=True)
        print("✅ 合并计算图已保存")
        
    except Exception as e:
        print(f"⚠️ 可视化失败: {e}")
    
    print("\n🎉 栈回放演示完成！")
    print("主要功能验证:")
    print("✅ 两层函数调用（第二层包含循环）")
    print("✅ 计算历史记录和查询")
    print("✅ 参数修改和函数重新执行")
    print("✅ 新节点替换和ComputationFrame生成")
    print("✅ 结果分析和比较")


def main():
    """主函数"""
    print("简化版栈回放（函数再执行）演示系统")
    print("=" * 60)
    
    try:
        演示栈回放()
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n演示结束！")


if __name__ == "__main__":
    main()
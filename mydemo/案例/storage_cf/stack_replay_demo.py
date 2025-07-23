#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
栈回放（函数再执行）演示系统

这个演示展示了如何使用mandala框架实现函数的栈回放功能：
1. 创建两层函数的计算历史（第二层包含循环）
2. 查找和分析特定的函数调用
3. 修改函数参数并重新执行
4. 替换节点生成新的ComputationFrame
5. 可视化和分析结果

作者: AI Assistant
日期: 2025-01-18
"""

import sys
import os
from pathlib import Path
try:
    from typing import List, Dict, Any, Optional, Tuple, Literal
except ImportError:
    from typing import List, Dict, Any, Optional, Tuple
    from typing_extensions import Literal
import logging

# 添加mandala路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from mandala1.imports import *
from mandala1.model import Call, Ref
from mandala1.cf import ComputationFrame

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@op
def 数据处理(数据: List[int], 乘数: int = 2) -> List[int]:
    """
    第一层函数：简单的数据处理
    对输入数据中的每个元素乘以指定的乘数
    """
    logger.info(f"执行数据处理: 数据={数据}, 乘数={乘数}")
    结果 = [x * 乘数 for x in 数据]
    logger.info(f"数据处理结果: {结果}")
    return 结果


@op
def 批量计算(输入列表: List[List[int]], 处理参数: int = 2) -> Dict[str, Any]:
    """
    第二层函数：包含循环的批量计算
    对输入列表中的每个子列表进行数据处理，然后汇总结果
    """
    logger.info(f"开始批量计算: 输入列表长度={len(输入列表)}, 处理参数={处理参数}")
    
    所有结果 = []
    总和 = 0
    
    # 循环处理每个子列表（这里体现了第二层函数的循环复杂度）
    for i, 子列表 in enumerate(输入列表):
        logger.info(f"处理第{i+1}个子列表: {子列表}")
        
        # 在noop上下文中调用第一层函数以获取实际值
        with noop():
            处理结果_值 = 数据处理(子列表, 处理参数)
        
        # 同时保存引用用于计算图
        处理结果_引用 = 数据处理(子列表, 处理参数)
        所有结果.append(处理结果_引用)
        
        # 计算当前结果的总和（使用实际值）
        当前总和 = sum(处理结果_值)
        总和 += 当前总和
        
        logger.info(f"第{i+1}个子列表处理完成，结果: {处理结果_值}, 总和: {当前总和}")
    
    最终结果 = {
        "所有结果": 所有结果,
        "总和": 总和,
        "平均值": 总和 / len(所有结果) if 所有结果 else 0,
        "处理数量": len(所有结果)
    }
    
    logger.info(f"批量计算完成: {最终结果}")
    return 最终结果


class StackReplayDemo:
    """栈回放演示主类"""
    
    def __init__(self, storage_path: str = ":memory:"):
        """初始化演示系统"""
        self.storage = Storage(db_path=storage_path)
        self.原始结果 = None
        self.原始cf = None
        logger.info(f"栈回放演示系统初始化完成，存储路径: {storage_path}")
    
    def 创建计算历史(self) -> None:
        """创建两层函数的计算历史"""
        logger.info("=" * 50)
        logger.info("开始创建计算历史...")
        
        # 准备测试数据
        测试数据 = [
            [1, 2, 3],
            [4, 5, 6], 
            [7, 8, 9]
        ]
        
        # 在storage上下文中执行计算
        with self.storage:
            logger.info("执行原始计算...")
            self.原始结果 = 批量计算(测试数据, 处理参数=2)
            
        logger.info(f"原始计算完成，结果: {self.原始结果}")
        
        # 创建原始的ComputationFrame
        self.原始cf = self.storage.cf(self.原始结果).expand_back(recursive=True)
        logger.info(f"原始ComputationFrame创建完成，包含 {len(self.原始cf.nodes)} 个节点")
        
    def 查找目标函数(self, 函数名: str) -> List[Call]:
        """查找指定函数的所有调用记录"""
        logger.info(f"查找函数 '{函数名}' 的调用记录...")
        
        # 从ComputationFrame中获取函数调用
        if 函数名 in self.原始cf.fnames:
            调用集合 = self.原始cf.calls_by_func()[函数名]
            调用列表 = list(调用集合)
            logger.info(f"找到 {len(调用列表)} 个 '{函数名}' 的调用记录")
            
            # 显示调用详情
            for i, call in enumerate(调用列表):
                logger.info(f"调用 {i+1}: 输入={call.inputs}, 输出键={list(call.outputs.keys())}")
            
            return 调用列表
        else:
            logger.warning(f"未找到函数 '{函数名}' 的调用记录")
            return []
    
    def 修改参数重新执行(self, 原始调用: Call, 新参数: Dict[str, Any]) -> Any:
        """修改参数并重新执行函数"""
        logger.info("=" * 50)
        logger.info("开始修改参数并重新执行函数...")
        
        # 获取原始参数
        原始参数 = {}
        for 参数名, ref in 原始调用.inputs.items():
            原始值 = self.storage.unwrap(ref)
            原始参数[参数名] = 原始值
            logger.info(f"原始参数 {参数名}: {原始值}")
        
        # 应用新参数
        最终参数 = 原始参数.copy()
        最终参数.update(新参数)
        
        logger.info("应用新参数:")
        for 参数名, 新值 in 新参数.items():
            logger.info(f"  {参数名}: {原始参数.get(参数名)} -> {新值}")
        
        # 重新执行函数
        with self.storage:
            if 原始调用.op.name == "批量计算":
                新结果 = 批量计算(**最终参数)
            elif 原始调用.op.name == "数据处理":
                新结果 = 数据处理(**最终参数)
            else:
                raise ValueError(f"不支持的函数: {原始调用.op.name}")
        
        logger.info(f"重新执行完成，新结果: {新结果}")
        return 新结果
    
    def 替换节点生成新CF(self, 新结果: Any) -> ComputationFrame:
        """基于新结果创建新的ComputationFrame"""
        logger.info("=" * 50)
        logger.info("创建新的ComputationFrame...")
        
        # 创建包含新结果的ComputationFrame
        新cf = self.storage.cf(新结果).expand_back(recursive=True)
        logger.info(f"新ComputationFrame创建完成，包含 {len(新cf.nodes)} 个节点")
        
        return 新cf
    
    def 合并ComputationFrame(self, 原始cf: ComputationFrame, 新cf: ComputationFrame) -> ComputationFrame:
        """合并原始和新的ComputationFrame"""
        logger.info("合并ComputationFrame...")
        
        try:
            # 尝试合并两个ComputationFrame
            合并cf = 原始cf | 新cf
            logger.info(f"ComputationFrame合并成功，包含 {len(合并cf.nodes)} 个节点")
            return 合并cf
        except Exception as e:
            logger.warning(f"ComputationFrame合并失败: {e}")
            logger.info("返回新的ComputationFrame作为替代")
            return 新cf
    
    def 可视化结果(self, cf: ComputationFrame, 文件名: str) -> None:
        """可视化ComputationFrame"""
        logger.info(f"生成可视化文件: {文件名}")
        
        try:
            输出路径 = Path(__file__).parent / f"{文件名}.svg"
            cf.draw(path=str(输出路径), verbose=True, orientation='TB')
            logger.info(f"可视化文件已保存: {输出路径}")
        except Exception as e:
            logger.error(f"可视化失败: {e}")
    
    def 分析结果(self, 原始结果: Any, 新结果: Any) -> None:
        """分析和比较结果"""
        logger.info("=" * 50)
        logger.info("结果分析:")
        
        logger.info("原始结果:")
        if isinstance(原始结果, dict):
            for key, value in 原始结果.items():
                logger.info(f"  {key}: {value}")
        else:
            logger.info(f"  {原始结果}")
        
        logger.info("新结果:")
        if isinstance(新结果, dict):
            for key, value in 新结果.items():
                logger.info(f"  {key}: {value}")
        else:
            logger.info(f"  {新结果}")
        
        # 计算差异
        if isinstance(原始结果, dict) and isinstance(新结果, dict):
            logger.info("差异分析:")
            for key in set(原始结果.keys()) | set(新结果.keys()):
                原始值 = 原始结果.get(key, "未定义")
                新值 = 新结果.get(key, "未定义")
                if 原始值 != 新值:
                    logger.info(f"  {key}: {原始值} -> {新值}")
    
    def 运行完整演示(self) -> None:
        """运行完整的栈回放演示"""
        logger.info("🚀 开始栈回放演示")
        
        try:
            # 步骤1: 创建计算历史
            self.创建计算历史()
            
            # 步骤2: 查找目标函数
            批量计算调用 = self.查找目标函数("批量计算")
            if not 批量计算调用:
                logger.error("未找到批量计算函数的调用记录")
                return
            
            # 步骤3: 修改参数重新执行
            原始调用 = 批量计算调用[0]  # 取第一个调用
            新参数 = {"处理参数": 3}  # 将处理参数从2改为3
            新结果 = self.修改参数重新执行(原始调用, 新参数)
            
            # 步骤4: 创建新的ComputationFrame
            新cf = self.替换节点生成新CF(新结果)
            
            # 步骤5: 合并ComputationFrame
            合并cf = self.合并ComputationFrame(self.原始cf, 新cf)
            
            # 步骤6: 可视化结果
            self.可视化结果(self.原始cf, "原始计算图")
            self.可视化结果(新cf, "新计算图")
            self.可视化结果(合并cf, "合并计算图")
            
            # 步骤7: 分析结果
            self.分析结果(self.原始结果, 新结果)
            
            logger.info("✅ 栈回放演示完成")
            
        except Exception as e:
            logger.error(f"❌ 演示过程中发生错误: {e}")
            raise


def main():
    """主函数"""
    print("栈回放（函数再执行）演示系统")
    print("=" * 50)
    
    # 创建演示实例
    demo = StackReplayDemo()
    
    # 运行完整演示
    demo.运行完整演示()
    
    print("\n演示完成！请查看生成的SVG文件以查看计算图。")


if __name__ == "__main__":
    main()
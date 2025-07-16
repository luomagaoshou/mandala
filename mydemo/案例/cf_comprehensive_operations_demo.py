"""
ComputationFrame 综合操作演示
从简单到复杂，逐步展示 ComputationFrame 的各种操作

文档来源：
- 基于 mydemo/doc/cf.md 的 ComputationFrame 完整文档
- 参考 mandala1/cf.py 的实际实现
- 主题：从基础到高级的 ComputationFrame 操作
- 内容结构：
  1. 基础操作：创建、查看、基本属性
  2. 遍历操作：节点遍历、边遍历、路径查找
  3. 查找操作：节点查找、值查找、条件过滤
  4. 删除操作：节点删除、引用删除、批量删除
  5. 增加操作：节点增加、边增加、数据增加
  6. 修改操作：重命名、数据修改、结构调整
  7. 替换操作：节点替换、值替换、图重构
  8. 高级操作：图合并、扩展、优化
  9. 单节点操作：单一节点的增删查改细粒度操作

演示特点：
- 每个操作都有详细的中文注释
- 从简单的单步操作到复杂的组合操作
- 展示实际的使用场景和最佳实践
- 包含错误处理和验证机制
"""

import numpy as np
import pandas as pd
from mandala1.imports import Storage, op
import logging

# 设置随机种子确保结果可重现
np.random.seed(42)

# 定义一系列测试用的操作函数
@op
def 数据预处理(原始数据):
    """数据预处理：清洗和标准化"""
    return [x * 2 for x in 原始数据 if x > 0]

@op
def 特征提取(数据):
    """特征提取：计算统计特征"""
    return {
        '平均值': np.mean(数据),
        '标准差': np.std(数据),
        '最大值': np.max(数据),
        '最小值': np.min(数据)
    }

@op
def 数据变换(数据, 变换类型='标准化'):
    """数据变换：应用不同的变换方法"""
    if 变换类型 == '标准化':
        mean_val = np.mean(数据)
        std_val = np.std(数据)
        return [(x - mean_val) / std_val for x in 数据]
    elif 变换类型 == '归一化':
        min_val = np.min(数据)
        max_val = np.max(数据)
        return [(x - min_val) / (max_val - min_val) for x in 数据]
    else:
        return 数据

@op
def 模型训练(特征数据, 算法='线性回归'):
    """模型训练：基于特征训练模型"""
    return {
        '算法': 算法,
        '特征数量': len(特征数据) if isinstance(特征数据, list) else 1,
        '训练状态': '成功',
        '模型参数': {'权重': np.random.random(3).tolist()}
    }

@op
def 模型评估(模型, 测试数据):
    """模型评估：评估模型性能"""
    return {
        '准确率': np.random.uniform(0.7, 0.95),
        '精确率': np.random.uniform(0.6, 0.9),
        '召回率': np.random.uniform(0.6, 0.9),
        '测试样本数': len(测试数据) if isinstance(测试数据, list) else 1
    }

@op
def 结果汇总(评估结果, 模型信息):
    """结果汇总：生成最终报告"""
    return {
        '模型类型': 模型信息.get('算法', '未知'),
        '性能指标': 评估结果,
        '推荐使用': 评估结果.get('准确率', 0) > 0.8
    }

# 用于单节点操作演示的附加函数
@op
def 数据验证(数据):
    """数据验证：检查数据质量"""
    return {
        '数据长度': len(数据) if hasattr(数据, '__len__') else 1,
        '数据类型': type(数据).__name__,
        '是否有效': 数据 is not None
    }

@op
def 单步计算(输入值, 操作类型='平方'):
    """单步计算：简单的数学运算"""
    if 操作类型 == '平方':
        return 输入值 ** 2
    elif 操作类型 == '立方':
        return 输入值 ** 3
    elif 操作类型 == '开方':
        return 输入值 ** 0.5 if 输入值 >= 0 else 0
    else:
        return 输入值

@op
def 条件处理(数据, 条件='大于零'):
    """条件处理：基于条件过滤数据"""
    if isinstance(数据, (list, tuple)):
        if 条件 == '大于零':
            return [x for x in 数据 if x > 0]
        elif 条件 == '偶数':
            return [x for x in 数据 if x % 2 == 0]
        else:
            return 数据
    else:
        return 数据 if 数据 > 0 else 0

class ComputationFrameDemo:
    """ComputationFrame 综合操作演示类"""
    
    def __init__(self):
        self.storage = Storage()
        self.演示阶段 = 0
        
    def 打印分隔线(self, 标题):
        """打印美观的分隔线"""
        print(f"\n{'='*60}")
        print(f"第{self.演示阶段}阶段：{标题}")
        print(f"{'='*60}")
        self.演示阶段 += 1
    
    def 第1阶段_基础操作(self):
        """第1阶段：ComputationFrame 基础操作"""
        self.打印分隔线("基础操作 - 创建和查看")
        
        # 1.1 创建基础计算历史
        print("1.1 创建基础计算历史")
        with self.storage:
            原始数据 = [1, 2, 3, 4, 5, -1, 0, 6, 7, 8]
            清洗数据 = 数据预处理(原始数据)
            特征 = 特征提取(清洗数据)
            
            print(f"- 原始数据: {原始数据}")
            print(f"- 清洗后数据: {self.storage.unwrap(清洗数据)}")
            print(f"- 提取特征: {self.storage.unwrap(特征)}")
        
        # 1.2 创建 ComputationFrame
        print("\n1.2 创建 ComputationFrame")
        cf = self.storage.cf(特征)
        print(f"- 初始 CF 节点数: {len(cf.nodes)}")
        print(f"- 变量节点: {list(cf.vnames)}")
        print(f"- 函数节点: {list(cf.fnames)}")
        
        # 1.3 查看基本属性
        print("\n1.3 查看基本属性")
        print(f"- 源节点: {cf.sources}")
        print(f"- 汇节点: {cf.sinks}")
        print(f"- 边数量: {len(cf.edges())}")
        print(f"- 图描述:\n{cf.get_graph_desc()}")
        
        return cf
    
    def 第2阶段_遍历操作(self, cf):
        """第2阶段：遍历操作 - 节点遍历、边遍历、路径查找"""
        self.打印分隔线("遍历操作 - 图结构探索")
        
        # 2.1 节点遍历
        print("2.1 节点遍历")
        print("所有节点:")
        for i, node in enumerate(cf.nodes, 1):
            node_type = "变量" if node in cf.vnames else "函数"
            element_count = len(cf.sets[node])
            print(f"  {i}. {node} ({node_type}) - {element_count}个元素")
        
        # 2.2 边遍历
        print("\n2.2 边遍历")
        print("所有边:")
        for i, (src, dst, label) in enumerate(cf.edges(), 1):
            print(f"  {i}. {src} --[{label}]--> {dst}")
        
        # 2.3 邻居查找
        print("\n2.3 邻居查找")
        if cf.nodes:
            sample_node = next(iter(cf.nodes))
            in_neighbors = cf.in_neighbors(sample_node)
            out_neighbors = cf.out_neighbors(sample_node)
            print(f"节点 '{sample_node}' 的邻居:")
            print(f"- 输入邻居: {in_neighbors}")
            print(f"- 输出邻居: {out_neighbors}")
        
        # 2.4 拓扑排序
        print("\n2.4 拓扑排序")
        sorted_nodes = cf.topsort_modulo_sccs()
        print(f"拓扑排序结果: {sorted_nodes}")
        
        return cf
    
    def 第3阶段_查找操作(self, cf):
        """第3阶段：查找操作 - 节点查找、值查找、条件过滤"""
        self.打印分隔线("查找操作 - 数据检索")
        
        # 3.1 扩展计算框架以获得更多数据
        print("3.1 扩展计算框架")
        expanded_cf = cf.expand_back(recursive=True)
        print(f"- 扩展前节点数: {len(cf.nodes)}")
        print(f"- 扩展后节点数: {len(expanded_cf.nodes)}")
        print(f"- 新增变量: {expanded_cf.vnames - cf.vnames}")
        print(f"- 新增函数: {expanded_cf.fnames - cf.fnames}")
        
        # 3.2 按类型查找节点
        print("\n3.2 按类型查找节点")
        variables = expanded_cf.vnames
        functions = expanded_cf.fnames
        print(f"- 变量节点 ({len(variables)}个): {list(variables)}")
        print(f"- 函数节点 ({len(functions)}个): {list(functions)}")
        
        # 3.3 查找特定操作的节点
        print("\n3.3 查找特定操作的节点")
        ops_dict = expanded_cf.ops()
        for fname, op in ops_dict.items():
            print(f"- 函数 '{fname}' 对应操作: {op.name}")
        
        # 3.4 值查找和过滤
        print("\n3.4 值查找和过滤")
        try:
            # 获取函数调用表
            if functions:
                sample_func = next(iter(functions))
                func_table = expanded_cf.get_func_table(sample_func)
                print(f"函数 '{sample_func}' 的调用表:")
                print(func_table.head() if len(func_table) > 0 else "无调用记录")
        except Exception as e:
            print(f"获取函数表时出错: {e}")
        
        # 3.5 源和汇元素查找
        print("\n3.5 源和汇元素查找")
        source_elts = expanded_cf.get_source_elts()
        sink_elts = expanded_cf.get_sink_elts()
        print("源元素统计:")
        for node, elts in source_elts.items():
            if elts:
                print(f"  {node}: {len(elts)}个源元素")
        print("汇元素统计:")
        for node, elts in sink_elts.items():
            if elts:
                print(f"  {node}: {len(elts)}个汇元素")
        
        return expanded_cf
    
    def 第4阶段_删除操作(self, cf):
        """第4阶段：删除操作 - 节点删除、引用删除、批量删除"""
        self.打印分隔线("删除操作 - 数据清理")
        
        # 4.1 复制 CF 用于删除实验
        print("4.1 准备删除实验")
        cf_copy = cf.copy()
        print(f"- 复制前节点数: {len(cf.nodes)}")
        print(f"- 复制后节点数: {len(cf_copy.nodes)}")
        
        # 4.2 删除单个节点
        print("\n4.2 删除单个节点")
        if cf_copy.nodes:
            # 选择一个非关键节点进行删除
            nodes_to_try = list(cf_copy.nodes)
            deleted_node = None
            
            for node in nodes_to_try:
                try:
                    # 尝试删除节点
                    cf_after_delete = cf_copy.drop_node(node, inplace=False)
                    deleted_node = node
                    print(f"- 成功删除节点: {node}")
                    print(f"- 删除前节点数: {len(cf_copy.nodes)}")
                    print(f"- 删除后节点数: {len(cf_after_delete.nodes)}")
                    cf_copy = cf_after_delete
                    break
                except Exception as e:
                    print(f"- 删除节点 '{node}' 失败: {e}")
                    continue
        
        # 4.3 批量删除节点
        print("\n4.3 批量删除节点")
        if len(cf_copy.nodes) >= 2:
            # 选择多个节点进行批量删除
            nodes_to_delete = list(cf_copy.nodes)[:2]
            try:
                cf_batch_deleted = cf_copy.drop(nodes_to_delete, inplace=False)
                print(f"- 批量删除节点: {nodes_to_delete}")
                print(f"- 删除前节点数: {len(cf_copy.nodes)}")
                print(f"- 删除后节点数: {len(cf_batch_deleted.nodes)}")
                cf_copy = cf_batch_deleted
            except Exception as e:
                print(f"- 批量删除失败: {e}")
        
        # 4.4 清理空节点
        print("\n4.4 清理和简化")
        cf_cleaned = cf_copy.cleanup(inplace=False)
        print(f"- 清理前节点数: {len(cf_copy.nodes)}")
        print(f"- 清理后节点数: {len(cf_cleaned.nodes)}")
        
        return cf_cleaned
    
    def 第5阶段_增加操作(self, cf):
        """第5阶段：增加操作 - 节点增加、边增加、数据增加"""
        self.打印分隔线("增加操作 - 扩展计算图")
        
        # 5.1 创建新的计算数据
        print("5.1 创建新的计算数据")
        # 使用独立的存储实例来避免合并冲突
        with self.storage:
            # 创建新的计算分支
            新数据 = [10, 20, 30, 40, 50]
            变换数据 = 数据变换(新数据, 变换类型='归一化')
            模型 = 模型训练(变换数据, 算法='决策树')
            评估 = 模型评估(模型, 新数据)
            最终报告 = 结果汇总(评估, 模型)
            
            print(f"- 新数据: {新数据}")
            print(f"- 变换结果: {self.storage.unwrap(变换数据)}")
            print(f"- 模型信息: {self.storage.unwrap(模型)}")
            print(f"- 评估结果: {self.storage.unwrap(评估)}")
            print(f"- 最终报告: {self.storage.unwrap(最终报告)}")
        
        # 5.2 创建新的 ComputationFrame
        print("\n5.2 创建新的 ComputationFrame")
        new_cf = self.storage.cf(最终报告).expand_back(recursive=True)
        print(f"- 新 CF 节点数: {len(new_cf.nodes)}")
        print(f"- 新 CF 变量: {list(new_cf.vnames)}")
        print(f"- 新 CF 函数: {list(new_cf.fnames)}")
        
        # 5.3 合并 ComputationFrame
        print("\n5.3 合并 ComputationFrame")
        try:
            merged_cf = cf | new_cf  # 使用并集操作
            print(f"- 原 CF 节点数: {len(cf.nodes)}")
            print(f"- 新 CF 节点数: {len(new_cf.nodes)}")
            print(f"- 合并后节点数: {len(merged_cf.nodes)}")
            print(f"- 合并后变量数: {len(merged_cf.vnames)}")
            print(f"- 合并后函数数: {len(merged_cf.fnames)}")
        except Exception as e:
            print(f"- 合并失败: {e}")
            print("- 使用新的 CF 继续演示")
            merged_cf = new_cf
            print(f"- 使用新 CF，节点数: {len(merged_cf.nodes)}")
            print(f"- 使用新 CF，变量数: {len(merged_cf.vnames)}")
            print(f"- 使用新 CF，函数数: {len(merged_cf.fnames)}")
        
        # 5.4 扩展操作
        print("\n5.4 扩展操作")
        try:
            # 向前扩展
            forward_expanded = merged_cf.expand_forward(recursive=True)
            print(f"- 向前扩展后节点数: {len(forward_expanded.nodes)}")
            
            # 全方向扩展
            full_expanded = merged_cf.expand_all()
            print(f"- 全方向扩展后节点数: {len(full_expanded.nodes)}")
            
            return full_expanded
        except Exception as e:
            print(f"- 扩展操作失败: {e}")
            print("- 返回合并后的 CF")
            return merged_cf
    
    def 第6阶段_修改操作(self, cf):
        """第6阶段：修改操作 - 重命名、数据修改、结构调整"""
        self.打印分隔线("修改操作 - 结构调整")
        
        # 6.1 节点重命名
        print("6.1 节点重命名")
        cf_renamed = cf.copy()
        
        # 获取一些变量进行重命名
        variables = list(cf_renamed.vnames)
        if len(variables) >= 2:
            rename_dict = {
                variables[0]: f"重命名_{variables[0]}",
                variables[1]: f"优化_{variables[1]}"
            }
            
            try:
                cf_renamed = cf_renamed.rename(vars=rename_dict, inplace=False)
                print(f"- 重命名映射: {rename_dict}")
                print(f"- 重命名前变量: {variables[:2]}")
                print(f"- 重命名后变量: {[name for name in cf_renamed.vnames if '重命名_' in name or '优化_' in name]}")
            except Exception as e:
                print(f"- 重命名失败: {e}")
        
        # 6.2 选择子图
        print("\n6.2 选择子图")
        if len(cf.nodes) >= 3:
            selected_nodes = list(cf.nodes)[:3]
            sub_cf = cf.select_nodes(selected_nodes)
            print(f"- 选择的节点: {selected_nodes}")
            print(f"- 原图节点数: {len(cf.nodes)}")
            print(f"- 子图节点数: {len(sub_cf.nodes)}")
            print(f"- 子图边数: {len(sub_cf.edges())}")
        
        # 6.3 上游和下游分析
        print("\n6.3 上游和下游分析")
        if cf.vnames:
            sample_var = next(iter(cf.vnames))
            try:
                upstream_cf = cf.upstream(sample_var)
                downstream_cf = cf.downstream(sample_var)
                
                print(f"- 分析变量: {sample_var}")
                print(f"- 上游节点数: {len(upstream_cf.nodes)}")
                print(f"- 下游节点数: {len(downstream_cf.nodes)}")
                print(f"- 上游变量: {list(upstream_cf.vnames)}")
                print(f"- 下游变量: {list(downstream_cf.vnames)}")
            except Exception as e:
                print(f"- 上下游分析失败: {e}")
        
        return cf_renamed
    
    def 第7阶段_替换操作(self, cf):
        """第7阶段：替换操作 - 节点替换、值替换、图重构"""
        self.打印分隔线("替换操作 - 高级重构")
        
        # 7.1 创建替换数据
        print("7.1 创建替换数据")
        with self.storage:
            # 创建一个改进的计算流程
            改进数据 = [100, 200, 300, 400, 500]
            改进特征 = 特征提取(改进数据)
            改进模型 = 模型训练(改进特征, 算法='随机森林')
            改进评估 = 模型评估(改进模型, 改进数据)
            最终报告 = 结果汇总(改进评估, 改进模型)
            
            print(f"- 改进数据: {改进数据}")
            print(f"- 改进特征: {self.storage.unwrap(改进特征)}")
            print(f"- 改进模型: {self.storage.unwrap(改进模型)['算法']}")
            print(f"- 最终报告: {self.storage.unwrap(最终报告)}")
        
        # 7.2 创建替换的 ComputationFrame
        print("\n7.2 创建替换的 ComputationFrame")
        replacement_cf = self.storage.cf(最终报告).expand_back(recursive=True)
        print(f"- 替换 CF 节点数: {len(replacement_cf.nodes)}")
        print(f"- 替换 CF 包含的操作: {list(replacement_cf.ops().keys())}")
        
        # 7.3 分析替换前后的差异
        print("\n7.3 分析替换前后的差异")
        print("原始计算图:")
        print(f"  节点数: {len(cf.nodes)}")
        print(f"  变量数: {len(cf.vnames)}")
        print(f"  函数数: {len(cf.fnames)}")
        
        print("替换计算图:")
        print(f"  节点数: {len(replacement_cf.nodes)}")
        print(f"  变量数: {len(replacement_cf.vnames)}")
        print(f"  函数数: {len(replacement_cf.fnames)}")
        
        # 7.4 图重构 - 创建混合计算图
        print("\n7.4 图重构 - 创建混合计算图")
        try:
            # 使用并集创建包含两个计算流程的图
            hybrid_cf = cf | replacement_cf
            print(f"- 混合图节点数: {len(hybrid_cf.nodes)}")
            print(f"- 混合图变量数: {len(hybrid_cf.vnames)}")
            print(f"- 混合图函数数: {len(hybrid_cf.fnames)}")
        except Exception as e:
            print(f"- 直接合并失败: {e}")
            print("- 使用替代方案：分别分析两个计算图")
            hybrid_cf = replacement_cf  # 使用替换图作为主要分析对象
            print(f"- 使用替换图进行后续分析")
            print(f"- 替换图节点数: {len(hybrid_cf.nodes)}")
            print(f"- 替换图变量数: {len(hybrid_cf.vnames)}")
            print(f"- 替换图函数数: {len(hybrid_cf.fnames)}")
        
        # 7.5 对比分析
        print("\n7.5 对比分析")
        try:
            # 尝试提取和比较结果
            if hybrid_cf.vnames:
                sample_vars = list(hybrid_cf.vnames)[:3]
                comparison_df = hybrid_cf.df(*sample_vars, verbose=False)
                print(f"- 对比变量: {sample_vars}")
                print(f"- 对比数据形状: {comparison_df.shape}")
                if not comparison_df.empty:
                    print("- 对比结果预览:")
                    print(comparison_df.head())
        except Exception as e:
            print(f"- 对比分析失败: {e}")
        
        return hybrid_cf
    
    def 第8阶段_高级操作(self, cf):
        """第8阶段：高级操作 - 图合并、扩展、优化"""
        self.打印分隔线("高级操作 - 图优化和分析")
        
        # 8.1 图统计分析
        print("8.1 图统计分析")
        print(f"- 总节点数: {len(cf.nodes)}")
        print(f"- 总边数: {len(cf.edges())}")
        print(f"- 变量节点数: {len(cf.vnames)}")
        print(f"- 函数节点数: {len(cf.fnames)}")
        print(f"- 源节点数: {len(cf.sources)}")
        print(f"- 汇节点数: {len(cf.sinks)}")
        
        # 8.2 复杂查询操作
        print("\n8.2 复杂查询操作")
        try:
            # 获取计算历史
            if cf.vnames:
                sample_var = list(cf.vnames)[0]
                history_df = cf.get_history_df(sample_var, verbose=False)
                print(f"- 变量 '{sample_var}' 的历史:")
                print(f"  历史记录数: {len(history_df)}")
                print(f"  涉及变量: {list(history_df.columns)}")
        except Exception as e:
            print(f"- 历史查询失败: {e}")
        
        # 8.3 图优化
        print("\n8.3 图优化")
        try:
            # 尝试合并变量
            optimized_cf = cf.copy()
            optimized_cf.merge_vars(inplace=True)
            print(f"- 优化前变量数: {len(cf.vnames)}")
            print(f"- 优化后变量数: {len(optimized_cf.vnames)}")
            
            # 清理优化
            optimized_cf.cleanup(inplace=True)
            print(f"- 清理后节点数: {len(optimized_cf.nodes)}")
        except Exception as e:
            print(f"- 图优化失败: {e}")
        
        # 8.4 可达性分析
        print("\n8.4 可达性分析")
        try:
            if cf.sources:
                source_node = next(iter(cf.sources))
                reachable_nodes = cf.get_reachable_nodes({source_node}, direction="forward")
                print(f"- 从源节点 '{source_node}' 可达的节点数: {len(reachable_nodes)}")
                print(f"- 可达节点: {list(reachable_nodes)[:5]}...")  # 只显示前5个
        except Exception as e:
            print(f"- 可达性分析失败: {e}")
        
        # 8.5 性能统计
        print("\n8.5 性能统计")
        var_stats = cf.get_var_stats()
        func_stats = cf.get_func_stats()
        
        print("变量统计:")
        if not var_stats.empty:
            print(f"  平均值数量: {var_stats['num_values'].mean():.2f}")
            print(f"  最大值数量: {var_stats['num_values'].max()}")
            print(f"  最小值数量: {var_stats['num_values'].min()}")
        
        print("函数统计:")
        if not func_stats.empty:
            print(f"  平均调用数: {func_stats['num_calls'].mean():.2f}")
            print(f"  最大调用数: {func_stats['num_calls'].max()}")
            print(f"  最小调用数: {func_stats['num_calls'].min()}")
        
        return cf
    
    def 第9阶段_单节点操作(self, cf):
        """第9阶段：单节点操作 - 单一节点的增删查改细粒度操作"""
        self.打印分隔线("单节点操作 - 细粒度节点管理")
        
        # 9.1 单节点查询操作
        print("9.1 单节点查询操作")
        
        # 获取一个示例变量节点进行操作
        if cf.vnames:
            示例变量 = list(cf.vnames)[0]
            print(f"- 选择变量节点: {示例变量}")
            
            # 查询节点基本信息
            print(f"  节点类型: 变量")
            print(f"  包含元素数: {len(cf.vs[示例变量])}")
            print(f"  元素ID列表: {list(cf.vs[示例变量])[:3]}...")  # 只显示前3个
            
            # 查询节点的邻居
            输入邻居 = cf.in_neighbors(示例变量)
            输出邻居 = cf.out_neighbors(示例变量)
            print(f"  输入邻居: {输入邻居}")
            print(f"  输出邻居: {输出邻居}")
            
            # 查询节点的边
            输入边 = cf.in_edges(示例变量)
            输出边 = cf.out_edges(示例变量)
            print(f"  输入边数: {len(输入边)}")
            print(f"  输出边数: {len(输出边)}")
            
            # 查询节点的值
            节点值 = cf.get_var_values(示例变量)
            print(f"  节点值数量: {len(节点值)}")
        
        # 获取一个示例函数节点进行操作
        if cf.fnames:
            示例函数 = list(cf.fnames)[0]
            print(f"\n- 选择函数节点: {示例函数}")
            
            # 查询函数节点信息
            print(f"  节点类型: 函数")
            print(f"  包含调用数: {len(cf.fs[示例函数])}")
            
            # 获取函数对应的操作
            操作字典 = cf.ops()
            if 示例函数 in 操作字典:
                操作对象 = 操作字典[示例函数]
                print(f"  对应操作: {操作对象.name}")
                # 尝试获取操作的更多信息
                try:
                    if hasattr(操作对象, 'sig'):
                        print(f"  操作签名: {操作对象.sig}")
                    elif hasattr(操作对象, 'f'):
                        print(f"  操作函数: {操作对象.f.__name__}")
                    else:
                        print(f"  操作类型: {type(操作对象)}")
                except Exception as e:
                    print(f"  获取操作详情失败: {e}")
        
        # 9.2 单节点增加操作
        print("\n9.2 单节点增加操作")
        
        # 创建用于演示的新数据
        with self.storage:
            新测试数据 = 42
            验证结果 = 数据验证(新测试数据)
            计算结果 = 单步计算(新测试数据, 操作类型='平方')
            
            print(f"- 创建新数据: {新测试数据}")
            print(f"- 验证结果: {self.storage.unwrap(验证结果)}")
            print(f"- 计算结果: {self.storage.unwrap(计算结果)}")
        
        # 创建包含新数据的 ComputationFrame
        新节点cf = self.storage.cf(计算结果).expand_back(recursive=True)
        print(f"- 新节点CF变量数: {len(新节点cf.vnames)}")
        print(f"- 新节点CF函数数: {len(新节点cf.fnames)}")
        
        # 9.3 单节点修改操作
        print("\n9.3 单节点修改操作")
        
        # 复制CF用于修改实验
        修改cf = cf.copy()
        原始节点数 = len(修改cf.nodes)
        
        # 添加新变量节点
        try:
            新变量名 = 修改cf._add_var("手动添加变量")
            print(f"- 添加新变量节点: {新变量名}")
            print(f"- 添加前节点数: {原始节点数}")
            print(f"- 添加后节点数: {len(修改cf.nodes)}")
        except Exception as e:
            print(f"- 添加变量节点失败: {e}")
        
        # 重命名变量节点
        if 修改cf.vnames:
            原变量名 = list(修改cf.vnames)[0]
            新变量名 = f"重命名_{原变量名}"
            try:
                修改cf.rename_var(原变量名, 新变量名, inplace=True)
                print(f"- 重命名变量: {原变量名} -> {新变量名}")
                print(f"- 重命名后变量列表: {list(修改cf.vnames)[:3]}...")
            except Exception as e:
                print(f"- 重命名变量失败: {e}")
        
        # 9.4 单节点引用操作
        print("\n9.4 单节点引用操作")
        
        # 获取新创建的引用
        if 新节点cf.vnames:
            目标变量 = list(新节点cf.vnames)[0]
            变量引用 = 新节点cf.get_var_values(目标变量)
            
            if 变量引用:
                示例引用 = next(iter(变量引用))
                print(f"- 目标变量: {目标变量}")
                print(f"- 引用对象: {示例引用}")
                print(f"- 引用值: {self.storage.unwrap(示例引用)}")
                
                # 尝试将引用添加到现有变量
                if 修改cf.vnames:
                    目标现有变量 = list(修改cf.vnames)[0]
                    try:
                        修改cf.add_ref(目标现有变量, 示例引用, allow_existing=True)
                        print(f"- 成功将引用添加到变量: {目标现有变量}")
                        print(f"- 添加后该变量的引用数: {len(修改cf.vs[目标现有变量])}")
                    except Exception as e:
                        print(f"- 添加引用失败: {e}")
        
        # 9.5 单节点删除操作
        print("\n9.5 单节点删除操作")
        
        删除cf = 修改cf.copy()
        删除前节点数 = len(删除cf.nodes)
        
        # 删除单个变量节点
        if 删除cf.vnames:
            要删除的变量 = list(删除cf.vnames)[-1]  # 选择最后一个变量
            try:
                删除cf.drop_var(要删除的变量, inplace=True)
                print(f"- 删除变量节点: {要删除的变量}")
                print(f"- 删除前节点数: {删除前节点数}")
                print(f"- 删除后节点数: {len(删除cf.nodes)}")
            except Exception as e:
                print(f"- 删除变量节点失败: {e}")
        
        # 删除单个函数节点
        if 删除cf.fnames:
            要删除的函数 = list(删除cf.fnames)[-1]  # 选择最后一个函数
            try:
                删除cf.drop_func(要删除的函数, inplace=True)
                print(f"- 删除函数节点: {要删除的函数}")
                print(f"- 删除后节点数: {len(删除cf.nodes)}")
            except Exception as e:
                print(f"- 删除函数节点失败: {e}")
        
        # 9.6 单节点边操作
        print("\n9.6 单节点边操作")
        
        边操作cf = cf.copy()
        原始边数 = len(边操作cf.edges())
        
        # 查看现有边
        if 边操作cf.edges():
            示例边 = 边操作cf.edges()[0]
            源节点, 目标节点, 边标签 = 示例边
            print(f"- 示例边: {源节点} --[{边标签}]--> {目标节点}")
            
            # 尝试删除边（使用私有方法）
            try:
                边操作cf._drop_edge(源节点, 目标节点, 边标签)
                print(f"- 删除边: {源节点} --[{边标签}]--> {目标节点}")
                print(f"- 删除前边数: {原始边数}")
                print(f"- 删除后边数: {len(边操作cf.edges())}")
            except Exception as e:
                print(f"- 删除边失败: {e}")
        
        # 9.7 单节点调用操作
        print("\n9.7 单节点调用操作")
        
        # 获取函数的调用信息
        if cf.fnames:
            示例函数 = list(cf.fnames)[0]
            函数调用 = cf.calls_by_func()
            
            if 示例函数 in 函数调用:
                调用集合 = 函数调用[示例函数]
                print(f"- 函数 '{示例函数}' 的调用数: {len(调用集合)}")
                
                if 调用集合:
                    示例调用 = next(iter(调用集合))
                    print(f"- 示例调用ID: {示例调用.hid}")
                    print(f"- 调用操作: {示例调用.op.name}")
                    print(f"- 调用输入: {list(示例调用.inputs.keys())}")
                    print(f"- 调用输出: {list(示例调用.outputs.keys())}")
                    
                    # 获取函数调用表
                    try:
                        调用表 = cf.get_func_table(示例函数)
                        print(f"- 函数调用表形状: {调用表.shape}")
                        if not 调用表.empty:
                            print("- 调用表列名:", list(调用表.columns))
                    except Exception as e:
                        print(f"- 获取调用表失败: {e}")
        
        # 9.8 单节点验证和检查
        print("\n9.8 单节点验证和检查")
        
        # 验证节点的完整性
        验证cf = 删除cf.copy()
        
        try:
            验证cf._check()
            print("- ✅ ComputationFrame 完整性验证通过")
        except Exception as e:
            print(f"- ❌ ComputationFrame 完整性验证失败: {e}")
        
        # 检查节点统计
        if 验证cf.vnames:
            变量统计 = 验证cf.get_var_stats()
            print(f"- 变量统计表形状: {变量统计.shape}")
            if not 变量统计.empty:
                print(f"- 平均引用数: {变量统计['num_values'].mean():.2f}")
        
        if 验证cf.fnames:
            函数统计 = 验证cf.get_func_stats()
            print(f"- 函数统计表形状: {函数统计.shape}")
            if not 函数统计.empty:
                print(f"- 平均调用数: {函数统计['num_calls'].mean():.2f}")
        
        # 9.9 单节点信息查看
        print("\n9.9 单节点信息查看")
        
        # 查看具体节点的详细信息
        if 验证cf.vnames:
            示例变量 = list(验证cf.vnames)[0]
            print(f"- 变量 '{示例变量}' 的详细信息:")
            try:
                验证cf.var_info(示例变量)
            except Exception as e:
                print(f"  获取变量信息失败: {e}")
        
        if 验证cf.fnames:
            示例函数 = list(验证cf.fnames)[0]
            print(f"- 函数 '{示例函数}' 的详细信息:")
            try:
                验证cf.func_info(示例函数)
            except Exception as e:
                print(f"  获取函数信息失败: {e}")
        
        # 总结单节点操作
        print("\n9.10 单节点操作总结")
        print("✅ 已演示的单节点操作:")
        单节点操作列表 = [
            "节点查询 - 基本信息、邻居、边、值",
            "节点增加 - 新变量、新数据、新引用",
            "节点修改 - 重命名、属性更新",
            "引用操作 - 添加引用、移动引用",
            "节点删除 - 变量删除、函数删除",
            "边操作 - 边查询、边删除",
            "调用操作 - 调用查询、调用表获取",
            "节点验证 - 完整性检查、统计信息",
            "信息查看 - 详细信息、调试输出"
        ]
        
        for i, 操作 in enumerate(单节点操作列表, 1):
            print(f"  {i}. {操作}")
        
        print(f"\n📊 单节点操作统计:")
        print(f"- 最终变量节点数: {len(验证cf.vnames)}")
        print(f"- 最终函数节点数: {len(验证cf.fnames)}")
        print(f"- 最终边数: {len(验证cf.edges())}")
        
        return 验证cf
    
    def 运行完整演示(self):
        """运行完整的 ComputationFrame 操作演示"""
        print("🚀 ComputationFrame 综合操作演示开始")
        print("本演示将从基础到高级，展示 ComputationFrame 的各种操作")
        
        try:
            # 第1阶段：基础操作
            cf1 = self.第1阶段_基础操作()
            
            # 第2阶段：遍历操作
            cf2 = self.第2阶段_遍历操作(cf1)
            
            # 第3阶段：查找操作
            cf3 = self.第3阶段_查找操作(cf2)
            
            # 第4阶段：删除操作
            cf4 = self.第4阶段_删除操作(cf3)
            
            # 第5阶段：增加操作
            cf5 = self.第5阶段_增加操作(cf4)
            
            # 第6阶段：修改操作
            cf6 = self.第6阶段_修改操作(cf5)
            
            # 第7阶段：替换操作
            cf7 = self.第7阶段_替换操作(cf6)
            
            # 第8阶段：高级操作
            cf8 = self.第8阶段_高级操作(cf7)
            
            # 第9阶段：单节点操作
            final_cf = self.第9阶段_单节点操作(cf8)
            
            # 总结
            self.打印分隔线("演示总结")
            print("🎉 ComputationFrame 综合操作演示完成！")
            print("\n📊 演示成果:")
            print(f"- 最终图节点数: {len(final_cf.nodes)}")
            print(f"- 最终图变量数: {len(final_cf.vnames)}")
            print(f"- 最终图函数数: {len(final_cf.fnames)}")
            print(f"- 最终图边数: {len(final_cf.edges())}")
            
            print("\n✅ 已演示的功能:")
            演示功能列表 = [
                "ComputationFrame 创建和基本属性查看",
                "节点和边的遍历操作",
                "复杂查找和过滤操作",
                "节点删除和批量删除",
                "图扩展和合并操作",
                "节点重命名和结构修改",
                "计算流程替换和重构",
                "图优化和性能分析",
                "单节点细粒度增删查改操作"
            ]
            
            for i, 功能 in enumerate(演示功能列表, 1):
                print(f"  {i}. {功能}")
            
            print("\n🔧 使用的 ComputationFrame 核心方法:")
            核心方法列表 = [
                "cf.expand_back/expand_forward/expand_all - 图扩展",
                "cf.copy/select_nodes/drop_node - 图操作",
                "cf.rename/merge_vars/cleanup - 图修改",
                "cf.upstream/downstream/midstream - 方向性查询",
                "cf.get_history_df/get_func_table - 历史分析",
                "cf.ops/refs_by_var/calls_by_func - 数据访问",
                "cf | cf2 / cf & cf2 - 集合操作",
                "cf.get_reachable_nodes - 可达性分析",
                "cf._add_var/drop_var/rename_var - 单变量操作",
                "cf.add_ref/drop_ref/get_var_values - 引用管理",
                "cf.in_neighbors/out_neighbors/in_edges/out_edges - 邻居查询",
                "cf._add_edge/_drop_edge - 边操作（私有方法）",
                "cf.var_info/func_info/_check - 节点信息和验证"
            ]
            
            for 方法 in 核心方法列表:
                print(f"  - {方法}")
            
            return final_cf
            
        except Exception as e:
            print(f"\n❌ 演示过程中出现错误: {e}")
            import traceback
            print("详细错误信息:")
            traceback.print_exc()
            return None

def main():
    """主函数：运行 ComputationFrame 综合操作演示"""
    demo = ComputationFrameDemo()
    final_cf = demo.运行完整演示()
    
    if final_cf is not None:
        print(f"\n📈 最终图描述:")
        print(final_cf.get_graph_desc())
        
        print(f"\n💡 建议下一步:")
        print("1. 尝试使用 final_cf.draw() 可视化计算图")
        print("2. 使用 final_cf.df() 提取具体数据进行分析")
        print("3. 使用 final_cf.info() 查看详细的图信息")
        print("4. 探索更复杂的图操作和查询功能")

if __name__ == '__main__':
    main() 
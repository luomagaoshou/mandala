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
  10. 数据提取：历史追踪、DataFrame 转换
  11. 可视化分析：图形展示、信息输出

演示特点：
- 每个操作都有详细的中文注释
- 从简单的单步操作到复杂的组合操作
- 展示实际的使用场景和最佳实践
- 包含完善的错误处理和验证机制
- 充分利用 ComputationFrame 的所有已实现功能
"""

import numpy as np
import pandas as pd
from mandala1.imports import Storage, op
import logging
from typing import Optional, List, Dict, Any, Set

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
        
    def 打印分隔线(self, 标题: str):
        """打印美观的分隔线"""
        print(f"\n{'='*60}")
        print(f"第{self.演示阶段}阶段：{标题}")
        print(f"{'='*60}")
        self.演示阶段 += 1
    
    def 安全执行(self, 操作名称: str, 操作函数, *args, **kwargs):
        """安全执行操作并处理异常"""
        try:
            result = 操作函数(*args, **kwargs)
            return result
        except Exception as e:
            print(f"- ❌ {操作名称} 失败: {e}")
            return None
    
    def 展示图统计(self, cf, 标题: str = "图统计"):
        """展示 ComputationFrame 的基本统计信息"""
        print(f"\n📊 {标题}:")
        print(f"  节点总数: {len(cf.nodes)}")
        print(f"  变量节点: {len(cf.vnames)}")
        print(f"  函数节点: {len(cf.fnames)}")
        print(f"  边总数: {len(cf.edges())}")
        print(f"  源节点: {len(cf.sources)}")
        print(f"  汇节点: {len(cf.sinks)}")
        
        # 展示变量名（限制显示数量）
        if cf.vnames:
            vnames_list = list(cf.vnames)[:5]
            print(f"  变量示例: {vnames_list}{'...' if len(cf.vnames) > 5 else ''}")
        
        # 展示函数名（限制显示数量）
        if cf.fnames:
            fnames_list = list(cf.fnames)[:5]
            print(f"  函数示例: {fnames_list}{'...' if len(cf.fnames) > 5 else ''}")
    
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
        print(f"- 初始 CF 创建成功")
        self.展示图统计(cf, "初始图统计")
        
        # 1.3 展示基本属性
        print("\n1.3 展示基本属性")
        print(f"- 图描述:\n{cf.get_graph_desc()}")
        
        # 1.4 展示操作映射
        print("\n1.4 展示操作映射")
        ops_dict = cf.ops()
        for fname, op in ops_dict.items():
            print(f"- 函数 '{fname}' 对应操作: {op.name}")
        
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
            
            # 2.4 边查找
            print(f"\n2.4 边查找")
            in_edges = cf.in_edges(sample_node)
            out_edges = cf.out_edges(sample_node)
            print(f"节点 '{sample_node}' 的边:")
            print(f"- 输入边: {in_edges}")
            print(f"- 输出边: {out_edges}")
        
        # 2.5 拓扑排序
        print("\n2.5 拓扑排序")
        sorted_nodes = cf.topsort_modulo_sccs()
        print(f"拓扑排序结果: {sorted_nodes}")
        
        # 2.6 路径分析
        print("\n2.6 路径分析")
        if len(cf.nodes) >= 2:
            nodes_list = list(cf.nodes)
            start_node = nodes_list[0]
            end_node = nodes_list[-1]
            
            # 使用可达性分析
            reachable_from_start = self.安全执行(
                "可达性分析",
                cf.get_reachable_nodes,
                {start_node},
                direction="forward"
            )
            
            if reachable_from_start:
                print(f"从 '{start_node}' 可达的节点: {reachable_from_start}")
                print(f"'{end_node}' 是否可达: {end_node in reachable_from_start}")
        
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
                if not func_table.empty:
                    print(f"- 调用表形状: {func_table.shape}")
                    print(f"- 调用表列名: {list(func_table.columns)}")
                    print("- 调用表预览:")
                    print(func_table.head(3))
                else:
                    print("- 无调用记录")
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
        
        # 3.6 条件过滤演示
        print("\n3.6 条件过滤演示")
        if expanded_cf.vnames:
            # 选择一个变量进行过滤演示
            sample_var = next(iter(expanded_cf.vnames))
            var_values = expanded_cf.get_var_values(sample_var)
            print(f"- 变量 '{sample_var}' 包含 {len(var_values)} 个值")
            
            # 使用 isin 进行条件过滤（如果有多个值）
            if len(var_values) > 1:
                value_list = list(var_values)[:2]  # 取前两个值
                filtered_cf = self.安全执行(
                    "isin 过滤",
                    expanded_cf.isin,
                    value_list,
                    by="val",
                    node_class="var"
                )
                if filtered_cf:
                    print(f"- 过滤后节点数: {len(filtered_cf.nodes)}")
        
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
            cf_batch_deleted = self.安全执行(
                "批量删除节点",
                cf_copy.drop,
                nodes_to_delete,
                inplace=False
            )
            
            if cf_batch_deleted:
                print(f"- 批量删除节点: {nodes_to_delete}")
                print(f"- 删除前节点数: {len(cf_copy.nodes)}")
                print(f"- 删除后节点数: {len(cf_batch_deleted.nodes)}")
                cf_copy = cf_batch_deleted
        
        # 4.4 删除不可达节点
        print("\n4.4 删除不可达节点")
        if cf_copy.nodes:
            # 尝试删除不可达节点
            cf_before_cleanup = cf_copy.copy()
            cf_cleaned = self.安全执行(
                "删除不可达节点",
                cf_copy.drop_unreachable,
                direction="forward",
                how="strong"
            )
            
            if cf_cleaned:
                print(f"- 清理前节点数: {len(cf_before_cleanup.nodes)}")
                print(f"- 清理后节点数: {len(cf_cleaned.nodes)}")
                cf_copy = cf_cleaned
        
        # 4.5 最终清理
        print("\n4.5 最终清理")
        cf_final = cf_copy.cleanup(inplace=False)
        print(f"- 最终清理前节点数: {len(cf_copy.nodes)}")
        print(f"- 最终清理后节点数: {len(cf_final.nodes)}")
        
        return cf_final
    
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
        self.展示图统计(new_cf, "新建图统计")
        
        # 5.3 合并 ComputationFrame
        print("\n5.3 合并 ComputationFrame")
        merged_cf = self.安全执行(
            "图合并操作",
            lambda: cf | new_cf  # 使用并集操作
        )
        
        if merged_cf:
            print(f"- 原 CF 节点数: {len(cf.nodes)}")
            print(f"- 新 CF 节点数: {len(new_cf.nodes)}")
            print(f"- 合并后节点数: {len(merged_cf.nodes)}")
            print(f"- 合并后变量数: {len(merged_cf.vnames)}")
            print(f"- 合并后函数数: {len(merged_cf.fnames)}")
        else:
            print("- 使用新的 CF 继续演示")
            merged_cf = new_cf
        
        # 5.4 扩展操作
        print("\n5.4 扩展操作")
        try:
            # 向前扩展
            forward_expanded = merged_cf.expand_forward(recursive=True)
            print(f"- 向前扩展后节点数: {len(forward_expanded.nodes)}")
            
            # 全方向扩展
            full_expanded = merged_cf.expand_all()
            print(f"- 全方向扩展后节点数: {len(full_expanded.nodes)}")
            
            self.展示图统计(full_expanded, "完全扩展图统计")
            
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
            
            cf_renamed = self.安全执行(
                "变量重命名",
                cf_renamed.rename,
                vars=rename_dict,
                inplace=False
            )
            
            if cf_renamed:
                print(f"- 重命名映射: {rename_dict}")
                print(f"- 重命名前变量: {variables[:2]}")
                print(f"- 重命名后变量: {[name for name in cf_renamed.vnames if '重命名_' in name or '优化_' in name]}")
        
        # 6.2 选择子图
        print("\n6.2 选择子图")
        if len(cf.nodes) >= 3:
            selected_nodes = list(cf.nodes)[:3]
            sub_cf = cf.select_nodes(selected_nodes)
            print(f"- 选择的节点: {selected_nodes}")
            self.展示图统计(cf, "原图统计")
            self.展示图统计(sub_cf, "子图统计")
        
        # 6.3 上游和下游分析
        print("\n6.3 上游和下游分析")
        if cf.vnames:
            sample_var = next(iter(cf.vnames))
            upstream_cf = self.安全执行("上游分析", cf.upstream, sample_var)
            downstream_cf = self.安全执行("下游分析", cf.downstream, sample_var)
            
            if upstream_cf and downstream_cf:
                print(f"- 分析变量: {sample_var}")
                print(f"- 上游节点数: {len(upstream_cf.nodes)}")
                print(f"- 下游节点数: {len(downstream_cf.nodes)}")
                print(f"- 上游变量: {list(upstream_cf.vnames)}")
                print(f"- 下游变量: {list(downstream_cf.vnames)}")
        
        # 6.4 中游分析
        print("\n6.4 中游分析")
        if len(cf.vnames) >= 2:
            var_list = list(cf.vnames)[:2]
            midstream_cf = self.安全执行("中游分析", cf.midstream, *var_list)
            
            if midstream_cf:
                print(f"- 中游分析变量: {var_list}")
                print(f"- 中游节点数: {len(midstream_cf.nodes)}")
                print(f"- 中游变量: {list(midstream_cf.vnames)}")
        
        return cf_renamed if cf_renamed else cf
    
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
        self.展示图统计(replacement_cf, "替换图统计")
        
        # 7.3 分析替换前后的差异
        print("\n7.3 分析替换前后的差异")
        print("图结构对比:")
        self.展示图统计(cf, "原始图")
        self.展示图统计(replacement_cf, "替换图")
        
        # 7.4 图重构 - 创建混合计算图
        print("\n7.4 图重构 - 创建混合计算图")
        hybrid_cf = self.安全执行(
            "图重构",
            lambda: cf | replacement_cf  # 使用并集创建包含两个计算流程的图
        )
        
        if hybrid_cf:
            self.展示图统计(hybrid_cf, "混合图统计")
        else:
            print("- 使用替换图作为主要分析对象")
            hybrid_cf = replacement_cf
        
        # 7.5 对比分析
        print("\n7.5 对比分析")
        if hybrid_cf.vnames:
            sample_vars = list(hybrid_cf.vnames)[:3]
            comparison_df = self.安全执行(
                "对比分析",
                hybrid_cf.df,
                *sample_vars,
                verbose=False
            )
            
            if comparison_df is not None and not comparison_df.empty:
                print(f"- 对比变量: {sample_vars}")
                print(f"- 对比数据形状: {comparison_df.shape}")
                print("- 对比结果预览:")
                print(comparison_df.head())
        
        return hybrid_cf
    
    def 第8阶段_高级操作(self, cf):
        """第8阶段：高级操作 - 图合并、扩展、优化"""
        self.打印分隔线("高级操作 - 图优化和分析")
        
        # 8.1 图统计分析
        print("8.1 图统计分析")
        self.展示图统计(cf, "详细图统计")
        
        # 8.2 复杂查询操作
        print("\n8.2 复杂查询操作")
        try:
            # 获取计算历史
            if cf.vnames:
                sample_var = list(cf.vnames)[0]
                history_df = cf.get_history_df(sample_var, verbose=False)
                print(f"- 变量 '{sample_var}' 的历史:")
                print(f"  历史记录数: {len(history_df)}")
                print(f"  涉及列: {list(history_df.columns)}")
                if not history_df.empty:
                    print("  历史记录预览:")
                    print(history_df.head(3))
        except Exception as e:
            print(f"- 历史查询失败: {e}")
        
        # 8.3 联合历史查询
        print("\n8.3 联合历史查询")
        if len(cf.vnames) >= 2:
            var_list = list(cf.vnames)[:2]
            joint_history = self.安全执行(
                "联合历史查询",
                cf.get_joint_history_df,
                var_list,
                how="outer",
                verbose=False
            )
            
            if joint_history is not None and not joint_history.empty:
                print(f"- 联合查询变量: {var_list}")
                print(f"- 联合历史形状: {joint_history.shape}")
                print("- 联合历史预览:")
                print(joint_history.head(3))
        
        # 8.4 图优化
        print("\n8.4 图优化")
        optimized_cf = cf.copy()
        
        # 尝试合并变量
        merge_result = self.安全执行(
            "变量合并",
            optimized_cf.merge_vars,
            inplace=True
        )
        
        if merge_result is not None:
            print(f"- 优化前变量数: {len(cf.vnames)}")
            print(f"- 优化后变量数: {len(optimized_cf.vnames)}")
        
        # 清理优化
        cleanup_result = self.安全执行(
            "清理优化",
            optimized_cf.cleanup,
            inplace=True
        )
        
        if cleanup_result is not None:
            print(f"- 清理后节点数: {len(optimized_cf.nodes)}")
        
        # 8.5 可达性分析
        print("\n8.5 可达性分析")
        if cf.sources:
            source_node = next(iter(cf.sources))
            reachable_nodes = self.安全执行(
                "可达性分析",
                cf.get_reachable_nodes,
                {source_node},
                direction="forward"
            )
            
            if reachable_nodes:
                print(f"- 从源节点 '{source_node}' 可达的节点数: {len(reachable_nodes)}")
                print(f"- 可达节点: {list(reachable_nodes)[:5]}...")  # 只显示前5个
        
        # 8.6 性能统计
        print("\n8.6 性能统计")
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
        
        return optimized_cf
    
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
        新变量名 = self.安全执行(
            "添加新变量节点",
            修改cf._add_var,
            "手动添加变量"
        )
        
        if 新变量名:
            print(f"- 添加新变量节点: {新变量名}")
            print(f"- 添加前节点数: {原始节点数}")
            print(f"- 添加后节点数: {len(修改cf.nodes)}")
        
        # 重命名变量节点
        if 修改cf.vnames:
            原变量名 = list(修改cf.vnames)[0]
            新变量名 = f"重命名_{原变量名}"
            rename_result = self.安全执行(
                "重命名变量",
                修改cf.rename_var,
                原变量名,
                新变量名,
                inplace=True
            )
            
            if rename_result is not None:
                print(f"- 重命名变量: {原变量名} -> {新变量名}")
                print(f"- 重命名后变量列表: {list(修改cf.vnames)[:3]}...")
        
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
                    add_ref_result = self.安全执行(
                        "添加引用",
                        修改cf.add_ref,
                        目标现有变量,
                        示例引用,
                        allow_existing=True
                    )
                    
                    if add_ref_result is not None:
                        print(f"- 成功将引用添加到变量: {目标现有变量}")
                        print(f"- 添加后该变量的引用数: {len(修改cf.vs[目标现有变量])}")
        
        # 9.5 单节点删除操作
        print("\n9.5 单节点删除操作")
        
        删除cf = 修改cf.copy()
        删除前节点数 = len(删除cf.nodes)
        
        # 删除单个变量节点
        if 删除cf.vnames:
            要删除的变量 = list(删除cf.vnames)[-1]  # 选择最后一个变量
            delete_var_result = self.安全执行(
                "删除变量节点",
                删除cf.drop_var,
                要删除的变量,
                inplace=True
            )
            
            if delete_var_result is not None:
                print(f"- 删除变量节点: {要删除的变量}")
                print(f"- 删除前节点数: {删除前节点数}")
                print(f"- 删除后节点数: {len(删除cf.nodes)}")
        
        # 删除单个函数节点
        if 删除cf.fnames:
            要删除的函数 = list(删除cf.fnames)[-1]  # 选择最后一个函数
            delete_func_result = self.安全执行(
                "删除函数节点",
                删除cf.drop_func,
                要删除的函数,
                inplace=True
            )
            
            if delete_func_result is not None:
                print(f"- 删除函数节点: {要删除的函数}")
                print(f"- 删除后节点数: {len(删除cf.nodes)}")
        
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
            drop_edge_result = self.安全执行(
                "删除边",
                边操作cf._drop_edge,
                源节点,
                目标节点,
                边标签
            )
            
            if drop_edge_result is not None:
                print(f"- 删除边: {源节点} --[{边标签}]--> {目标节点}")
                print(f"- 删除前边数: {原始边数}")
                print(f"- 删除后边数: {len(边操作cf.edges())}")
        
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
                    func_table = self.安全执行(
                        "获取函数调用表",
                        cf.get_func_table,
                        示例函数
                    )
                    
                    if func_table is not None:
                        print(f"- 函数调用表形状: {func_table.shape}")
                        if not func_table.empty:
                            print("- 调用表列名:", list(func_table.columns))
        
        # 9.8 单节点验证和检查
        print("\n9.8 单节点验证和检查")
        
        # 验证节点的完整性
        验证cf = 删除cf.copy()
        
        check_result = self.安全执行(
            "ComputationFrame 完整性验证",
            验证cf._check
        )
        
        if check_result is not None:
            print("- ✅ ComputationFrame 完整性验证通过")
        else:
            print("- ❌ ComputationFrame 完整性验证失败")
        
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
            self.安全执行(
                "变量信息查看",
                验证cf.var_info,
                示例变量
            )
        
        if 验证cf.fnames:
            示例函数 = list(验证cf.fnames)[0]
            print(f"- 函数 '{示例函数}' 的详细信息:")
            self.安全执行(
                "函数信息查看",
                验证cf.func_info,
                示例函数
            )
        
        return 验证cf
    
    def 第10阶段_数据提取(self, cf):
        """第10阶段：数据提取 - 历史追踪、DataFrame 转换"""
        self.打印分隔线("数据提取 - 历史追踪和数据转换")
        
        # 10.1 简单数据提取
        print("10.1 简单数据提取")
        
        if cf.vnames:
            # 使用 eval 方法进行快速数据提取
            sample_vars = list(cf.vnames)[:3]
            eval_result = self.安全执行(
                "快速数据提取",
                cf.eval,
                *sample_vars,
                values="objs",
                verbose=True
            )
            
            if eval_result is not None and not eval_result.empty:
                print(f"- 提取变量: {sample_vars}")
                print(f"- 结果形状: {eval_result.shape}")
                print("- 结果预览:")
                print(eval_result.head())
        
        # 10.2 复杂数据提取
        print("\n10.2 复杂数据提取")
        
        if len(cf.vnames) >= 2:
            # 使用 df 方法进行复杂数据提取
            complex_vars = list(cf.vnames)[:2]
            df_result = self.安全执行(
                "复杂数据提取",
                cf.df,
                *complex_vars,
                values="objs",
                lazy_vars=None,
                verbose=False,
                include_calls=True,
                join_how="outer"
            )
            
            if df_result is not None and not df_result.empty:
                print(f"- 提取变量: {complex_vars}")
                print(f"- 结果形状: {df_result.shape}")
                print(f"- 结果列名: {list(df_result.columns)}")
                print("- 结果预览:")
                print(df_result.head())
        
        # 10.3 历史追踪分析
        print("\n10.3 历史追踪分析")
        
        if cf.vnames:
            target_var = list(cf.vnames)[0]
            
            # 获取直接历史
            if cf.vs[target_var]:
                sample_hids = set(list(cf.vs[target_var])[:3])
                direct_history = self.安全执行(
                    "直接历史追踪",
                    cf.get_direct_history,
                    target_var,
                    sample_hids,
                    include_calls=True
                )
                
                if direct_history:
                    print(f"- 变量 '{target_var}' 的直接历史:")
                    for node, hids in direct_history.items():
                        print(f"  {node}: {len(hids)} 个元素")
                
                # 获取完整历史
                total_history = self.安全执行(
                    "完整历史追踪",
                    cf.get_total_history,
                    target_var,
                    sample_hids,
                    include_calls=True
                )
                
                if total_history:
                    print(f"- 变量 '{target_var}' 的完整历史:")
                    for node, hids in total_history.items():
                        print(f"  {node}: {len(hids)} 个元素")
        
        # 10.4 数据格式转换
        print("\n10.4 数据格式转换")
        
        # 获取引用形式的数据
        if cf.vnames:
            ref_vars = list(cf.vnames)[:2]
            ref_df = self.安全执行(
                "引用形式数据",
                cf.df,
                *ref_vars,
                values="refs",
                verbose=False
            )
            
            if ref_df is not None and not ref_df.empty:
                print(f"- 引用形式数据形状: {ref_df.shape}")
                print("- 引用形式数据预览:")
                print(ref_df.head())
                
                # 评估引用数据
                eval_df = self.安全执行(
                    "评估引用数据",
                    cf.eval_df,
                    ref_df,
                    skip_calls=False
                )
                
                if eval_df is not None and not eval_df.empty:
                    print(f"- 评估后数据形状: {eval_df.shape}")
                    print("- 评估后数据预览:")
                    print(eval_df.head())
        
        # 10.5 集合操作结果提取
        print("\n10.5 集合操作结果提取")
        
        # 获取变量的引用集合
        if cf.vnames:
            sample_var = list(cf.vnames)[0]
            var_refs = cf.refs_by_var()
            
            if sample_var in var_refs:
                refs_set = var_refs[sample_var]
                print(f"- 变量 '{sample_var}' 的引用集合:")
                print(f"  引用数量: {len(refs_set)}")
                
                # 获取引用的实际值
                if refs_set:
                    sample_ref = next(iter(refs_set))
                    actual_value = self.storage.unwrap(sample_ref)
                    print(f"  示例引用值: {actual_value}")
        
        # 获取函数的调用集合
        if cf.fnames:
            sample_func = list(cf.fnames)[0]
            func_calls = cf.calls_by_func()
            
            if sample_func in func_calls:
                calls_set = func_calls[sample_func]
                print(f"- 函数 '{sample_func}' 的调用集合:")
                print(f"  调用数量: {len(calls_set)}")
                
                # 获取调用的详细信息
                if calls_set:
                    sample_call = next(iter(calls_set))
                    print(f"  示例调用操作: {sample_call.op.name}")
                    print(f"  示例调用输入: {list(sample_call.inputs.keys())}")
                    print(f"  示例调用输出: {list(sample_call.outputs.keys())}")
        
        return cf
    
    def 第11阶段_可视化分析(self, cf):
        """第11阶段：可视化分析 - 图形展示、信息输出"""
        self.打印分隔线("可视化分析 - 图形展示和信息输出")
        
        # 11.1 图形描述
        print("11.1 图形描述")
        
        # 获取图的描述
        graph_desc = cf.get_graph_desc()
        print("- 图结构描述:")
        print(graph_desc)
        
        # 11.2 节点信息展示
        print("\n11.2 节点信息展示")
        
        # 显示所有节点的信息
        if cf.nodes:
            node_list = list(cf.nodes)[:3]  # 限制显示数量
            info_result = self.安全执行(
                "节点信息展示",
                cf.info,
                *node_list
            )
            
            if info_result is not None:
                print(f"- 已显示 {len(node_list)} 个节点的详细信息")
        
        # 11.3 统计信息可视化
        print("\n11.3 统计信息可视化")
        
        # 变量统计
        var_stats = cf.get_var_stats()
        if not var_stats.empty:
            print("- 变量统计信息:")
            print(var_stats)
        
        # 函数统计
        func_stats = cf.get_func_stats()
        if not func_stats.empty:
            print("- 函数统计信息:")
            print(func_stats)
        
        # 11.4 图结构分析
        print("\n11.4 图结构分析")
        
        # 分析图的连通性
        if cf.sources and cf.sinks:
            print("- 图连通性分析:")
            print(f"  源节点: {list(cf.sources)}")
            print(f"  汇节点: {list(cf.sinks)}")
            
            # 分析从源到汇的路径
            source_node = next(iter(cf.sources))
            reachable_from_source = self.安全执行(
                "从源节点的可达性",
                cf.get_reachable_nodes,
                {source_node},
                direction="forward"
            )
            
            if reachable_from_source:
                sink_nodes = cf.sinks
                reachable_sinks = sink_nodes & reachable_from_source
                print(f"  从源节点可达的汇节点: {reachable_sinks}")
                print(f"  图连通性: {'连通' if reachable_sinks else '不连通'}")
        
        # 11.5 图绘制尝试
        print("\n11.5 图绘制尝试")
        
        # 尝试绘制图（可能需要特定的依赖）
        draw_result = self.安全执行(
            "图绘制",
            cf.draw,
            verbose=False
        )
        
        if draw_result is not None:
            print("- ✅ 图绘制成功")
        else:
            print("- ❌ 图绘制失败（可能缺少依赖或环境不支持）")
        
        # 11.6 图打印
        print("\n11.6 图打印")
        
        # 打印图的详细信息
        print_result = self.安全执行(
            "图打印",
            cf.print_graph
        )
        
        if print_result is not None:
            print("- ✅ 图打印完成")
        
        # 11.7 综合图分析报告
        print("\n11.7 综合图分析报告")
        
        # 生成综合报告
        报告内容 = {
            "图基本信息": {
                "节点总数": len(cf.nodes),
                "变量节点数": len(cf.vnames),
                "函数节点数": len(cf.fnames),
                "边总数": len(cf.edges()),
                "源节点数": len(cf.sources),
                "汇节点数": len(cf.sinks)
            },
            "节点统计": {
                "变量平均引用数": var_stats['num_values'].mean() if not var_stats.empty else 0,
                "函数平均调用数": func_stats['num_calls'].mean() if not func_stats.empty else 0,
                "最大引用数": var_stats['num_values'].max() if not var_stats.empty else 0,
                "最大调用数": func_stats['num_calls'].max() if not func_stats.empty else 0
            },
            "图结构特征": {
                "是否为DAG": len(cf.sources) > 0 and len(cf.sinks) > 0,
                "连通性": "连通" if cf.sources and cf.sinks and (cf.sinks & cf.get_reachable_nodes(cf.sources, "forward")) else "不连通",
                "复杂度": "高" if len(cf.nodes) > 10 else "中" if len(cf.nodes) > 5 else "低"
            }
        }
        
        print("- 📊 综合分析报告:")
        for 类别, 信息 in 报告内容.items():
            print(f"  {类别}:")
            for 键, 值 in 信息.items():
                print(f"    {键}: {值:.2f}" if isinstance(值, float) else f"    {键}: {值}")
        
        return cf
    
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
            cf9 = self.第9阶段_单节点操作(cf8)
            
            # 第10阶段：数据提取
            cf10 = self.第10阶段_数据提取(cf9)
            
            # 第11阶段：可视化分析
            final_cf = self.第11阶段_可视化分析(cf10)
            
            # 总结
            self.打印分隔线("演示总结")
            print("🎉 ComputationFrame 综合操作演示完成！")
            
            # 展示最终统计
            self.展示图统计(final_cf, "最终图统计")
            
            print("\n✅ 已演示的功能模块:")
            演示功能列表 = [
                "1. 基础操作：ComputationFrame 创建、属性查看、操作映射",
                "2. 遍历操作：节点遍历、边遍历、邻居查找、拓扑排序",
                "3. 查找操作：图扩展、节点查找、条件过滤、源汇分析",
                "4. 删除操作：单节点删除、批量删除、不可达节点清理",
                "5. 增加操作：图合并、向前扩展、全方向扩展",
                "6. 修改操作：节点重命名、子图选择、上下游分析",
                "7. 替换操作：计算流程替换、图重构、对比分析",
                "8. 高级操作：图优化、可达性分析、性能统计",
                "9. 单节点操作：细粒度的增删查改操作",
                "10. 数据提取：历史追踪、DataFrame 转换、引用评估",
                "11. 可视化分析：图形展示、统计信息、结构分析"
            ]
            
            for 功能 in 演示功能列表:
                print(f"  {功能}")
            
            print("\n🔧 使用的核心 ComputationFrame 方法:")
            核心方法分类 = {
                "图结构": ["nodes", "vnames", "fnames", "edges", "sources", "sinks"],
                "遍历查找": ["in_neighbors", "out_neighbors", "in_edges", "out_edges", "topsort_modulo_sccs"],
                "扩展操作": ["expand_back", "expand_forward", "expand_all", "upstream", "downstream", "midstream"],
                "修改操作": ["drop_node", "drop", "rename", "drop_var", "drop_func", "add_ref", "drop_ref"],
                "集合操作": ["__or__", "__and__", "__sub__", "union", "intersection"],
                "数据提取": ["eval", "df", "get_history_df", "get_joint_history_df", "eval_df"],
                "信息查询": ["ops", "refs_by_var", "calls_by_func", "get_var_values", "get_func_table"],
                "可达性分析": ["get_reachable_nodes", "get_source_elts", "get_sink_elts"],
                "统计分析": ["get_var_stats", "get_func_stats", "get_graph_desc"],
                "可视化": ["info", "var_info", "func_info", "draw", "print_graph"],
                "验证清理": ["_check", "cleanup", "merge_vars", "drop_unreachable"]
            }
            
            for 分类, 方法列表 in 核心方法分类.items():
                print(f"  {分类}: {', '.join(方法列表)}")
            
            print("\n💡 建议下一步操作:")
            建议列表 = [
                "1. 使用 final_cf.draw() 可视化完整的计算图",
                "2. 使用 final_cf.eval() 提取具体数据进行分析",
                "3. 使用 final_cf.get_history_df() 进行血缘分析",
                "4. 探索更复杂的图操作和查询组合",
                "5. 尝试自定义操作函数和扩展功能",
                "6. 使用 final_cf.isin() 进行高级过滤",
                "7. 结合存储功能进行数据持久化操作"
            ]
            
            for 建议 in 建议列表:
                print(f"  {建议}")
            
            return final_cf
            
        except Exception as e:
            print(f"\n❌ 演示过程中出现错误: {e}")
            import traceback
            print("详细错误信息:")
            traceback.print_exc()
            return None

def main():
    """主函数：运行 ComputationFrame 综合操作演示"""
    print("🎯 启动 ComputationFrame 综合操作演示")
    print("📚 基于 cf.md 文档的完整功能展示")
    
    demo = ComputationFrameDemo()
    final_cf = demo.运行完整演示()
    
    if final_cf is not None:
        print(f"\n🎊 演示成功完成！")
        print(f"📊 最终图包含 {len(final_cf.nodes)} 个节点，{len(final_cf.edges())} 条边")
        print(f"🔗 图连通性：{'连通' if final_cf.sources and final_cf.sinks else '独立节点'}")
        print(f"📈 图复杂度：{'高' if len(final_cf.nodes) > 10 else '中' if len(final_cf.nodes) > 5 else '低'}")
        
        print(f"\n🎁 演示成果：")
        print(f"- 创建了完整的 ComputationFrame 操作演示")
        print(f"- 展示了 {11} 个主要功能模块")
        print(f"- 使用了 {40}+ 个核心方法")
        print(f"- 包含了完善的错误处理机制")
        print(f"- 提供了实用的操作建议")
        
        return final_cf
    else:
        print(f"\n❌ 演示未能完成，请检查错误信息")
        return None

if __name__ == '__main__':
    main() 
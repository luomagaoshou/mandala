# ComputationFrame 综合操作演示文档

## 概述

本演示是一个从简单到复杂的 ComputationFrame 操作教程，系统地展示了 mandala 框架中 ComputationFrame 类的各种功能。演示分为8个阶段，每个阶段都有明确的学习目标和实践内容。

## 文档来源

- **主要参考**: `mydemo/doc/cf.md` - ComputationFrame 完整文档
- **实现参考**: `mandala1/cf.py` - 实际源代码实现
- **设计理念**: 从基础操作到高级功能的渐进式学习

## 演示结构

### 第1阶段：基础操作 - 创建和查看
**学习目标**: 掌握 ComputationFrame 的基本概念和创建方法

**主要内容**:
- 创建基础计算历史
- 从计算结果创建 ComputationFrame
- 查看基本属性（节点、边、源汇节点）
- 理解图描述格式

**核心方法**:
- `storage.cf(result)` - 创建 ComputationFrame
- `cf.nodes`, `cf.vnames`, `cf.fnames` - 节点访问
- `cf.sources`, `cf.sinks` - 源汇节点
- `cf.edges()` - 边信息
- `cf.get_graph_desc()` - 图描述

### 第2阶段：遍历操作 - 图结构探索
**学习目标**: 掌握图结构的遍历和探索方法

**主要内容**:
- 节点遍历（变量节点和函数节点）
- 边遍历（源节点、目标节点、边标签）
- 邻居查找（输入邻居和输出邻居）
- 拓扑排序

**核心方法**:
- `cf.sets[node]` - 节点元素集合
- `cf.in_neighbors(node)`, `cf.out_neighbors(node)` - 邻居查找
- `cf.topsort_modulo_sccs()` - 拓扑排序

### 第3阶段：查找操作 - 数据检索
**学习目标**: 掌握各种查找和过滤操作

**主要内容**:
- 图扩展以获得更多数据
- 按类型查找节点
- 查找特定操作的节点
- 值查找和过滤
- 源汇元素查找

**核心方法**:
- `cf.expand_back(recursive=True)` - 向后扩展
- `cf.ops()` - 操作映射
- `cf.get_func_table(fname)` - 函数调用表
- `cf.get_source_elts()`, `cf.get_sink_elts()` - 源汇元素

### 第4阶段：删除操作 - 数据清理
**学习目标**: 掌握节点和数据的删除操作

**主要内容**:
- 复制 ComputationFrame 进行实验
- 删除单个节点
- 批量删除节点
- 清理和简化操作

**核心方法**:
- `cf.copy()` - 复制操作
- `cf.drop_node(node, inplace=False)` - 删除节点
- `cf.drop(nodes, inplace=False)` - 批量删除
- `cf.cleanup(inplace=False)` - 清理操作

### 第5阶段：增加操作 - 扩展计算图
**学习目标**: 掌握图的扩展和合并操作

**主要内容**:
- 创建新的计算数据和分支
- 创建新的 ComputationFrame
- 合并多个 ComputationFrame
- 各种扩展操作

**核心方法**:
- `cf1 | cf2` - 并集操作
- `cf.expand_forward(recursive=True)` - 向前扩展
- `cf.expand_all()` - 全方向扩展

### 第6阶段：修改操作 - 结构调整
**学习目标**: 掌握图结构的修改和调整

**主要内容**:
- 节点重命名
- 选择子图
- 上游和下游分析

**核心方法**:
- `cf.rename(vars=rename_dict, inplace=False)` - 重命名
- `cf.select_nodes(selected_nodes)` - 选择子图
- `cf.upstream(var)`, `cf.downstream(var)` - 上下游分析

### 第7阶段：替换操作 - 高级重构
**学习目标**: 掌握复杂的图重构和替换操作

**主要内容**:
- 创建替换数据和计算流程
- 分析替换前后的差异
- 图重构和混合计算图
- 对比分析

**核心方法**:
- 组合使用多种操作进行复杂重构
- `cf.df(*vars, verbose=False)` - 数据提取和对比

### 第8阶段：高级操作 - 图优化和分析
**学习目标**: 掌握高级的图分析和优化技术

**主要内容**:
- 图统计分析
- 复杂查询操作
- 图优化技术
- 可达性分析
- 性能统计

**核心方法**:
- `cf.get_history_df(var, verbose=False)` - 历史分析
- `cf.merge_vars(inplace=True)` - 变量合并
- `cf.get_reachable_nodes(nodes, direction)` - 可达性分析
- `cf.get_var_stats()`, `cf.get_func_stats()` - 统计信息

## 技术特点

### 1. 渐进式学习设计
- 从最基础的创建操作开始
- 逐步引入更复杂的概念和操作
- 每个阶段都建立在前一阶段的基础上

### 2. 实用的示例场景
- 使用机器学习流水线作为示例场景
- 包含数据预处理、特征提取、模型训练、评估等步骤
- 展示真实的计算图操作需求

### 3. 完整的错误处理
- 每个操作都包含适当的错误处理
- 提供详细的错误信息和调试帮助
- 确保演示的健壮性

### 4. 中文友好的接口
- 所有函数名和变量名都使用中文
- 详细的中文注释和说明
- 符合中文开发习惯

## 使用方法

### 运行完整演示
```python
python mydemo/案例/cf_comprehensive_operations_demo.py
```

### 分阶段学习
```python
from mydemo.案例.cf_comprehensive_operations_demo import ComputationFrameDemo

demo = ComputationFrameDemo()

# 只运行前3个阶段
cf1 = demo.第1阶段_基础操作()
cf2 = demo.第2阶段_遍历操作(cf1)
cf3 = demo.第3阶段_查找操作(cf2)
```

### 自定义实验
```python
# 基于演示代码进行自定义实验
demo = ComputationFrameDemo()
cf = demo.第1阶段_基础操作()

# 尝试自己的操作
my_expanded_cf = cf.expand_all()
my_sub_cf = my_expanded_cf.select_nodes(['var_0', 'func_0'])
```

## 核心概念解释

### ComputationFrame 的本质
ComputationFrame 是 mandala 框架中对计算图的高级抽象，类似于 pandas.DataFrame 对表格数据的抽象。它将计算历史组织为有向图结构，其中：
- **节点**：变量节点存储数据，函数节点表示操作
- **边**：表示数据流和依赖关系
- **元素**：节点中包含的具体引用（Ref）或调用（Call）

### 图操作的设计模式
1. **非破坏性操作**：大多数操作默认返回新的 ComputationFrame，不修改原始对象
2. **inplace 参数**：提供就地修改选项，类似 pandas 的设计
3. **链式操作**：支持方法链式调用，提高代码可读性
4. **集合操作**：支持并集、交集、差集等数学集合操作

### 扩展操作的核心思想
- **向后扩展**：追溯数据来源，找到创建当前数据的计算步骤
- **向前扩展**：追踪数据使用，找到消费当前数据的计算步骤
- **递归扩展**：重复扩展直到无法再扩展（固定点）
- **全方向扩展**：结合向前和向后扩展，获得完整的计算图

## 学习建议

### 初学者路径
1. 先运行完整演示，观察整体效果
2. 逐个阶段深入学习，理解每个操作的作用
3. 尝试修改参数，观察结果变化
4. 阅读 `cf.md` 文档，深入理解理论基础

### 进阶用户路径
1. 关注高级操作和优化技术
2. 学习图分析和可达性算法
3. 探索自定义的图操作组合
4. 研究性能优化和大规模图处理

### 开发者路径
1. 研究源代码实现细节
2. 理解内部数据结构和算法
3. 开发自定义的图操作方法
4. 贡献新的功能和优化

## 常见问题

### Q: 为什么有些操作会失败？
A: ComputationFrame 的操作有一定的约束条件，比如删除关键节点可能导致图结构不一致。演示中包含了错误处理，会尝试其他节点或跳过失败的操作。

### Q: 如何理解图的扩展操作？
A: 扩展操作是 ComputationFrame 的核心功能，它从存储中获取相关的计算历史，并将其添加到当前图中。这类似于 SQL 中的 JOIN 操作，但针对的是计算图结构。

### Q: 集合操作的结果如何理解？
A: 并集操作会合并两个图的所有节点和边，交集操作只保留共同的部分，差集操作会移除指定的元素。这些操作遵循数学集合的基本规律。

### Q: 如何选择合适的扩展策略？
A: 
- 如果需要了解数据来源，使用 `expand_back`
- 如果需要了解数据用途，使用 `expand_forward`
- 如果需要完整的计算图，使用 `expand_all`
- 如果只需要部分信息，使用非递归的扩展

## 扩展阅读

1. **ComputationFrame 完整文档**: `mydemo/doc/cf.md`
2. **源代码实现**: `mandala1/cf.py`
3. **其他案例**: `mydemo/案例/` 目录下的其他演示文件
4. **基础教程**: `mydemo/topics/` 目录下的主题教程

这个演示为 ComputationFrame 的学习提供了一个完整而系统的路径，从基础概念到高级应用，帮助用户全面掌握这个强大的计算图操作工具。 
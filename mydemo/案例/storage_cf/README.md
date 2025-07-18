# mandala框架Storage和ComputationFrame案例集合

## 概述

这个案例集合详细展示了mandala框架中Storage和ComputationFrame的工作原理，以及如何使用它们进行计算图的增删查改操作。

## 文件结构

```
storage_cf/
├── README.md                       # 本文档
├── 01_framework_capture_analysis.py  # 框架捕获原理分析
├── 02_cf_query_operations.py        # CF查询操作详解
├── 03_cf_add_operations.py          # CF增加操作详解
├── 04_cf_delete_operations.py       # CF删除操作详解
├── 05_cf_modify_operations.py       # CF修改操作详解
└── 06_comprehensive_demo.py         # 综合演示
```

## 案例内容

### 1. 框架捕获原理分析 (01_framework_capture_analysis.py)

**核心内容：**
- mandala框架的工作原理
- Storage如何捕获和存储计算历史
- ComputationFrame的构建过程
- 函数装饰器@op的作用机制

**主要功能演示：**
- 存储初始化和配置
- 计算历史的自动记录
- 引用对象的管理
- 计算图的构建

### 2. CF查询操作详解 (02_cf_query_operations.py)

**核心内容：**
- ComputationFrame的查询功能
- 数据提取和筛选
- 图结构遍历
- 统计信息获取

**主要功能演示：**
- 基础查询（节点、边、变量、函数）
- 数据框架生成 (df方法)
- 值过滤和选择
- 图结构分析

### 3. CF增加操作详解 (03_cf_add_operations.py)

**核心内容：**
- ComputationFrame的扩展功能
- 新节点和边的添加
- 图的联合操作
- 动态图构建

**主要功能演示：**
- 节点添加 (_add_var, _add_func)
- 图扩展 (expand_back, expand_forward, expand_all)
- 联合操作 (union, | 运算符)
- 从引用构造CF

### 4. CF删除操作详解 (04_cf_delete_operations.py)

**核心内容：**
- ComputationFrame的删除功能
- 节点和边的移除
- 图的过滤和清理
- 集合操作

**主要功能演示：**
- 节点删除 (drop_node, drop_var, drop_func)
- 元素删除 (drop_ref, drop_call)
- 过滤操作 (isin, 条件过滤)
- 清理操作 (cleanup, drop_unreachable)

### 5. CF修改操作详解 (05_cf_modify_operations.py)

**核心内容：**
- ComputationFrame的修改功能
- 节点重命名和移动
- 图的变换和优化
- 数据处理操作

**主要功能演示：**
- 重命名操作 (rename_var, rename)
- 移动操作 (move_ref)
- 合并操作 (merge_into, merge_vars)
- 应用操作 (apply, eval)

### 6. 综合演示 (06_comprehensive_demo.py)

**核心内容：**
- 完整的数据处理流水线
- 真实场景的应用示例
- 性能优化和最佳实践
- 实际问题解决方案

**主要功能演示：**
- 端到端的数据处理
- 计算图分析和优化
- 数据血缘追踪
- 调试和故障排查

## 使用方法

### 环境要求

```bash
# 确保已安装mandala框架
pip install mandala

# 或者如果使用本地开发版本
# 确保mandala目录在Python路径中
```

### 运行案例

```bash
# 运行单个案例
python 01_framework_capture_analysis.py

# 运行所有案例
python 02_cf_query_operations.py
python 03_cf_add_operations.py
python 04_cf_delete_operations.py
python 05_cf_modify_operations.py
python 06_comprehensive_demo.py
```

### 交互式使用

```python
# 在Python交互环境中使用
import sys
sys.path.append('path/to/mandala')

from mandala.imports import *
storage = Storage()

# 定义操作
@op(output_names=['result'])
def my_function(x: int) -> int:
    return x * 2

# 执行计算
with storage:
    result = my_function(5)

# 分析计算图
cf = storage.cf(my_function)
print(cf.df())
```

## 核心概念

### Storage (存储)

Storage是mandala框架的核心组件，负责：
- 自动捕获函数调用历史
- 缓存计算结果避免重复计算
- 管理引用对象的生命周期
- 提供计算图的构建接口

### ComputationFrame (计算框架)

ComputationFrame是计算图的表示，提供：
- 图结构的查询和遍历
- 数据的提取和转换
- 图的修改和优化
- 血缘追踪和依赖分析

### 关键特性

1. **透明性**: 只需@op装饰器即可开始使用
2. **自动化**: 自动记录计算历史和依赖关系
3. **灵活性**: 支持复杂的图操作和查询
4. **高效性**: 智能缓存避免重复计算
5. **可扩展性**: 支持大规模计算图操作

## 最佳实践

### 1. 函数设计

```python
# 好的做法：纯函数，明确的输入输出
@op(output_names=['processed_data'])
def process_data(raw_data: List[int]) -> List[int]:
    return [x * 2 for x in raw_data]

# 避免：有副作用的函数
@op(output_names=['result'])
def bad_function(x: int) -> int:
    print(f"Processing {x}")  # 副作用
    return x * 2
```

### 2. 存储管理

```python
# 使用with语句确保正确的存储上下文
with storage:
    result = my_function(input_data)

# 定期清理缓存
storage.cache_info()
storage.clear_cache()
```

### 3. 计算图分析

```python
# 分析计算图结构
cf = storage.cf(my_function)

# 检查图的完整性
cf._check()

# 优化图结构
cf_optimized = cf.cleanup().merge_vars()
```

### 4. 调试技巧

```python
# 查看计算历史
df = cf.df()
print(df)

# 追踪特定变量的血缘
history = cf.get_history_df('target_variable')

# 分析函数调用
func_table = cf.get_func_table('function_name')
```

## 常见问题

### Q: 如何处理大规模计算图？
A: 使用图的分割和清理功能，定期清理不必要的节点和引用。

### Q: 如何优化计算性能？
A: 利用Storage的缓存机制，避免重复计算，使用适当的数据结构。

### Q: 如何调试计算图？
A: 使用ComputationFrame的查询功能，分析数据流和依赖关系。

### Q: 如何扩展框架功能？
A: 继承Storage和ComputationFrame类，实现自定义的存储和分析功能。

## 进一步学习

1. 阅读mandala框架的官方文档
2. 研究Storage和ComputationFrame的源代码
3. 实践更复杂的计算图操作
4. 尝试与其他数据处理框架集成

## 贡献

如果您发现问题或有改进建议，请：
1. 提交Issue报告问题
2. 创建Pull Request贡献代码
3. 完善文档和示例

---

*这个案例集合旨在帮助用户深入理解mandala框架的工作原理和使用方法，通过实际示例学习如何有效地使用Storage和ComputationFrame进行计算图管理。* 
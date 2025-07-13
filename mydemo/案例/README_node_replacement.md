# 节点替换和参数修改功能演示

## 概述

本演示展示了如何使用 mandala 框架的 ComputationFrame 来实现以下核心功能：

1. **函数捕获**：从已运行的计算历史中捕获函数调用信息
2. **参数修改**：修改函数的输入参数
3. **新计算执行**：使用新参数重新执行函数
4. **节点替换**：将新结果替换原有节点并更新计算图

## 文件结构

```
mydemo/topics/
├── 11_node_replacement_demo.py    # 主要演示文件
├── test_node_replacement.py       # 测试文件
└── README_node_replacement.md     # 本说明文件
```

## 核心功能

### 1. 函数捕获

```python
# 从计算框架中获取函数信息
cf = storage.cf(result).expand_back(recursive=True)
calls_by_func = cf.calls_by_func()
```

**实现的功能**：
- 从 ComputationFrame 中提取已执行的函数
- 获取函数的调用历史和参数信息
- 支持递归扩展获取完整的计算图

### 2. 参数修改

```python
# 获取原始参数
original_call = next(iter(score_calls))
original_params = original_call.inputs

# 修改参数并重新执行
with storage:
    new_result = function(modified_params)
```

**实现的功能**：
- 提取函数的原始输入参数
- 支持修改任意参数值
- 保持其他参数不变

### 3. 新计算执行

```python
# 使用新参数重新执行函数
with storage:
    new_final_score = calculate_score(original_normalized_data, weight=new_weight)
```

**实现的功能**：
- 使用修改后的参数重新执行函数
- 自动记录新的计算历史
- 生成新的计算节点

### 4. 节点替换

```python
# 创建新的计算框架
new_cf = storage.cf(new_final_score).expand_back(recursive=True)

# 合并计算框架
combined_cf = original_cf | new_cf | modified_cf
```

**实现的功能**：
- 创建包含新计算的计算框架
- 合并多个计算框架
- 比较不同参数下的计算结果

## 使用的 ComputationFrame 核心功能

### 扩展功能
- `cf.expand_back(recursive=True)`: 递归扩展计算历史
- `cf.expand_forward()`: 向前扩展计算
- `cf.expand_all()`: 全方向扩展

### 查询功能
- `cf.get_func_table(fname)`: 获取函数调用表
- `cf.calls_by_func()`: 获取函数到调用的映射
- `cf.refs_by_var()`: 获取变量到引用的映射

### 集合操作
- `cf1 | cf2`: 计算框架并集操作
- `cf1 & cf2`: 计算框架交集操作
- `cf1 - cf2`: 计算框架差集操作

### 分析功能
- `cf.upstream(node)`: 获取上游计算
- `cf.downstream(node)`: 获取下游计算
- `cf.eval(*nodes)`: 数据提取和评估

## 运行演示

### 基本演示

```bash
python mydemo/topics/11_node_replacement_demo.py
```

### 运行测试

```bash
python mydemo/topics/test_node_replacement.py
```

## 演示输出

### 1. 创建初始计算历史
```
- 原始数据: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
- 平均值: 5.5
- 标准差: 2.87...
- 最终分数: -1.66...e-15
```

### 2. 捕获函数信息
```
- 计算框架结构:
ComputationFrame with:
    6 variable(s) (6 unique refs)
    4 operation(s) (4 unique calls)
```

### 3. 参数修改结果
```
- 将权重从 1.5 修改为 2.0
- 新的最终分数: -2.22...e-15
- 分数变化: -5.55...e-16
```

### 4. 计算框架比较
```
- 原始框架节点数: 10
- 新框架节点数: 4
- 合并后节点数: 10
```

## 技术特点

### 1. 完整的计算历史追踪
- 自动记录所有函数调用
- 支持递归扩展获取完整依赖图
- 保持计算的可重现性

### 2. 灵活的参数修改
- 支持修改任意函数参数
- 保持其他参数不变
- 支持复杂数据类型的参数

### 3. 高效的计算图操作
- 使用集合操作合并计算框架
- 支持上游下游分析
- 提供丰富的查询接口

### 4. 强大的数据提取能力
- 支持提取任意节点的数据
- 自动处理引用和对象转换
- 支持 DataFrame 格式输出

## 实际应用场景

### 1. 机器学习参数调优
```python
# 捕获已训练的模型
cf = storage.cf(trained_model).expand_back(recursive=True)

# 修改超参数重新训练
with storage:
    new_model = train_model(data, new_hyperparams)
```

### 2. 数据处理流水线优化
```python
# 捕获数据处理流程
cf = storage.cf(processed_data).expand_back(recursive=True)

# 修改处理参数
with storage:
    optimized_data = process_data(raw_data, optimized_params)
```

### 3. 算法性能比较
```python
# 合并不同算法的计算框架
combined_cf = algorithm1_cf | algorithm2_cf | algorithm3_cf

# 比较性能指标
performance_df = combined_cf.eval('accuracy', 'speed', 'memory')
```

## 注意事项

### 1. 数据类型兼容性
- 确保修改后的参数类型与原始参数兼容
- 复杂对象可能需要特殊处理

### 2. 计算图复杂度
- 大型计算图的扩展可能需要较长时间
- 可以使用 `verbose=True` 监控扩展过程

### 3. 内存使用
- 合并大量计算框架可能消耗较多内存
- 考虑使用分批处理或清理不需要的节点

## 总结

本演示展示了 mandala 框架强大的计算图操作能力，特别是：

1. **完整的函数捕获机制**：能够从计算历史中提取任意函数的调用信息
2. **灵活的参数修改能力**：支持修改函数参数并重新执行
3. **强大的节点替换功能**：能够生成新节点并更新计算图
4. **丰富的分析工具**：提供多种方式分析和比较计算结果

这些功能为机器学习、数据分析和算法研究提供了强大的工具支持，使得参数调优、实验比较和结果分析变得更加高效和直观。 
# ComputationFrame详解

ComputationFrame是Mandala框架的核心数据结构，提供了对保存在Storage中的计算历史的高级视图和操作能力。本文档详细介绍ComputationFrame的创建、结构和使用方法。

## ComputationFrame创建方法

有多种方法可以创建ComputationFrame：

### 1. 从结果对象创建

最直接的方法是从一个操作的结果创建ComputationFrame：

```python
from mandala.imports import *

@op
def add(a, b):
    return a + b

with Storage() as s:
    result = add(1, 2)
    
    # 从结果创建ComputationFrame
    cf = s.cf(result)
```

这将创建一个包含生成该结果的计算链的ComputationFrame。

### 2. 从操作创建

可以从操作本身创建ComputationFrame，这将包含该操作的所有调用：

```python
with Storage() as s:
    add(1, 2)
    add(3, 4)
    add(5, 6)
    
    # 从操作创建ComputationFrame
    cf = s.cf(add)
```

这将创建一个包含`add`操作的所有调用的ComputationFrame。

### 3. 从多个对象创建

可以从多个对象（结果或操作）创建ComputationFrame：

```python
@op
def multiply(a, b):
    return a * b

with Storage() as s:
    result1 = add(1, 2)
    result2 = multiply(3, 4)
    
    # 从多个对象创建ComputationFrame
    cf = s.cf([result1, result2])  # 从结果列表创建
    cf = s.cf([add, multiply])     # 从操作列表创建
```

### 4. 从字典创建

可以使用字典指定变量名称：

```python
with Storage() as s:
    result1 = add(1, 2)
    result2 = multiply(3, 4)
    
    # 使用自定义变量名创建ComputationFrame
    cf = s.cf({"sum": result1, "product": result2})
```

## 结构与属性

ComputationFrame由以下核心组件组成：

### 1. 节点（Nodes）

ComputationFrame有两种类型的节点：
- **变量节点（Variable Nodes）**：表示数据值
- **函数节点（Function Nodes）**：表示操作（@op装饰的函数）

```python
# 查看所有变量节点
print(cf.vnames)

# 查看所有函数节点
print(cf.fnames)

# 查看所有节点（变量和函数）
print(cf.nodes)
```

### 2. 边（Edges）

边表示节点之间的关系，通常是函数的输入和输出：

```python
# 获取所有边
edges = cf.edges()
print(edges)
```

边的格式为元组 `(source_node, target_node, label)`，其中`label`通常是参数名或输出名。

### 3. 引用（References）

ComputationFrame跟踪每个变量节点中包含的所有值：

```python
# 获取特定变量的所有值
values = cf.get_var_values("variable_name")
print(values)

# 获取所有变量及其值
var_values = cf.refs_by_var()
print(var_values)
```

### 4. 调用（Calls）

ComputationFrame跟踪每个函数节点关联的所有调用：

```python
# 获取特定函数的所有调用
calls = cf.calls_by_func()["function_name"]
print(calls)

# 获取所有函数及其调用
func_calls = cf.calls_by_func()
print(func_calls)
```

## 导航与查询

ComputationFrame提供了多种导航和查询计算图的方法：

### 1. 基本导航

```python
# 获取节点的输入邻居
in_neighbors = cf.in_neighbors("node_name")

# 获取节点的输出邻居
out_neighbors = cf.out_neighbors("node_name")

# 获取输入边
in_edges = cf.in_edges("node_name")

# 获取输出边
out_edges = cf.out_edges("node_name")
```

### 2. 计算图遍历

#### 上游遍历（向输入方向）

```python
# 获取上游计算图（生成给定节点的所有计算）
upstream_cf = cf.upstream("node_name")
```

`upstream`方法找出所有为指定节点提供输入的计算路径。

#### 下游遍历（向输出方向）

```python
# 获取下游计算图（使用给定节点结果的所有计算）
downstream_cf = cf.downstream("node_name")
```

`downstream`方法找出所有使用指定节点值的计算路径。

#### 双向遍历

```python
# 获取包含指定节点上下游的计算图
midstream_cf = cf.midstream("node_name")
```

`midstream`方法结合了`upstream`和`downstream`，找出与指定节点相关的所有计算路径。

### 3. 遍历强度控制

上述所有遍历方法都支持`how`参数控制遍历的严格程度：

```python
# 强遍历：所有依赖必须存在
strong_upstream = cf.upstream("node_name", how="strong")

# 弱遍历：允许部分依赖
weak_upstream = cf.upstream("node_name", how="weak")
```

- **strong**：要求所有输入都存在于结果中
- **weak**：允许部分输入缺失

### 4. 计算历史

```python
# 获取单个变量的计算历史
history_df = cf.get_history_df("variable_name")

# 获取多个变量的联合历史
joint_history = cf.get_joint_history_df(["var1", "var2"])
```

这些方法返回变量的计算历史，包括创建这些变量的函数调用和相关参数。

## 与Pandas DataFrame的关系

ComputationFrame可以导出为pandas DataFrame，使分析更加便捷：

```python
# 获取计算框架的DataFrame表示
df = cf.df()
print(df)

# 选择特定列
df_subset = cf.df("input_var", "function_node", "output_var")
print(df_subset)

# 控制返回值类型
df_refs = cf.df(values="refs")  # 返回引用对象
df_objs = cf.df(values="objs")  # 返回实际值（默认）
```

生成的DataFrame表示如下：
- **列**：计算图中的变量和函数节点
- **行**：计算轨迹，每行表示一条完整或部分的计算路径

## 合并与分割操作

ComputationFrame支持集合操作，可以组合和细化计算图：

### 1. 合并操作

```python
# 使用union方法合并
merged_cf = ComputationFrame.union(cf1, cf2, cf3)

# 使用运算符合并
merged_cf = cf1 | cf2
```

### 2. 交集操作

```python
# 使用intersection方法
common_cf = ComputationFrame.intersection(cf1, cf2)

# 使用运算符
common_cf = cf1 & cf2
```

### 3. 差集操作

```python
# 获取在cf1中但不在cf2中的部分
diff_cf = cf1 - cf2
```

### 4. 选择操作

```python
# 选择特定节点
selected_cf = cf.select_nodes(["node1", "node2"])

# 选择特定子集
subset_cf = cf.select_subsets({"var1": {ref1, ref2}, "var2": {ref3}})
```

### 5. 节点操作

```python
# 重命名变量
renamed_cf = cf.rename(vars={"old_name": "new_name"})

# 删除节点
pruned_cf = cf.drop(["node_to_remove"])

# 合并节点
merged_nodes_cf = cf.merge({"var1", "var2"}, new_name="combined_var")
```

## 扩展计算图

ComputationFrame提供了强大的扩展方法，可以发现和添加相关计算：

### 1. expand_back

`expand_back`方法沿输入方向扩展计算图，查找创建当前变量的函数：

```python
# 简单扩展
cf.expand_back(inplace=True)

# 指定变量进行扩展
cf.expand_back("var_name", inplace=True)

# 递归扩展（直到找不到更多相关计算）
cf.expand_back(recursive=True, inplace=True)
```

### 2. expand_forward

`expand_forward`方法沿输出方向扩展计算图，查找使用当前变量的函数：

```python
# 简单扩展
cf.expand_forward(inplace=True)

# 指定变量进行扩展
cf.expand_forward("var_name", inplace=True)

# 递归扩展
cf.expand_forward(recursive=True, inplace=True)
```

### 3. expand_all

`expand_all`方法同时在两个方向扩展计算图，结合了`expand_back`和`expand_forward`：

```python
# 扩展所有可能的相关计算
cf.expand_all(inplace=True)

# 控制是否跳过已存在的调用
cf.expand_all(skip_existing=True, inplace=True)

# 详细输出扩展过程
cf.expand_all(verbose=True, inplace=True)
```

`expand_all`特别适合发现计算图的完整结构，通常是创建ComputationFrame后的首选操作。

## 计算图分析

ComputationFrame提供了多种分析计算图结构的工具：

### 1. 拓扑排序

```python
# 获取节点的拓扑排序（考虑循环）
ordered_nodes = cf.topsort_modulo_sccs()

# 对指定节点排序
sorted_nodes = cf.sort_nodes(["node1", "node2", "node3"])
```

### 2. 可达性分析

```python
# 找出从指定节点可达的所有节点
reachable = cf.get_reachable_nodes({"node1"}, direction="forward")

# 获取从特定状态可达的所有元素
reachable_elts = cf.get_reachable_elts(
    initial_state={"var1": {ref1, ref2}},
    direction="forward",
    how="strong"
)
```

### 3. 信息查询

```python
# 查看计算框架概要信息
cf.info()

# 查看特定节点信息
cf.info("node_name")

# 获取变量统计
var_stats = cf.get_var_stats()

# 获取函数统计
func_stats = cf.get_func_stats()
```

## 完整示例

以下是一个展示ComputationFrame主要功能的完整示例：

```python
from mandala.imports import *
import pandas as pd
import numpy as np

# 创建Storage
storage = Storage(db_path="computation_demo.db")

# 定义操作
@op
def load_data(source):
    print(f"Loading data from {source}")
    # 模拟数据加载
    return np.random.rand(10)

@op
def preprocess(data):
    print("Preprocessing data")
    return data * 2

@op
def analyze(data, method="mean"):
    print(f"Analyzing with method: {method}")
    if method == "mean":
        return data.mean()
    elif method == "sum":
        return data.sum()
    else:
        return None

@op(output_names=["value", "label"])
def classify(value):
    print(f"Classifying value: {value}")
    if value > 10:
        return value, "high"
    else:
        return value, "low"

# 执行计算链
with storage:
    # 执行两条不同的计算路径
    # 路径1: 加载 -> 预处理 -> 分析(mean)
    data1 = load_data("source1")
    processed1 = preprocess(data1)
    result1 = analyze(processed1, method="mean")
    
    # 路径2: 加载 -> 预处理 -> 分析(sum)
    data2 = load_data("source2")
    processed2 = preprocess(data2)
    result2 = analyze(processed2, method="sum")
    
    # 路径3: 分析结果 -> 分类
    value, label = classify(result2)

# 创建初始ComputationFrame
cf = storage.cf([result1, result2, value])

# 展示初始计算图
print("初始计算图:")
cf.info()

# 扩展计算图
print("\n扩展计算图:")
cf.expand_all(inplace=True, verbose=True)
cf.info()

# 获取计算历史数据框
df = cf.df()
print("\n计算历史数据框:")
print(df)

# 查询上游计算
upstream_cf = cf.upstream("result2")
print("\n生成result2的上游计算:")
upstream_cf.info()

# 查询下游计算
downstream_cf = cf.downstream("processed2")
print("\n使用processed2的下游计算:")
downstream_cf.info()

# 选择特定节点的子图
subgraph = cf.select_nodes(["data1", "processed1", "result1"])
print("\n路径1的子图:")
subgraph.info()

# 可视化完整计算图
cf.draw(path="computation_graph.png", orientation="LR")
print("\n计算图已保存为computation_graph.png")
```

这个例子展示了ComputationFrame的主要功能：
- 创建ComputationFrame
- 扩展计算图
- 查询上下游计算
- 提取数据框
- 选择子图
- 可视化计算图

通过ComputationFrame，您可以全面了解计算历史和依赖关系，这对于调试、分析和优化计算流程非常有价值。 
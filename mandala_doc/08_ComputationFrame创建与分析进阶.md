# ComputationFrame创建与分析进阶

ComputationFrame是Mandala框架中用于查询、分析和可视化计算过程的核心数据结构。本文档将详细介绍ComputationFrame的创建方法、扩展技术和高级分析功能，帮助用户深入理解和利用这一强大工具。

## 1. ComputationFrame的创建方法

ComputationFrame可以通过多种方式创建，每种方式提供不同的初始视角：

### 1.1 从单个结果创建

从单个计算结果创建ComputationFrame，初始只包含该结果对应的变量节点：

```python
from mandala.imports import *

@op
def add(a, b):
    return a + b

with Storage() as s:
    result = add(5, 3)
    
    # 从单个结果创建ComputationFrame
    cf = s.cf(result)
```

此时创建的ComputationFrame是最小的，仅包含一个表示结果的变量节点。

### 1.2 从操作创建

从操作（@op装饰的函数）创建ComputationFrame，包含该操作的所有调用：

```python
with Storage() as s:
    add(1, 2)
    add(3, 4)
    add(5, 6)
    
    # 从操作创建ComputationFrame，包含所有add的调用
    cf = s.cf(add)
```

这种方式创建的ComputationFrame包含指定操作的全部调用历史，可以用来分析该操作的各种用法和结果。

### 1.3 从多个对象创建

从多个结果或操作创建ComputationFrame：

```python
@op
def multiply(a, b):
    return a * b

with Storage() as s:
    result1 = add(1, 2)
    result2 = multiply(3, 4)
    
    # 从多个结果创建
    cf_results = s.cf([result1, result2])
    
    # 从多个操作创建
    cf_ops = s.cf([add, multiply])
    
    # 混合创建
    cf_mixed = s.cf([add, result2])
```

这种方式可以初始化一个包含多个相关操作或结果的计算图。

### 1.4 使用字典指定变量名

使用字典创建ComputationFrame，可以为节点指定自定义名称：

```python
with Storage() as s:
    result1 = add(1, 2)
    result2 = multiply(3, 4)
    
    # 使用自定义变量名
    cf = s.cf({"sum_result": result1, "product_result": result2})
```

这种方式对于创建更易读和理解的计算图特别有用。

### 1.5 从变量引用集合创建

使用变量引用集合创建更复杂的初始计算图：

```python
with Storage() as s:
    results = []
    for i in range(5):
        results.append(add(i, i+1))
        
    # 从引用集合创建
    cf = s.cf({"results": results})
```

这对于分析一系列相关计算非常有用，比如模型训练过程中的多次迭代结果。

## 2. 扩展计算图

创建初始ComputationFrame后，通常需要扩展它以包含更多相关的计算信息：

### 2.1 expand_back：向上游展开

`expand_back`方法向输入方向展开，找出创建指定变量的操作：

```python
# 创建初始计算框架
cf = s.cf(final_result)

# 向上游展开一次
cf.expand_back(inplace=True)

# 递归向上游展开，直到找不到更多来源
cf.expand_back(recursive=True, inplace=True)

# 仅展开特定变量
cf.expand_back(varnames=["specific_var"], inplace=True)
```

`expand_back`对于追踪数据来源和理解计算依赖非常有用。

### 2.2 expand_forward：向下游展开

`expand_forward`方法向输出方向展开，找出使用指定变量的操作：

```python
# 向下游展开一次
cf.expand_forward(inplace=True)

# 递归向下游展开
cf.expand_forward(recursive=True, inplace=True)

# 仅展开特定变量的下游
cf.expand_forward(varnames=["input_var"], inplace=True)
```

`expand_forward`有助于分析计算结果的使用方式和影响。

### 2.3 expand_all：全方向展开

`expand_all`方法同时向上游和下游展开，提供完整的计算上下文：

```python
# 全方向展开计算图
cf.expand_all(inplace=True)

# 控制展开方向
cf.expand_all(direction="backward", inplace=True)  # 仅向上游
cf.expand_all(direction="forward", inplace=True)   # 仅向下游
cf.expand_all(direction="both", inplace=True)      # 双向（默认）

# 限制展开深度
cf.expand_all(max_iterations=3, inplace=True)

# 控制展开策略
cf.expand_all(how="strong", inplace=True)  # 强依赖（默认）
cf.expand_all(how="weak", inplace=True)    # 弱依赖
```

`expand_all`是最常用的展开方法，可以快速获取完整的计算上下文。

### 2.4 选择性展开策略

对于大型计算图，可以采用选择性展开策略：

```python
# 步骤1：先有限展开找出关键节点
cf_limited = cf.expand_all(max_iterations=2, inplace=False)

# 步骤2：确定关键变量
key_vars = identify_key_variables(cf_limited)

# 步骤3：只展开关键变量
cf_focused = cf.expand_all(varnames=key_vars, inplace=False)
```

选择性展开可以避免计算图过大而难以分析的问题。

## 3. 计算图分析与操作

展开后的ComputationFrame提供了丰富的分析和操作功能：

### 3.1 基本信息查询

```python
# 查看计算图基本信息
cf.info()

# 查看特定节点信息
cf.info("node_name")

# 查看节点列表
print("变量节点:", cf.vnames)
print("函数节点:", cf.fnames)
print("所有节点:", cf.nodes)

# 查看边列表
print("所有边:", cf.edges)
```

这些方法提供了计算图结构的基本视图。

### 3.2 节点关系查询

```python
# 获取节点的输入边
in_edges = cf.in_edges("node_name")

# 获取节点的输出边
out_edges = cf.out_edges("node_name")

# 获取节点的输入邻居
in_neighbors = cf.in_neighbors("node_name")

# 获取节点的输出邻居
out_neighbors = cf.out_neighbors("node_name")

# 获取所有邻居
neighbors = cf.neighbors("node_name")
```

这些方法帮助理解节点之间的依赖关系。

### 3.3 路径分析

```python
# 获取两个节点之间的最短路径
shortest_path = cf.get_shortest_path("start_node", "end_node")

# 获取两个节点之间的所有路径
all_paths = cf.get_all_paths_between("start_node", "end_node")

# 获取路径上的所有边
edges_on_path = cf.get_all_edges_on_paths_between("start_node", "end_node")
```

路径分析帮助理解复杂计算中变量之间的传递关系。

### 3.4 集合操作

ComputationFrame支持类似集合的操作：

```python
# 计算两个ComputationFrame的并集
union_cf = cf1.union(cf2)
# 或使用运算符
union_cf = cf1 | cf2

# 计算交集
intersect_cf = cf1.intersect(cf2)
# 或使用运算符
intersect_cf = cf1 & cf2

# 计算差集
diff_cf = cf1.difference(cf2)
# 或使用运算符
diff_cf = cf1 - cf2
```

集合操作有助于比较不同计算过程或找出公共计算部分。

### 3.5 选择性过滤

使用`select`方法进行选择性过滤：

```python
# 选择包含特定节点的边
filtered_cf = cf.select(lambda edge: "important_node" in edge)

# 选择特定函数的调用
func_cf = cf.select(lambda edge: edge[0] == "target_function")

# 根据边属性选择
attr_cf = cf.select(lambda edge: cf.edge_props(edge).get("priority") == "high")
```

选择性过滤可以创建更聚焦的子图，便于分析特定问题。

## 4. 转换为DataFrame进行分析

ComputationFrame可以转换为pandas DataFrame，这是一种更熟悉的表格形式，便于进一步分析：

### 4.1 基本转换

```python
# 转换为DataFrame
df = cf.df()

# 查看特定列
print(df[["func", "input", "output", "time"]])
```

### 4.2 控制返回值类型

```python
# 返回引用对象
df_refs = cf.df(values="refs")

# 返回实际值（默认）
df_objs = cf.df(values="objs")
```

### 4.3 按规则过滤

```python
# 过滤特定函数的调用
func_calls = df[df["func"] == "target_function"]

# 分析执行时间
time_analysis = df.groupby("func")["time"].mean().sort_values(descending=True)

# 查找输入值满足特定条件的调用
filtered_calls = df[df["input"].apply(lambda x: x.get("param") > threshold)]
```

### 4.4 计算历史分析

```python
# 获取特定变量的计算历史
history_df = cf.get_history_df("variable_name")

# 获取多个变量的联合历史
joint_history = cf.get_joint_history_df(["var1", "var2"])
```

## 5. 高级使用模式

### 5.1 增量构建分析

逐步构建和分析计算图是一种有效策略：

```python
# 从关键结果开始
cf = storage.cf(final_result)

# 第一步：向上游展开一级，了解直接依赖
cf.expand_back(inplace=True)
print("直接依赖:")
cf.info()

# 第二步：继续向上游展开，了解更深层依赖
cf.expand_back(recursive=True, inplace=True)
print("完整上游依赖:")
cf.info()

# 第三步：向下游展开，了解结果影响
cf.expand_forward(recursive=True, inplace=True)
print("完整计算图:")
cf.info()

# 第四步：过滤关注的部分
key_paths = cf.get_all_paths_between("input_data", "final_metric")
key_cf = cf.select(lambda edge: edge in key_paths)
print("关键路径:")
key_cf.info()
```

这种增量方法对于理解复杂计算特别有效。

### 5.2 比较分析

比较不同参数或模型的计算过程：

```python
# 创建两个不同实验的计算框架
cf1 = storage.cf(result1)
cf1.expand_all(inplace=True)

cf2 = storage.cf(result2)
cf2.expand_all(inplace=True)

# 找出共同部分
common_cf = cf1 & cf2
print("共同计算步骤:")
common_cf.info()

# 找出差异部分
diff1 = cf1 - cf2
print("实验1特有步骤:")
diff1.info()

diff2 = cf2 - cf1
print("实验2特有步骤:")
diff2.info()

# 创建合并视图
merged_cf = cf1 | cf2
merged_cf.draw(path="comparison.png")
```

比较分析有助于理解不同实验间的异同，对调优和改进算法很有价值。

### 5.3 依赖分析

分析函数间的依赖关系：

```python
def analyze_function_dependencies(cf, target_func):
    # 确保计算图完全展开
    cf = cf.expand_all(inplace=False)
    
    # 获取直接依赖
    direct_deps = set()
    for edge in cf.in_edges(target_func):
        source = edge[0]
        if cf.is_func(source):
            direct_deps.add(source)
    
    # 获取间接依赖
    all_deps = set()
    for func in direct_deps:
        deps = analyze_function_dependencies(cf, func)
        all_deps.update(deps)
    
    all_deps.update(direct_deps)
    return all_deps
```

依赖分析对于理解代码结构和重构代码特别有用。

### 5.4 性能分析

分析计算过程中的性能瓶颈：

```python
def analyze_performance(cf):
    # 转换为DataFrame
    df = cf.df()
    
    # 计算每个函数的平均执行时间
    func_times = df.groupby("func")["time"].mean().sort_values(ascending=False)
    
    # 找出执行次数最多的函数
    call_counts = df["func"].value_counts()
    
    # 计算总时间占比
    total_time = df["time"].sum()
    time_percentage = {func: time / total_time * 100 
                       for func, time in func_times.items()}
    
    return {
        "average_times": func_times,
        "call_counts": call_counts,
        "time_percentage": time_percentage
    }
```

性能分析有助于识别和优化计算瓶颈。

## 6. 实际应用示例

### 6.1 机器学习实验跟踪

使用ComputationFrame跟踪机器学习实验的完整过程：

```python
from mandala.imports import *
import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

storage = Storage()

@op
def load_data(random_seed=42):
    X, y = load_digits(return_X_y=True)
    return X, y

@op
def split_dataset(X, y, test_size=0.2, random_seed=42):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_seed)
    return X_train, X_test, y_train, y_test

@op
def train_model(X_train, y_train, n_estimators, max_depth=None):
    model = RandomForestClassifier(
        n_estimators=n_estimators, 
        max_depth=max_depth,
        random_state=42
    )
    model.fit(X_train, y_train)
    train_acc = model.score(X_train, y_train)
    return model, train_acc

@op
def evaluate_model(model, X_test, y_test):
    test_acc = model.score(X_test, y_test)
    return test_acc

with storage:
    # 加载和准备数据
    X, y = load_data()
    X_train, X_test, y_train, y_test = split_dataset(X, y)
    
    # 训练不同模型
    results = []
    for n_estimators in [10, 50, 100]:
        for max_depth in [None, 5, 10]:
            model, train_acc = train_model(
                X_train, y_train, 
                n_estimators=n_estimators,
                max_depth=max_depth
            )
            test_acc = evaluate_model(model, X_test, y_test)
            results.append((n_estimators, max_depth, train_acc, test_acc))
            
    # 找出最佳模型
    best_idx = np.argmax([res[3] for res in results])
    best_params = results[best_idx]
    print(f"最佳模型: n_estimators={best_params[0]}, max_depth={best_params[1]}")
    print(f"训练准确率: {best_params[2]:.4f}, 测试准确率: {best_params[3]:.4f}")

# 分析实验
cf = storage.cf(evaluate_model)
cf.expand_all(inplace=True)

# 转换为DataFrame进行分析
df = cf.df()
model_params = df[[
    "n_estimators", "max_depth", "train_acc", "evaluate_model"
]].rename(columns={"evaluate_model": "test_acc"})

# 分析参数与性能的关系
print(model_params.sort_values("test_acc", ascending=False))

# 可视化完整实验流程
cf.draw(path="ml_experiment.png", orientation="LR")
```

### 6.2 数据处理管道分析

分析数据处理管道中的数据流和转换：

```python
@op
def load_data(source):
    # 模拟数据加载
    data = {"source": source, "rows": 1000, "columns": 10}
    return data

@op
def clean_data(data):
    # 模拟数据清洗
    clean_data = {**data, "cleaned": True, "rows": data["rows"] * 0.95}
    return clean_data

@op
def transform_features(data):
    # 模拟特征转换
    transformed = {**data, "transformed": True, "columns": data["columns"] + 5}
    return transformed

@op
def filter_data(data, threshold=0.5):
    # 模拟数据过滤
    filtered = {**data, "filtered": True, "rows": data["rows"] * threshold}
    return filtered

@op
def aggregate_data(data, groupby="category"):
    # 模拟数据聚合
    aggregated = {**data, "aggregated": True, "rows": data["rows"] * 0.1}
    return aggregated

with storage:
    # 执行两个不同的数据处理流程
    # 流程1: 加载 -> 清洗 -> 转换 -> 聚合
    data1 = load_data("database1")
    clean1 = clean_data(data1)
    transform1 = transform_features(clean1)
    result1 = aggregate_data(transform1)
    
    # 流程2: 加载 -> 清洗 -> 过滤 -> 聚合
    data2 = load_data("database2")
    clean2 = clean_data(data2)
    filter2 = filter_data(clean2, threshold=0.7)
    result2 = aggregate_data(filter2)

# 创建并分析两个流程
cf1 = storage.cf(result1)
cf1.expand_all(inplace=True)

cf2 = storage.cf(result2)
cf2.expand_all(inplace=True)

# 找出共同步骤
common_steps = cf1 & cf2
print("共同数据处理步骤:")
common_steps.info()

# 找出不同步骤
diff_steps = (cf1 | cf2) - common_steps
print("不同数据处理步骤:")
diff_steps.info()

# 数据流分析
def analyze_data_changes(cf):
    df = cf.df()
    data_flow = []
    
    # 按处理顺序排列节点
    ordered_nodes = cf.topsort_modulo_sccs()
    
    # 分析每个节点的数据变化
    for node in ordered_nodes:
        if cf.is_var(node) and "rows" in df[node].iloc[0]:
            data_flow.append({
                "stage": node,
                "rows": df[node].iloc[0]["rows"],
                "columns": df[node].iloc[0]["columns"] if "columns" in df[node].iloc[0] else None
            })
    
    return data_flow

# 分析两个流程的数据变化
flow1 = analyze_data_changes(cf1)
flow2 = analyze_data_changes(cf2)

print("\n流程1数据变化:")
for stage in flow1:
    print(f"{stage['stage']}: {stage['rows']} 行, {stage['columns']} 列")

print("\n流程2数据变化:")
for stage in flow2:
    print(f"{stage['stage']}: {stage['rows']} 行, {stage['columns']} 列")
```

## 7. 总结

ComputationFrame是Mandala框架中一个极其强大的数据结构，提供了丰富的创建、扩展和分析功能：

1. **灵活创建**：支持从单个结果、操作、多个对象或自定义变量名创建
2. **多向扩展**：可以向上游、下游或双向递归展开计算图
3. **丰富查询**：支持节点关系查询、路径分析和图的集合操作
4. **DataFrame转换**：可以转换为熟悉的表格形式进行进一步分析
5. **高级应用**：支持增量构建、比较分析、依赖分析和性能分析

通过ComputationFrame，用户可以深入理解计算过程中的数据流和依赖关系，这对于调试、优化和分析复杂计算流程至关重要。结合本文档中的示例，您可以开始利用ComputationFrame构建可追踪、可比较和可优化的数据处理和分析流程。 
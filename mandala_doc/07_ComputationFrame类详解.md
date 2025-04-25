# ComputationFrame类详解

ComputationFrame（计算框架）是Mandala中用于操作、分析和可视化计算图的核心类。本文档将详细介绍ComputationFrame的属性、方法和使用场景，帮助您充分发挥其功能。

## 1. ComputationFrame简介

ComputationFrame是Mandala中表示计算图的主要数据结构，它包含了计算过程中的节点（变量和函数）和边（依赖关系），提供了丰富的分析和操作方法。

### 1.1 创建ComputationFrame

在Mandala中，有几种方式可以创建ComputationFrame：

```python
from mandala.imports import *

# 通过存储上下文创建
with Storage() as s:
    a = 5
    b = 10
    
    @op
    def add(x, y):
        return x + y
    
    result = add(a, b)
    
    # 从单个结果创建
    cf = s.cf(result)
    
    # 从多个结果创建
    cf_multi = s.cf([a, b, result])
    
    # 从函数创建
    cf_func = s.cf(add)
```

### 1.2 基本结构

ComputationFrame由以下核心组件构成：

- **节点（Nodes）**：包括变量节点和函数节点
- **边（Edges）**：表示节点之间的依赖关系
- **属性集（Properties）**：存储节点和边的附加信息

## 2. 基本属性和方法

### 2.1 查询节点和边

```python
# 获取所有节点
nodes = cf.nodes

# 获取所有变量节点名称
variables = cf.vnames

# 获取所有函数节点名称
functions = cf.fnames

# 获取所有边（依赖关系）
edges = cf.edges

# 获取源节点（没有输入的节点）
sources = cf.sources

# 获取汇节点（没有输出的节点）
sinks = cf.sinks

# 获取中间节点
intermediate_nodes = cf.intermediate_nodes
```

### 2.2 检查节点类型

```python
# 检查一个节点是否为变量节点
is_var = cf.is_var("node_name")

# 检查一个节点是否为函数节点
is_func = cf.is_func("node_name")

# 获取节点类型
node_type = cf.node_type("node_name")  # 返回 "var" 或 "func"
```

### 2.3 查询节点关系

```python
# 获取节点的输入边
input_edges = cf.input_edges("node_name")

# 获取节点的输出边
output_edges = cf.output_edges("node_name")

# 获取节点的所有相邻节点
neighbors = cf.neighbors("node_name")

# 获取边属性
edge_props = cf.edge_props(("source_node", "edge_label", "target_node"))
```

## 3. 高级操作

### 3.1 计算图修改

```python
# 展开计算图（将在下一节详细介绍）
expanded_cf = cf.expand_all(inplace=False)

# 过滤计算图，保留选定的边
filtered_cf = cf.select(lambda edge: "important_node" in edge)

# 移除特定节点
cf_without_node = cf.without_nodes(["node_to_remove"])

# 移除特定边
cf_without_edge = cf.without_edges([("source", "label", "target")])
```

### 3.2 路径查询

```python
# 获取两个节点之间的最短路径
shortest_path = cf.get_shortest_path("start_node", "end_node")

# 获取最短路径上的所有边
edges_on_path = cf.get_all_edges_on_shortest_path("start_node", "end_node")

# 获取两个节点之间的所有路径
all_paths = cf.get_all_paths_between("start_node", "end_node")

# 获取所有路径上的边
all_edges_on_paths = cf.get_all_edges_on_paths_between("start_node", "end_node")
```

### 3.3 集合操作

```python
# 两个计算框架的并集
merged_cf = cf1.union(cf2)

# 两个计算框架的交集
common_cf = cf1.intersect(cf2)

# 计算框架的差集
difference_cf = cf1.difference(cf2)
```

## 4. 展开计算图：expand_all方法详解

`expand_all`是ComputationFrame中最强大的方法之一，它可以递归地展开计算图，显示完整的依赖关系。

### 4.1 基本用法

```python
# 展开并返回新的计算框架
expanded_cf = cf.expand_all(inplace=False)

# 原地展开当前计算框架
cf.expand_all(inplace=True)
```

### 4.2 参数详解

`expand_all`方法有以下重要参数：

1. **how** (`str`): 展开方式，可选值为 "full"（默认）或 "sampled"
2. **direction** (`str`): 展开方向，可选值为 "both"（默认）、"forward" 或 "backward"
3. **inplace** (`bool`): 是否原地修改，默认为 `False`
4. **keep_expanding** (`bool`): 是否持续展开直到没有新节点，默认为 `True`
5. **max_iterations** (`int`): 最大展开迭代次数，默认为 `None`（无限制）

### 4.3 展开方向

```python
# 向前展开（顺着计算流程）
forward_cf = cf.expand_all(direction="forward", inplace=False)

# 向后展开（逆着计算流程）
backward_cf = cf.expand_all(direction="backward", inplace=False)

# 双向展开
both_cf = cf.expand_all(direction="both", inplace=False)
```

### 4.4 控制展开深度

```python
# 限制展开迭代次数
limited_cf = cf.expand_all(max_iterations=3, inplace=False)

# 单次展开（不持续展开）
single_expand_cf = cf.expand_all(keep_expanding=False, inplace=False)
```

### 4.5 展开方式

```python
# 完整展开
full_cf = cf.expand_all(how="full", inplace=False)

# 采样展开（适用于大型计算图）
sampled_cf = cf.expand_all(how="sampled", inplace=False)
```

## 5. 可视化：draw方法详解

`draw`方法用于可视化计算图，帮助理解计算流程和依赖关系。

### 5.1 基本用法

```python
# 默认可视化（显示计算图）
cf.draw()

# 保存到文件
cf.draw(path="my_computation.png")
```

### 5.2 参数详解

`draw`方法有以下重要参数：

1. **path** (`str`): 输出文件路径，默认为`None`（直接显示）
2. **orientation** (`str`): 图方向，可选 "TB"（从上到下，默认）或 "LR"（从左到右）
3. **verbose** (`bool`): 是否显示详细信息，默认为`False`
4. **rankdir** (`str`): 与`orientation`相同，已弃用但保持兼容
5. **layout** (`str`): 图布局算法，例如 "dot"、"neato"、"fdp" 等
6. **format** (`str`): 输出格式，默认为`None`（根据path推断）
7. **show_edge_labels** (`bool`): 是否显示边标签，默认为`True`
8. **node_attrs** (`dict`): 节点属性自定义
9. **edge_attrs** (`dict`): 边属性自定义
10. **graph_attrs** (`dict`): 图属性自定义

### 5.3 调整图方向

```python
# 从上到下方向（默认）
cf.draw(orientation="TB")

# 从左到右方向
cf.draw(orientation="LR")
```

### 5.4 自定义样式

```python
# 自定义节点样式
cf.draw(node_attrs={
    "var": {"shape": "ellipse", "style": "filled", "color": "lightblue"},
    "func": {"shape": "box", "style": "filled", "color": "lightgreen"}
})

# 自定义边样式
cf.draw(edge_attrs={"fontsize": "10", "color": "gray"})

# 自定义图样式
cf.draw(graph_attrs={"bgcolor": "white", "rankdir": "LR"})
```

### 5.5 不同输出格式

```python
# 保存为PNG格式
cf.draw(path="graph.png")

# 保存为SVG格式
cf.draw(path="graph.svg")

# 保存为PDF格式
cf.draw(path="graph.pdf")
```

## 6. 数据分析功能

### 6.1 转换为DataFrame

```python
# 创建DataFrame
df = cf.df()

# 查看特定列
print(df[["func", "func_version", "input", "output", "time"]])

# 过滤特定函数的调用
add_calls = df[df["func"] == "add"]
```

### 6.2 节点信息查询

```python
# 获取特定节点的信息
node_info = cf.info("node_name")

# 查看函数节点信息
for func in cf.fnames:
    print(f"Function: {func}")
    cf.info(func)
```

### 6.3 计算统计信息

```python
# 计算节点度数（连接边数量）
node_degrees = {node: len(cf.neighbors(node)) for node in cf.nodes}

# 计算函数调用次数
func_calls = {}
for func in cf.fnames:
    func_calls[func] = sum(1 for edge in cf.edges if edge[0] == func)
```

## 7. 高级分析场景

### 7.1 函数依赖分析

分析函数之间的依赖关系：

```python
def analyze_function_dependencies(cf, target_func):
    # 展开计算图
    cf = cf.expand_all(inplace=False)
    
    # 获取函数的直接依赖
    direct_deps = set()
    for edge in cf.input_edges(target_func):
        source_node = edge[0]
        if cf.is_func(source_node):
            direct_deps.add(source_node)
    
    # 获取函数的间接依赖
    all_deps = set()
    for dep in direct_deps:
        # 递归分析每个直接依赖
        sub_deps = analyze_function_dependencies(cf, dep)
        all_deps.update(sub_deps)
    
    # 合并直接依赖和间接依赖
    all_deps.update(direct_deps)
    return all_deps
```

### 7.2 数据流分析

追踪数据如何在计算图中流动：

```python
def trace_data_flow(cf, start_node, max_depth=None):
    # 展开计算图
    cf = cf.expand_all(direction="forward", inplace=False)
    
    # 跟踪从起始节点开始的数据流
    visited = set()
    data_flow = []
    
    def dfs(node, depth=0):
        if node in visited or (max_depth is not None and depth > max_depth):
            return
        
        visited.add(node)
        data_flow.append((depth, node))
        
        # 获取输出边
        for edge in cf.output_edges(node):
            next_node = edge[2]
            dfs(next_node, depth + 1)
    
    # 从起始节点开始深度优先搜索
    dfs(start_node)
    
    return data_flow
```

### 7.3 性能分析

分析计算图的性能特征：

```python
def analyze_performance(cf):
    # 转换为DataFrame
    df = cf.df()
    
    # 计算每个函数的平均执行时间
    func_times = df.groupby("func")["time"].mean().sort_values(ascending=False)
    
    # 找出执行时间最长的函数
    slowest_funcs = func_times.head(5)
    
    # 计算整个计算图的总执行时间
    total_time = df["time"].sum()
    
    # 计算每个函数占总时间的百分比
    time_percentage = {func: time / total_time * 100 
                       for func, time in func_times.items()}
    
    return {
        "slowest_functions": slowest_funcs,
        "total_time": total_time,
        "time_percentage": time_percentage
    }
```

## 8. 实用技巧

### 8.1 处理大型计算图

对于大型计算图，可以采用以下策略：

```python
def handle_large_computation_frame(cf):
    # 1. 有限展开
    limited_cf = cf.expand_all(max_iterations=3, inplace=False)
    
    # 2. 采样展开
    sampled_cf = cf.expand_all(how="sampled", inplace=False)
    
    # 3. 选择关键路径
    sources = limited_cf.sources
    sinks = limited_cf.sinks
    
    critical_paths = []
    for source in sources:
        for sink in sinks:
            path = limited_cf.get_all_edges_on_shortest_path(source, sink)
            if path:
                critical_paths.extend(path)
    
    # 创建只包含关键路径的计算框架
    critical_cf = limited_cf.select(lambda edge: edge in critical_paths)
    
    return critical_cf
```

### 8.2 计算图比较

比较两个计算图的异同：

```python
def compare_computation_frames(cf1, cf2):
    # 计算共同节点
    common_nodes = set(cf1.nodes).intersection(set(cf2.nodes))
    
    # 计算特有节点
    cf1_unique = set(cf1.nodes) - set(cf2.nodes)
    cf2_unique = set(cf2.nodes) - set(cf1.nodes)
    
    # 计算共同边
    common_edges = set(cf1.edges).intersection(set(cf2.edges))
    
    # 计算特有边
    cf1_unique_edges = set(cf1.edges) - set(cf2.edges)
    cf2_unique_edges = set(cf2.edges) - set(cf1.edges)
    
    # 创建结合了两个图的新图，不同来源的边使用不同颜色
    merged_cf = cf1.union(cf2)
    
    return {
        "common_nodes": common_nodes,
        "cf1_unique_nodes": cf1_unique,
        "cf2_unique_nodes": cf2_unique,
        "common_edges": common_edges,
        "cf1_unique_edges": cf1_unique_edges,
        "cf2_unique_edges": cf2_unique_edges,
        "merged_cf": merged_cf
    }
```

### 8.3 计算图转换

将ComputationFrame转换为其他格式：

```python
def convert_computation_frame(cf, format_type):
    if format_type == "networkx":
        import networkx as nx
        
        # 创建有向图
        G = nx.DiGraph()
        
        # 添加节点
        for node in cf.nodes:
            node_type = "variable" if cf.is_var(node) else "function"
            G.add_node(node, type=node_type)
        
        # 添加边
        for edge in cf.edges:
            source, label, target = edge
            G.add_edge(source, target, label=label)
        
        return G
    
    elif format_type == "json":
        # 创建JSON表示
        cf_json = {
            "nodes": [],
            "edges": []
        }
        
        # 添加节点
        for node in cf.nodes:
            node_type = "variable" if cf.is_var(node) else "function"
            cf_json["nodes"].append({
                "id": node,
                "type": node_type
            })
        
        # 添加边
        for edge in cf.edges:
            source, label, target = edge
            cf_json["edges"].append({
                "source": source,
                "target": target,
                "label": label
            })
        
        return cf_json
    
    else:
        raise ValueError(f"Unsupported format: {format_type}")
```

## 9. 实际应用场景

### 9.1 数据科学工作流监控

监控数据科学工作流中的各个步骤：

```python
from mandala.imports import *
import pandas as pd
import numpy as np

@op
def load_data(file_path):
    return pd.read_csv(file_path)

@op
def preprocess(df):
    df = df.copy()
    df.fillna(0, inplace=True)
    return df

@op
def feature_engineering(df):
    df = df.copy()
    df['new_feature'] = df['feature1'] * df['feature2']
    return df

@op
def split_data(df, test_size=0.2):
    # 简化的数据拆分
    n = len(df)
    split_idx = int(n * (1 - test_size))
    return df.iloc[:split_idx], df.iloc[split_idx:]

@op
def train_model(train_df):
    # 模拟模型训练
    return {"model_type": "linear_regression", "coefficients": [0.1, 0.2, 0.3]}

@op
def evaluate_model(model, test_df):
    # 模拟评估
    return {"accuracy": 0.85, "f1_score": 0.82}

with Storage() as s:
    data = load_data("data.csv")
    preprocessed = preprocess(data)
    featured = feature_engineering(preprocessed)
    train, test = split_data(featured)
    model = train_model(train)
    metrics = evaluate_model(model, test)
    
    # 创建计算框架
    cf = s.cf(metrics)
    
    # 展开所有依赖
    cf.expand_all(inplace=True)
    
    # 可视化工作流
    cf.draw(path="data_science_workflow.png", orientation="LR")
    
    # 分析每个步骤的执行时间
    timing_df = cf.df()[["func", "time"]]
    print(timing_df.groupby("func").mean())
```

### 9.2 实验跟踪与比较

跟踪和比较不同实验：

```python
@op
def create_experiment(learning_rate, batch_size):
    return {"lr": learning_rate, "batch_size": batch_size}

@op
def run_experiment(config, data):
    # 模拟实验运行
    lr = config["lr"]
    batch_size = config["batch_size"]
    
    # 假设性能与参数有关
    accuracy = 0.7 + 0.1 * lr + 0.001 * batch_size
    
    return {
        "config": config,
        "accuracy": accuracy,
        "loss": 1.0 - accuracy
    }

with Storage() as s:
    data = load_data("data.csv")
    
    # 实验1：低学习率
    config1 = create_experiment(0.01, 32)
    result1 = run_experiment(config1, data)
    
    # 实验2：高学习率
    config2 = create_experiment(0.1, 32)
    result2 = run_experiment(config2, data)
    
    # 创建两个计算框架
    cf1 = s.cf(result1)
    cf2 = s.cf(result2)
    
    # 展开
    cf1.expand_all(inplace=True)
    cf2.expand_all(inplace=True)
    
    # 比较两个实验
    print(f"实验1准确率: {result1['accuracy']}")
    print(f"实验2准确率: {result2['accuracy']}")
    
    # 合并两个计算图
    merged_cf = cf1.union(cf2)
    merged_cf.draw(path="experiment_comparison.png")
```

### 9.3 故障排查与调试

使用ComputationFrame进行故障排查：

```python
@op
def process_data(data):
    try:
        # 一些可能出错的处理
        processed = data * 2
        return processed
    except Exception as e:
        return {"error": str(e), "data": data}

@op
def check_result(result):
    if isinstance(result, dict) and "error" in result:
        # 处理错误情况
        print(f"Error occurred: {result['error']}")
        return {"status": "error", "details": result}
    else:
        # 正常处理
        return {"status": "success", "result": result}

# 执行计算
with Storage() as s:
    data = [1, 2, "not_a_number", 4]  # 包含错误数据
    
    # 尝试处理
    processed = process_data(data)
    result = check_result(processed)
    
    # 创建计算框架
    cf = s.cf(result)
    cf.expand_all(inplace=True)
    
    # 分析错误路径
    df = cf.df()
    error_rows = df[df["output"].apply(
        lambda x: isinstance(x, dict) and x.get("status") == "error"
    )]
    
    if not error_rows.empty:
        print("Found errors in computation:")
        for _, row in error_rows.iterrows():
            print(f"Function: {row['func']}")
            print(f"Input: {row['input']}")
            print(f"Output: {row['output']}")
            
        # 可视化错误路径
        error_nodes = set(error_rows["output_name"])
        error_cf = cf.select(lambda edge: edge[0] in error_nodes or edge[2] in error_nodes)
        error_cf.draw(path="error_path.png")
```

## 10. 总结

ComputationFrame是Mandala框架中最强大的组件之一，它提供了丰富的功能来操作、分析和可视化计算图。通过掌握本文档中介绍的方法和技巧，您可以：

1. **深入理解计算依赖**：展开和分析完整的计算依赖链
2. **优化计算流程**：识别性能瓶颈和优化机会
3. **调试复杂计算**：追踪错误和异常的传播路径
4. **可视化数据流**：直观呈现数据如何在计算中转换
5. **比较不同计算**：分析多个计算过程的异同

ComputationFrame不仅是一个分析工具，更是理解和改进计算过程的强大助手。通过充分利用其功能，您可以构建更可靠、高效和可理解的数据处理和分析流程。 
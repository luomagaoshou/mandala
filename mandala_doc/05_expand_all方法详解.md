# expand_all方法详解

`expand_all`是Mandala框架中ComputationFrame类的一个重要方法，用于展开和扩充计算图。本文档详细解释此方法的功能、参数及使用场景。

## 概述

在使用Mandala构建的计算管道中，`expand_all`方法允许我们从一个简单的计算图起点出发，递归地探索和展开整个计算依赖网络。这个方法特别有用于:

1. 追踪数据依赖关系
2. 查看完整的计算历史
3. 分析复杂计算的全部过程
4. 准备进行可视化展示

## 基本用法

```python
from mandala.imports import *

@op
def add(a, b):
    return a + b

@op
def multiply(a, b):
    return a * b

with Storage() as s:
    x = add(1, 2)
    y = multiply(x, 3)
    z = add(y, 4)
    
    # 创建初始计算框架，仅包含z的直接依赖
    cf = s.cf(z)
    print("展开前节点数:", len(cf.nodes))
    
    # 展开所有计算依赖
    cf.expand_all(inplace=True)
    print("展开后节点数:", len(cf.nodes))
    
    # 可视化完整的计算图
    cf.draw()
```

## 参数详解

`expand_all`方法支持多个参数来控制展开过程：

```python
def expand_all(
    self,
    how="strong",
    direction="both",
    inplace=False,
    keep_expanding=True,
    max_iterations=None
):
    # 方法实现...
```

### how参数

控制展开强度，有两个可选值：

- `"strong"`（默认）：同时展开所有强依赖和弱依赖关系
- `"weak"`：仅展开弱依赖关系

强依赖和弱依赖的区别：
- **强依赖**：函数的输入和输出之间的必要依赖关系
- **弱依赖**：可能存在的其他依赖关系，如变量被多个函数使用

### direction参数

控制展开方向，有三个可选值：

- `"both"`（默认）：同时向上游（输入方向）和下游（输出方向）展开
- `"forward"`：仅向下游（输出方向）展开，追踪结果的使用
- `"backward"`：仅向上游（输入方向）展开，追踪数据来源

示例：

```python
# 仅展开上游依赖
cf_upstream = s.cf(z)
cf_upstream.expand_all(direction="backward", inplace=True)

# 仅展开下游依赖
cf_downstream = s.cf(x)
cf_downstream.expand_all(direction="forward", inplace=True)
```

### inplace参数

控制展开操作是否在原地修改当前ComputationFrame：

- `False`（默认）：返回一个新的ComputationFrame对象，原对象不变
- `True`：在当前ComputationFrame对象上进行修改，无返回值

示例：

```python
# 非原地展开，返回新对象
cf = s.cf(z)
expanded_cf = cf.expand_all(inplace=False)
# 此时cf和expanded_cf是两个不同的对象

# 原地展开
cf = s.cf(z)
cf.expand_all(inplace=True)
# 此时cf已被修改
```

### keep_expanding参数

控制是否持续展开直到无法继续：

- `True`（默认）：持续展开直到没有新的节点可以添加
- `False`：仅展开一轮

当处理大型计算图时，设置为`False`可以控制展开范围。

### max_iterations参数

限制最大展开迭代次数：

- `None`（默认）：无限制，直到完全展开
- 整数值：最多展开指定的迭代次数

这对于控制大型计算图的展开规模很有用。

## 高级用法

### 逐步展开分析

有时对于大型计算图，我们可能希望逐步展开以分析每一步添加的新节点：

```python
cf = s.cf(final_result)
print("初始节点:", cf.nodes)

for i in range(1, 5):
    new_cf = cf.expand_all(inplace=False, max_iterations=i)
    print(f"第{i}轮展开后节点数: {len(new_cf.nodes)}")
    
    # 查看每轮新增的节点
    new_nodes = set(new_cf.nodes) - set(cf.nodes)
    print(f"第{i}轮新增节点: {new_nodes}")
    
    cf = new_cf
```

### 选择性展开

结合其他ComputationFrame方法，可以实现更精细的展开控制：

```python
# 创建初始计算框架
cf = s.cf(result)

# 先展开特定节点的上游依赖
upstream_nodes = cf.get_reachable_nodes({"特定节点"}, direction="backward")
cf.add_nodes(upstream_nodes, inplace=True)

# 然后展开所有
cf.expand_all(inplace=True)
```

### 与intersect和union结合使用

`expand_all`可以与ComputationFrame的集合操作结合使用：

```python
# 创建并展开两个不同结果的计算图
cf1 = s.cf(result1)
cf1.expand_all(inplace=True)

cf2 = s.cf(result2)
cf2.expand_all(inplace=True)

# 找出两个计算图的共同部分
common_cf = cf1.intersect(cf2)

# 合并两个计算图
merged_cf = cf1.union(cf2)
```

## 使用场景

### 1. 数据谱系分析

跟踪数据从输入到输出的完整路径：

```python
def analyze_data_lineage(final_result):
    with Storage() as s:
        # 创建初始计算图
        cf = s.cf(final_result)
        
        # 展开所有上游依赖
        cf.expand_all(direction="backward", inplace=True)
        
        # 找出所有源节点（无输入的节点）
        source_nodes = cf.sources
        print("数据源节点:", source_nodes)
        
        # 提取每个源节点到结果的路径
        for source in source_nodes:
            paths = cf.get_all_edges_on_paths_between(source, cf.get_var_name(final_result))
            print(f"从{source}到结果的路径:")
            for path in paths:
                print("  ->".join(path))
```

### 2. 计算复杂度分析

分析计算过程中涉及的操作和变量：

```python
def analyze_computation_complexity(result):
    with Storage() as s:
        cf = s.cf(result)
        cf.expand_all(inplace=True)
        
        # 分析函数节点
        func_stats = {}
        for func in cf.fnames:
            calls = cf.fs.get(func, set())
            func_stats[func] = len(calls)
        
        # 按调用次数排序
        sorted_funcs = sorted(func_stats.items(), key=lambda x: x[1], reverse=True)
        print("函数调用统计:")
        for func, count in sorted_funcs:
            print(f"  {func}: {count}次调用")
        
        # 分析变量节点
        var_stats = {}
        for var in cf.vnames:
            refs = cf.vs.get(var, set())
            var_stats[var] = len(refs)
        
        # 按引用次数排序
        sorted_vars = sorted(var_stats.items(), key=lambda x: x[1], reverse=True)
        print("变量引用统计:")
        for var, count in sorted_vars[:10]:  # 只显示前10个
            print(f"  {var}: {count}次引用")
```

### 3. 计算图可视化

通过完全展开准备丰富的可视化图表：

```python
def visualize_full_computation(result, path="full_computation.png"):
    with Storage() as s:
        # 创建并展开计算图
        cf = s.cf(result)
        cf.expand_all(inplace=True)
        
        # 可视化
        cf.draw(
            path=path,
            orientation="LR",
            verbose=True
        )
        
        print(f"完整计算图已保存至: {path}")
        print(f"节点总数: {len(cf.nodes)}")
        print(f"函数节点数: {len(cf.fnames)}")
        print(f"变量节点数: {len(cf.vnames)}")
```

## 性能考虑

对于大型计算图，`expand_all`可能会导致计算图变得非常大，影响性能。以下是一些优化建议：

1. **限制展开范围**：使用`direction`参数限定展开方向
2. **控制展开深度**：使用`max_iterations`参数限制迭代次数
3. **逐步展开**：先用小的`max_iterations`值，再根据需要增加
4. **选择性展开**：先分析哪些节点更重要，然后只展开这些节点
5. **使用弱依赖**：对于某些分析，使用`how="weak"`可能就足够了

示例：

```python
# 处理大型计算图的策略
def handle_large_computation_graph(result):
    with Storage() as s:
        # 初始化
        cf = s.cf(result)
        
        # 先限制展开两轮查看规模
        cf_sample = cf.expand_all(max_iterations=2, inplace=False)
        print(f"两轮展开后节点数: {len(cf_sample.nodes)}")
        
        if len(cf_sample.nodes) > 1000:
            print("计算图过大，使用限制性展开")
            # 仅展开上游4轮
            cf.expand_all(direction="backward", max_iterations=4, inplace=True)
        else:
            print("计算图大小适中，执行完全展开")
            cf.expand_all(inplace=True)
        
        return cf
```

## 与其他方法的组合

`expand_all`方法通常与其他ComputationFrame方法结合使用，构建完整的分析流程：

### 与df()结合

展开后转换为DataFrame以进行表格分析：

```python
# 展开并提取DataFrame
cf = s.cf(result)
cf.expand_all(inplace=True)
df = cf.df()

# 分析计算历史
print(df[["input", "output", "func", "version"]])

# 保存计算历史
df.to_csv("computation_history.csv")
```

### 与select()结合

展开后选择特定子图：

```python
# 展开所有依赖
cf = s.cf(result)
cf.expand_all(inplace=True)

# 选择特定函数及其相关节点
filtering_cf = cf.select(lambda edge: "filter" in edge[0] or "filter" in edge[2])

# 可视化筛选相关操作的子图
filtering_cf.draw(path="filtering_operations.png")
```

### 与info()结合

展开后查看详细信息：

```python
# 展开计算图
cf = s.cf(result)
cf.expand_all(inplace=True)

# 查看关键节点的详细信息
for node in cf.critical_nodes:
    print(f"\n=== {node} 详情 ===")
    cf.info(node)
```

## 完整示例

以下是一个完整的示例，展示了`expand_all`方法在数据分析流程中的应用：

```python
from mandala.imports import *
import numpy as np
import pandas as pd

# 定义数据处理操作
@op
def load_data(source):
    if source == "sales":
        return pd.DataFrame({
            "product": ["A", "B", "C", "D"],
            "quantity": [100, 200, 150, 300],
            "price": [10, 15, 20, 25]
        })
    elif source == "costs":
        return pd.DataFrame({
            "product": ["A", "B", "C", "D"],
            "material_cost": [5, 8, 12, 15],
            "labor_cost": [2, 3, 4, 5]
        })
    else:
        return pd.DataFrame()

@op
def calculate_revenue(sales_data):
    sales_data = sales_data.copy()
    sales_data["revenue"] = sales_data["quantity"] * sales_data["price"]
    return sales_data

@op
def merge_data(sales_data, cost_data):
    return pd.merge(sales_data, cost_data, on="product")

@op
def calculate_profit(combined_data):
    combined_data = combined_data.copy()
    combined_data["total_cost"] = combined_data["material_cost"] + combined_data["labor_cost"]
    combined_data["unit_cost"] = combined_data["total_cost"] / combined_data["quantity"]
    combined_data["profit"] = combined_data["revenue"] - (combined_data["total_cost"] * combined_data["quantity"])
    return combined_data

@op(output_names=["total_revenue", "total_profit", "profit_margin"])
def summarize_results(profit_data):
    total_revenue = profit_data["revenue"].sum()
    total_profit = profit_data["profit"].sum()
    profit_margin = total_profit / total_revenue
    return total_revenue, total_profit, profit_margin

# 执行计算流程
with Storage() as s:
    # 加载数据
    sales_df = load_data("sales")
    costs_df = load_data("costs")
    
    # 计算收入
    revenue_df = calculate_revenue(sales_df)
    
    # 合并数据集
    combined_df = merge_data(revenue_df, costs_df)
    
    # 计算利润
    profit_df = calculate_profit(combined_df)
    
    # 汇总结果
    total_revenue, total_profit, profit_margin = summarize_results(profit_df)
    
    print(f"总收入: ${total_revenue:,.2f}")
    print(f"总利润: ${total_profit:,.2f}")
    print(f"利润率: {profit_margin:.2%}")
    
    # 创建初始计算图
    cf = s.cf([total_revenue, total_profit, profit_margin])
    
    print("\n--- 分析计算图 ---")
    print(f"初始节点数: {len(cf.nodes)}")
    
    # 展开完整的计算依赖
    cf.expand_all(inplace=True)
    print(f"展开后节点数: {len(cf.nodes)}")
    
    # 查找所有源节点
    print("\n数据源节点:")
    for source in cf.sources:
        print(f"  - {source}")
    
    # 提取计算历史到DataFrame
    history_df = cf.df()
    print("\n计算历史:")
    print(history_df[["func", "input", "output"]].head())
    
    # 可视化完整计算图
    cf.draw(path="business_analysis.png", orientation="LR")
    print("\n计算图已保存至 business_analysis.png")
    
    # 仅选择与利润相关的节点
    profit_cf = cf.select(lambda edge: 
        any(n in edge for n in ["profit", "Profit", "calculate_profit"]))
    profit_cf.draw(path="profit_calculation.png")
    print("利润计算子图已保存至 profit_calculation.png")
```

这个示例展示了如何使用`expand_all`方法来分析一个商业数据处理流程，包括跟踪数据来源、查看计算历史以及可视化不同子图。

## 总结

`expand_all`方法是Mandala框架中用于构建和分析完整计算图的强大工具：

1. **功能**：递归展开计算图中的所有相关节点和依赖关系
2. **参数**：提供了灵活控制展开过程的多种参数
3. **应用场景**：数据谱系追踪、计算复杂度分析、可视化准备等
4. **性能考虑**：对于大型计算，可以使用参数限制展开范围
5. **组合使用**：通常与其他方法结合使用，构建完整的分析流程

有效利用`expand_all`方法可以帮助我们更深入地理解复杂计算过程中的数据流和依赖关系，使Mandala成为强大的计算追踪和分析工具。 
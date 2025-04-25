# Mandala基本用法指南

Mandala是一个用于Python的计算跟踪框架，能够自动记录和可视化计算过程中的依赖关系。本指南将介绍Mandala的基本用法，帮助您快速入门和掌握其核心功能。

## 1. 安装

使用pip安装Mandala：

```bash
pip install mandala
```

或者从源代码安装最新版本：

```bash
git clone https://github.com/mandala-ai/mandala.git
cd mandala
pip install -e .
```

## 2. 基本概念

Mandala的核心概念包括：

- **操作（Operation）**：通过`@op`装饰器定义的函数，Mandala会自动跟踪其输入和输出
- **存储（Storage）**：用于存储计算图和中间结果的上下文管理器
- **计算框架（ComputationFrame）**：用于查询、分析和可视化计算图的对象

## 3. 定义操作

使用`@op`装饰器定义操作：

```python
from mandala.imports import *

@op
def add(a, b):
    return a + b

@op
def multiply(a, b):
    return a * b
```

### 3.1 多输出操作

使用`output_names`参数定义多输出操作：

```python
@op(output_names=["sum", "product"])
def calculate(a, b):
    return a + b, a * b
```

### 3.2 缓存控制

控制操作的缓存行为：

```python
# 禁用缓存
@op(cache=False)
def no_cache_func(x):
    return x + random.random()

# 自定义缓存键
@op(cache_key=lambda x: f"custom_{x}")
def custom_cache_func(x):
    return x * 2
```

## 4. 使用存储上下文

使用`Storage`上下文管理器执行和跟踪计算：

```python
with Storage() as s:
    # 执行计算
    result = add(5, 3)
    
    # 查看结果
    print(result)  # 输出: 8
```

### 4.1 嵌套存储

Mandala支持嵌套存储上下文：

```python
with Storage() as outer:
    x = add(1, 2)
    
    with Storage() as inner:
        y = multiply(x, 3)
    
    z = add(x, y)
```

### 4.2 存储配置

配置存储行为：

```python
# 禁用自动缓存
with Storage(auto_cache=False) as s:
    result = compute_function(data)

# 设置缓存目录
with Storage(cache_dir="./my_cache") as s:
    result = compute_function(data)
```

## 5. 创建计算框架

计算框架（ComputationFrame）是分析和可视化计算图的主要工具：

```python
with Storage() as s:
    x = add(1, 2)
    y = multiply(x, 3)
    z = add(y, 4)
    
    # 创建计算框架
    cf = s.cf(z)  # 从结果z创建
    
    # 或者从多个结果创建
    cf_multi = s.cf([x, y, z])
```

### 5.1 基本查询

查询计算图的基本信息：

```python
# 查看节点列表
print(cf.nodes)

# 查看变量节点
print(cf.vnames)

# 查看函数节点
print(cf.fnames)

# 查看边（依赖关系）
print(cf.edges)
```

## 6. 可视化计算图

使用`draw`方法可视化计算图：

```python
# 基本可视化
cf.draw()

# 保存到文件
cf.draw(path="computation.png")

# 更改方向（LR: 从左到右, TB: 从上到下）
cf.draw(orientation="LR")

# 显示详细信息
cf.draw(verbose=True)
```

## 7. 计算图操作

### 7.1 展开计算图

使用`expand_all`方法展开计算图的依赖关系：

```python
# 在当前对象上展开（原地修改）
cf.expand_all(inplace=True)

# 返回新的展开对象
cf_expanded = cf.expand_all(inplace=False)

# 仅向上游展开
cf.expand_all(direction="backward", inplace=True)

# 仅向下游展开
cf.expand_all(direction="forward", inplace=True)
```

### 7.2 选择子图

使用`select`方法选择计算图的子集：

```python
# 选择包含特定节点的边
sub_cf = cf.select(lambda edge: "add" in edge[0])

# 选择特定路径
paths = cf.get_all_edges_on_paths_between("input_node", "output_node")
path_cf = cf.select(lambda edge: edge in paths)
```

### 7.3 集合操作

Mandala支持计算框架的集合操作：

```python
# 并集
merged_cf = cf1.union(cf2)

# 交集
common_cf = cf1.intersect(cf2)

# 差集
diff_cf = cf1.difference(cf2)
```

## 8. 数据分析

### 8.1 转换为DataFrame

将计算图转换为Pandas DataFrame以进行分析：

```python
# 创建DataFrame
df = cf.df()

# 查看计算历史
print(df[["func", "input", "output", "time"]])

# 导出到CSV
df.to_csv("computation_history.csv")
```

### 8.2 节点信息查询

查询节点的详细信息：

```python
# 查看特定节点信息
cf.info("node_name")

# 查看函数调用详情
for func in cf.fnames:
    cf.info(func)
```

## 9. 高级用法

### 9.1 自定义输入输出名称

为多输入多输出操作指定名称：

```python
@op(
    input_names=["first_number", "second_number"],
    output_names=["result"]
)
def custom_add(a, b):
    return a + b
```

### 9.2 版本控制

Mandala支持操作的版本控制：

```python
@op(version="1.0")
def process_data_v1(data):
    # 版本1的实现
    return data * 2

@op(version="2.0")
def process_data_v2(data):
    # 版本2的实现
    return data * 2 + 1
```

### 9.3 元数据和标签

添加元数据和标签：

```python
@op(tags=["math", "basic"], metadata={"complexity": "O(1)"})
def tagged_op(x):
    return x * 2

# 查询特定标签的操作
with Storage() as s:
    result = tagged_op(5)
    cf = s.cf(result)
    
    # 查找带有特定标签的操作
    math_ops = cf.select(lambda edge: "math" in cf.get_tags(edge[0]))
```

### 9.4 错误处理

处理计算过程中的错误：

```python
@op
def risky_operation(x):
    if x < 0:
        raise ValueError("Input must be non-negative")
    return x ** 0.5

with Storage() as s:
    try:
        result = risky_operation(-1)
    except ValueError as e:
        print(f"捕获到错误: {e}")
        # 处理错误...
```

## 10. 使用场景示例

### 10.1 数据处理管道

使用Mandala构建数据处理管道：

```python
from mandala.imports import *
import pandas as pd

@op
def load_data(file_path):
    return pd.read_csv(file_path)

@op
def clean_data(df):
    # 删除缺失值
    return df.dropna()

@op
def transform_data(df):
    # 特征转换
    df = df.copy()
    df["new_feature"] = df["feature1"] * df["feature2"]
    return df

@op
def split_data(df, test_size=0.2):
    # 简单的训练测试集拆分
    n = len(df)
    split_idx = int(n * (1 - test_size))
    return df.iloc[:split_idx], df.iloc[split_idx:]

@op
def train_model(train_df, target_col="target"):
    # 模拟模型训练
    X = train_df.drop(target_col, axis=1)
    y = train_df[target_col]
    # 这里是模型训练代码
    model = {"coefficients": [0.1, 0.2, 0.3], "intercept": 0.5}
    return model

@op
def evaluate_model(model, test_df, target_col="target"):
    # 模拟模型评估
    X = test_df.drop(target_col, axis=1)
    y = test_df[target_col]
    # 这里是评估代码
    score = 0.85  # 模拟的评分
    return score

# 执行整个管道
with Storage() as s:
    raw_data = load_data("data.csv")
    clean_data_df = clean_data(raw_data)
    transformed_data = transform_data(clean_data_df)
    train_df, test_df = split_data(transformed_data)
    model = train_model(train_df)
    score = evaluate_model(model, test_df)
    
    print(f"模型得分: {score}")
    
    # 创建并可视化整个计算图
    cf = s.cf(score)
    cf.expand_all(inplace=True)
    cf.draw(path="ml_pipeline.png", orientation="LR")
```

### 10.2 实验跟踪

使用Mandala跟踪实验：

```python
@op
def generate_experiment_config(learning_rate, batch_size, epochs):
    return {
        "learning_rate": learning_rate,
        "batch_size": batch_size,
        "epochs": epochs
    }

@op
def run_experiment(config):
    # 模拟实验运行
    lr = config["learning_rate"]
    bs = config["batch_size"]
    epochs = config["epochs"]
    
    # 假设结果与参数有关
    accuracy = 0.5 + 0.1 * lr + 0.01 * bs + 0.001 * epochs
    loss = 1.0 - accuracy
    
    return {
        "accuracy": accuracy,
        "loss": loss,
        "config": config
    }

# 运行多个实验
with Storage(cache_dir="./experiments") as s:
    # 实验1
    config1 = generate_experiment_config(0.001, 32, 10)
    result1 = run_experiment(config1)
    
    # 实验2
    config2 = generate_experiment_config(0.01, 64, 20)
    result2 = run_experiment(config2)
    
    # 比较结果
    print(f"实验1准确率: {result1['accuracy']}")
    print(f"实验2准确率: {result2['accuracy']}")
    
    # 创建实验比较图
    cf1 = s.cf(result1)
    cf2 = s.cf(result2)
    
    # 将两个实验合并到一个计算图中
    merged_cf = cf1.union(cf2)
    merged_cf.expand_all(inplace=True)
    
    # 可视化
    merged_cf.draw(path="experiment_comparison.png")
```

## 11. 性能优化建议

使用Mandala时的性能优化技巧：

1. **适当使用缓存**：对于计算密集型操作，启用缓存可以提高性能
2. **控制计算图大小**：使用`select`、`direction`参数限制计算图范围
3. **批量处理**：对于大数据集，考虑在操作内实现批量处理
4. **使用`max_iterations`**：大型计算图展开时使用`max_iterations`限制展开深度
5. **选择性禁用跟踪**：对于性能敏感的操作，可以选择不使用`@op`装饰器

## 12. 常见问题排查

### 12.1 缓存问题

```python
# 清除缓存
from mandala.core.storage import clear_cache
clear_cache()

# 或在存储上下文中
with Storage(clear_cache=True) as s:
    # 你的代码...
```

### 12.2 内存占用过高

```python
# 限制存储在内存中的结果大小
with Storage(max_mem_size=1e9) as s:  # 限制为1GB
    # 你的代码...
```

### 12.3 计算图太大

```python
# 使用采样策略处理大型计算图
def handle_large_graph(result):
    with Storage() as s:
        cf = s.cf(result)
        
        # 先查看直接依赖
        print(f"直接依赖节点数: {len(cf.nodes)}")
        
        # 有限展开
        limited_cf = cf.expand_all(max_iterations=2, inplace=False)
        print(f"有限展开后节点数: {len(limited_cf.nodes)}")
        
        # 如果节点太多，只选择关键路径
        if len(limited_cf.nodes) > 100:
            # 找出关键节点
            critical_nodes = set()
            for source in limited_cf.sources:
                for sink in limited_cf.sinks:
                    path = limited_cf.get_all_edges_on_shortest_path(source, sink)
                    for edge in path:
                        critical_nodes.update([edge[0], edge[2]])
            
            # 只保留关键节点相关的边
            critical_cf = limited_cf.select(lambda edge: 
                               edge[0] in critical_nodes and edge[2] in critical_nodes)
            
            return critical_cf
        else:
            return limited_cf
```

### 12.4 版本冲突

```python
# 显式指定使用哪个版本的函数
@op(version="latest")
def my_function(x):
    # 最新版本实现
    return x * 3

# 在使用时
with Storage(op_versions={"my_function": "1.0"}) as s:
    # 这里会使用版本1.0的my_function
    result = my_function(5)
```

## 13. 最佳实践

1. **有意义的命名**：为操作和变量使用清晰、有意义的名称
2. **合理的粒度**：操作既不要太大（难以跟踪内部逻辑）也不要太小（图变得过于复杂）
3. **文档和标签**：使用标签和元数据为操作添加说明
4. **独立性**：尽量设计无副作用的操作，便于并行执行和缓存
5. **分层设计**：大型计算可以分解为多个子计算框架
6. **定期清理**：使用完毕后清理不需要的缓存和大型对象
7. **错误处理**：合理处理和记录操作中的错误

## 14. 总结

Mandala框架提供了强大而灵活的计算追踪能力，适用于各种数据科学和机器学习场景：

1. **透明追踪**：自动记录计算依赖，无需手动维护
2. **可视化能力**：直观呈现计算图结构
3. **交互分析**：提供丰富的API分析计算过程
4. **版本控制**：支持函数版本控制，便于实验比较
5. **缓存机制**：优化重复计算性能

通过掌握本指南中的基本用法，您可以开始利用Mandala构建可追踪、可复现的数据处理和分析流程。随着对框架的深入理解，您将能够应对更复杂的计算追踪和分析需求。 
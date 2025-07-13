# ComputationFrame 层级遍历功能详解

## 概述

新实现的 `traverse_cf_hierarchical` 方法为 ComputationFrame 提供了按照调用顺序与层级遍历的功能，能够深入分析计算图的依赖关系和执行顺序。

## 核心功能

### 1. 层级分析
- **依赖层级识别**：自动分析函数间的依赖关系，将函数分配到不同层级
- **调用顺序追踪**：记录函数的实际调用顺序和时间序列
- **输入输出映射**：详细分析每个函数的输入参数和输出结果

### 2. 详细信息提取
- **函数调用统计**：每个函数的调用次数和参数信息
- **数据流追踪**：输入输出数据的流向和引用关系
- **调用历史记录**：完整的函数调用历史和参数值

## 方法签名

```python
def traverse_cf_hierarchical(self, cf, show_details=True):
    """按照调用顺序与层级遍历 ComputationFrame
    
    参数:
        cf: ComputationFrame 对象
        show_details: 是否显示详细信息
    
    返回:
        层级结构信息字典
    """
```

## 返回结果结构

```python
hierarchy = {
    "levels": [
        {
            "level": 0,
            "functions": ["func1", "func2"]
        }
    ],
    "dependencies": {
        "func_name": {
            "inputs": ["input_var1", "input_var2"],
            "outputs": ["output_var1"],
            "calls": [
                {
                    "call_id": 0,
                    "inputs": {"param1": "value1"},
                    "outputs": {"result": "value2"},
                    "timestamp": None
                }
            ]
        }
    },
    "call_order": [
        {
            "function": "func_name",
            "call_id": 0,
            "timestamp": None,
            "inputs": {"param": "value"},
            "outputs": {"result": "value"}
        }
    ]
}
```

## 输出格式示例

```
=== 按层级和调用顺序遍历 ComputationFrame ===
📊 计算图层级结构:
   总层级数: 3
   总调用次数: 12

🔹 层级 0 (2 个函数):
   📋 step1_process: 3 次调用
      ⬇️  输入: data
      ⬆️  输出: output_0
      📞 调用 1:
         输入: data=[1, 2, 3]
         输出: output_0=[10, 20, 30]
      📞 调用 2:
         输入: data=[4, 5, 6, 7]
         输出: output_0=[40, 50, 60, 70]
      📞 调用 3:
         输入: data=[8, 9]
         输出: output_0=[80, 90]

🔹 层级 1 (1 个函数):
   📋 step2_transform: 3 次调用
      ⬇️  输入: processed_data
      ⬆️  输出: output_0
      📞 调用 1:
         输入: processed_data=[10, 20, 30]
         输出: output_0=[15, 25, 35]

🕐 调用时间顺序:
    1. step1_process (调用ID: 0)
       输入: data=[1, 2, 3]
    2. step1_process (调用ID: 1)
       输入: data=[4, 5, 6, 7]
    3. step2_transform (调用ID: 0)
       输入: processed_data=[10, 20, 30]
```

## 核心算法

### 1. 依赖关系分析

```python
def _compute_dependency_levels(self, func_dependencies):
    """计算函数的依赖层级"""
    levels = []
    remaining_funcs = set(func_dependencies.keys())
    current_level = 0
    
    while remaining_funcs:
        current_level_funcs = []
        
        for fname in list(remaining_funcs):
            # 检查是否所有依赖都已在前面的层级中
            dependencies_satisfied = True
            for input_var in func_dependencies[fname]["inputs"]:
                # 检查是否有其他函数产生这个输入变量
                for other_fname in func_dependencies:
                    if (other_fname != fname and 
                        input_var in func_dependencies[other_fname]["outputs"] and
                        other_fname in remaining_funcs):
                        dependencies_satisfied = False
                        break
            
            if dependencies_satisfied:
                current_level_funcs.append(fname)
        
        levels.append({
            "level": current_level,
            "functions": current_level_funcs
        })
        
        for fname in current_level_funcs:
            remaining_funcs.remove(fname)
        
        current_level += 1
    
    return levels
```

### 2. 调用顺序计算

```python
def _compute_call_order(self, func_dependencies):
    """计算函数调用的时间顺序"""
    call_order = []
    
    for fname, info in func_dependencies.items():
        for call in info["calls"]:
            call_order.append({
                "function": fname,
                "call_id": call["call_id"],
                "timestamp": call.get("timestamp"),
                "inputs": call["inputs"],
                "outputs": call["outputs"]
            })
    
    # 按时间戳或函数名排序
    if any(call.get("timestamp") for call in call_order):
        call_order.sort(key=lambda x: x.get("timestamp", 0))
    else:
        call_order.sort(key=lambda x: (x["function"], x["call_id"]))
    
    return call_order
```

## 使用场景

### 1. 计算图调试
- **依赖关系验证**：确认函数间的依赖关系是否正确
- **执行顺序分析**：理解计算的实际执行顺序
- **性能瓶颈识别**：找出执行时间较长的函数调用

### 2. 数据流分析
- **数据传递追踪**：跟踪数据在计算图中的流动路径
- **中间结果检查**：查看每个步骤的中间计算结果
- **错误源定位**：快速定位计算错误的来源

### 3. 计算优化
- **并行化机会识别**：找出可以并行执行的函数
- **缓存策略优化**：分析哪些计算结果值得缓存
- **计算图重构**：基于依赖关系优化计算图结构

## 实际应用示例

### 示例1：简单计算链

```python
# 创建计算链：数据处理 -> 转换 -> 聚合 -> 最终化
manager = ComputationFrameManager()
cf = storage.cf(final_func).expand_all()
hierarchy = manager.traverse_cf_hierarchical(cf, show_details=True)

# 输出结果显示清晰的层级结构：
# 层级 0: step1_process (基础处理)
# 层级 1: step2_transform (数据转换)  
# 层级 2: step3_aggregate (聚合)
# 层级 3: step4_finalize (最终化)
```

### 示例2：复杂依赖关系

```python
# 创建并行分支后合并的计算图
# branch_a 和 branch_b 并行处理 -> merge_branches -> final_process
hierarchy = manager.traverse_cf_hierarchical(complex_cf, show_details=True)

# 输出结果显示：
# 层级 0: branch_a, branch_b (并行处理)
# 层级 1: merge_branches (合并结果)
# 层级 2: final_process (最终处理)
```

## 技术特点

### 1. 智能依赖分析
- 自动识别函数间的输入输出依赖关系
- 处理复杂的多层级依赖结构
- 支持并行计算分支的识别

### 2. 详细信息提取
- 提取每次函数调用的具体参数值
- 记录输入输出数据的引用关系
- 支持时间戳排序（如果可用）

### 3. 友好的输出格式
- 使用 emoji 图标增强可读性
- 层级化的信息组织结构
- 支持详细和简洁两种显示模式

### 4. 错误处理
- 优雅处理无法获取的函数信息
- 防止无限循环的保护机制
- 详细的错误信息反馈

## 局限性

1. **时间戳依赖**：如果 mandala 不提供时间戳，调用顺序可能不完全准确
2. **复杂引用**：对于复杂的 Ref 对象，可能无法完全解析实际值
3. **循环依赖**：虽然有保护机制，但复杂的循环依赖可能导致层级分析不准确

## 扩展建议

1. **时间戳支持**：如果 mandala 提供调用时间戳，可以更准确地排序
2. **可视化增强**：结合 SVG 生成，在图形中标注层级信息
3. **性能分析**：添加执行时间统计和性能分析功能
4. **交互式查询**：支持按层级或函数名过滤显示信息

这个新功能为 ComputationFrame 的分析提供了强大的工具，特别适合复杂计算图的调试和优化工作。 
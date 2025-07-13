# ComputationFrame 简洁演示

这是 `cf_node_manipulation_example.py` 的简化版本，保留所有核心功能但提供更简洁易用的接口。

## 快速开始

```bash
# 基础演示
python mydemo/案例/cf_simple_demo.py

# 高级用法演示
python mydemo/案例/cf_simple_demo.py advanced
```

## 主要简化

### 1. 更简洁的类设计

```python
class CFDemo:
    """只有核心功能，去除冗余代码"""
    def __init__(self):
        self.storage = Storage()
        self.svg_dir = Path("mydemo/svg")
        self._setup_functions()
```

### 2. 清晰的函数命名

| 原函数名 | 新函数名 | 功能 |
|---------|---------|------|
| `traverse_computation_frame()` | `analyze_cf()` | 分析计算框架 |
| `generate_svg_visualization()` | `generate_svg()` | 生成SVG |
| `update_node_and_regenerate()` | `update_strategy_X()` | 更新策略 |
| `comprehensive_analysis()` | `run_demo()` | 运行演示 |

### 3. 简化的输出格式

使用 emoji 和简洁的信息：
```
📊 创建计算历史...
✅ 创建了 3 个计算分支
🔍 分析 原始计算框架:
  函数节点: 2 个
  变量节点: 8 个
🎨 SVG 已保存: demo_original.svg
```

### 4. 精简的功能集

保留核心功能，移除冗余：
- ✅ 计算历史创建
- ✅ ComputationFrame 分析
- ✅ SVG 可视化
- ✅ 三种更新策略
- ✅ 组合计算框架
- ❌ 过度详细的错误处理
- ❌ 复杂的配置选项

## 核心功能对比

| 功能 | 原版本 | 简洁版本 |
|------|--------|----------|
| 代码行数 | 420 行 | 250 行 |
| 类方法数 | 12 个 | 8 个 |
| 输出详细度 | 非常详细 | 简洁清晰 |
| 易用性 | 功能完整 | 更易理解 |

## 使用示例

### 基础用法
```python
from cf_simple_demo import CFDemo

demo = CFDemo()
demo.run_demo()  # 运行完整演示
```

### 单独功能
```python
demo = CFDemo()

# 创建计算历史
summaries = demo.create_history()

# 分析特定函数
cf = demo.storage.cf(demo.compute)
info = demo.analyze_cf(cf, "我的计算函数")

# 生成可视化
demo.generate_svg(cf, "my_graph.svg")

# 测试更新策略
new_cf, results = demo.update_strategy_1_version()
```

## 生成的文件

运行后会在 `mydemo/svg/` 目录生成：
- `demo_original.svg` - 原始计算图
- `demo_版本控制.svg` - 版本控制策略图
- `demo_参数哈希.svg` - 参数哈希策略图
- `demo_逻辑分支.svg` - 逻辑分支策略图
- `demo_combined.svg` - 组合计算图

## 核心概念保留

1. **@op 和 @track 装饰器的使用**
2. **ComputationFrame 的遍历和分析**
3. **三种节点更新策略**
4. **SVG 可视化生成**
5. **计算图的组合操作**

## 适用场景

- **学习 mandala 框架**：更容易理解核心概念
- **快速原型开发**：简洁的 API 便于快速实验
- **演示和教学**：清晰的输出适合展示
- **基础应用开发**：涵盖大部分常用功能

这个简洁版本保留了原版本的所有核心功能，但提供了更友好的用户体验和更清晰的代码结构。 
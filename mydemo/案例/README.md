# ComputationFrame 案例集合

本目录包含了 mandala 框架中 ComputationFrame 操作的完整案例集合。

## 文件概览

### 1. 完整功能版本
- **`cf_node_manipulation_example.py`** (420 行)
  - 完整的 ComputationFrame 管理器
  - 详细的错误处理和日志记录
  - 全面的功能覆盖
  - 适合深入学习和生产环境

### 2. 简洁演示版本
- **`cf_simple_demo.py`** (250 行)
  - 保留所有核心功能
  - 简化的 API 接口
  - 清晰的输出格式
  - 适合快速学习和原型开发

### 3. 对比学习版本
- **`op_vs_track_example.py`** (包含 9 个步骤的详细对比)
  - @op 和 @track 装饰器的深度对比
  - 节点替换策略的实际应用
  - 完整的调试和测试流程

## 功能对比

| 功能特性 | 完整版本 | 简洁版本 | 对比版本 |
|----------|----------|----------|----------|
| 代码行数 | 420 行 | 250 行 | 300+ 行 |
| 学习曲线 | 较陡峭 | 平缓 | 中等 |
| 功能完整性 | 100% | 90% | 70% |
| 易用性 | 中等 | 高 | 高 |
| 适用场景 | 生产环境 | 学习/原型 | 概念理解 |

## 核心功能覆盖

### 所有版本都包含：
- ✅ ComputationFrame 创建和管理
- ✅ 计算历史的遍历和分析
- ✅ SVG 可视化生成
- ✅ 节点更新和替换策略
- ✅ @op 和 @track 装饰器使用

### 新增功能（v2.0）：
- ✅ **层级遍历分析**：按调用顺序与层级遍历 ComputationFrame
- ✅ **依赖关系可视化**：智能识别函数间的依赖层级
- ✅ **调用顺序追踪**：详细记录函数的执行顺序和参数
- ✅ **并行计算识别**：自动识别可并行执行的计算分支

### 完整版本额外包含：
- ✅ 详细的错误处理
- ✅ 复杂的配置选项
- ✅ 全面的日志记录
- ✅ 高级的数据分析功能

### 简洁版本特点：
- ✅ 清晰的 emoji 输出
- ✅ 简化的函数命名
- ✅ 快速的上手体验
- ✅ 模块化的功能设计

## 使用建议

### 初学者路径
1. 从 `cf_simple_demo.py` 开始
2. 理解基本概念后查看 `op_vs_track_example.py`
3. 深入学习时参考 `cf_node_manipulation_example.py`

### 开发者路径
1. 快速原型：使用 `cf_simple_demo.py`
2. 功能对比：参考 `op_vs_track_example.py`
3. 生产部署：基于 `cf_node_manipulation_example.py`

## 运行示例

```bash
# 快速演示
python mydemo/案例/cf_simple_demo.py

# 高级用法
python mydemo/案例/cf_simple_demo.py advanced

# 完整功能演示
python mydemo/案例/cf_node_manipulation_example.py

# 对比学习
python mydemo/案例/op_vs_track_example.py
```

## 生成的可视化文件

运行后会在 `mydemo/svg/` 目录生成多个 SVG 文件：
- `demo_*.svg` - 简洁版本生成的图形
- `*_computation_graph.svg` - 完整版本生成的图形
- `op_track_*.svg` - 对比版本生成的图形

## 技术文档

每个示例都配有详细的技术文档：
- `cf_simple_demo.md` - 简洁版本说明
- `cf_node_manipulation_example.md` - 完整版本说明
- `op_vs_track_example.md` - 对比版本说明
- `hierarchical_traverse_guide.md` - 层级遍历功能详解
- `test_hierarchical_traverse.py` - 层级遍历测试示例

## 核心学习要点

1. **ComputationFrame 的本质**：计算历史的查询构建器
2. **@op vs @track**：缓存机制 vs 依赖追踪
3. **节点替换策略**：版本控制、参数哈希、逻辑分支
4. **可视化分析**：通过 SVG 理解计算图结构
5. **实际应用场景**：机器学习、数据分析、科学计算

这个案例集合提供了从入门到精通的完整学习路径，适合不同层次的开发者使用。 
# 栈回放（函数再执行）设计文档

## 概述
设计一个基于mandala框架的栈回放系统，利用ComputationFrame和Storage的现有功能，实现函数的重新执行和节点替换。

## 架构

### 核心组件
1. **StackReplayDemo**: 主演示类，协调整个回放流程
2. **计算历史创建**: 使用@op装饰器创建两层函数调用
3. **参数修改器**: 修改函数输入参数的工具
4. **节点替换器**: 替换ComputationFrame中节点的工具

### 数据流
```
原始计算 -> 存储到Storage -> 创建ComputationFrame -> 
查找目标函数 -> 修改参数 -> 重新执行 -> 
创建新ComputationFrame -> 合并/替换节点 -> 可视化结果
```

## 组件和接口

### StackReplayDemo类
```python
class StackReplayDemo:
    def __init__(self, storage_path: str = ":memory:")
    def 创建计算历史(self) -> None
    def 查找目标函数(self, 函数名: str) -> List[Call]
    def 修改参数重新执行(self, 原始调用: Call, 新参数: Dict) -> Any
    def 替换节点生成新CF(self, 新结果: Any) -> ComputationFrame
    def 运行完整演示(self) -> None
```

### 两层函数设计
```python
@op
def 数据处理(数据: List[int], 乘数: int = 2) -> List[int]
    # 第一层函数：简单的数据处理

@op  
def 批量计算(输入列表: List[int], 处理参数: int = 2) -> Dict[str, Any]
    # 第二层函数：包含循环的批量计算
    # 内部调用数据处理函数多次
```

## 数据模型

### 函数调用记录
- **Call对象**: 包含函数调用的完整信息
- **输入参数**: 函数的原始输入参数
- **输出结果**: 函数的执行结果
- **依赖关系**: 函数间的调用关系

### ComputationFrame结构
- **变量节点**: 存储函数的输入输出数据
- **函数节点**: 存储函数调用信息
- **边关系**: 表示数据流向

## 错误处理

### 参数修改错误
- 验证新参数的类型和格式
- 处理参数不兼容的情况
- 提供详细的错误信息

### 函数执行错误
- 捕获重新执行时的异常
- 记录执行失败的原因
- 提供回滚机制

### ComputationFrame操作错误
- 处理节点合并冲突
- 验证图结构的完整性
- 确保数据一致性

## 测试策略

### 单元测试
- 测试每个函数的独立功能
- 验证参数修改的正确性
- 检查ComputationFrame操作

### 集成测试
- 测试完整的回放流程
- 验证多层函数调用
- 检查结果的一致性

### 边界测试
- 测试极端参数值
- 验证错误处理机制
- 检查性能表现
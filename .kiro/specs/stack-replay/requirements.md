# 栈回放（函数再执行）需求文档

## 功能概述
实现一个栈回放系统，能够在程序运行完成后，通过函数上下文、层级和入参等信息，确定需要再执行的函数，修改入参或上下文后重新执行该函数，并将新的节点替换旧的节点，生成新的ComputationFrame。

## 需求

### Requirement 1

**User Story:** 作为开发者，我希望能够创建两层函数的计算历史，其中第二层函数包含循环逻辑，以便后续进行栈回放操作。

#### Acceptance Criteria

1. WHEN 执行两层函数调用 THEN 系统 SHALL 记录完整的计算历史
2. WHEN 第二层函数包含循环 THEN 系统 SHALL 正确记录每次循环的调用
3. WHEN 创建ComputationFrame THEN 系统 SHALL 包含所有函数调用和变量节点

### Requirement 2

**User Story:** 作为开发者，我希望能够从存储中查找特定的函数调用，以便确定需要重新执行的目标函数。

#### Acceptance Criteria

1. WHEN 查询函数调用历史 THEN 系统 SHALL 返回所有相关的Call对象
2. WHEN 分析函数层级 THEN 系统 SHALL 提供函数间的依赖关系
3. WHEN 提取函数参数 THEN 系统 SHALL 返回原始输入参数

### Requirement 3

**User Story:** 作为开发者，我希望能够修改函数的输入参数，重新执行该函数，以便测试不同参数下的计算结果。

#### Acceptance Criteria

1. WHEN 修改函数参数 THEN 系统 SHALL 使用新参数重新执行函数
2. WHEN 重新执行函数 THEN 系统 SHALL 生成新的计算节点
3. WHEN 保存新计算 THEN 系统 SHALL 将结果存储到storage中

### Requirement 4

**User Story:** 作为开发者，我希望能够将新的计算节点替换旧的节点，生成新的ComputationFrame，以便比较不同参数下的计算结果。

#### Acceptance Criteria

1. WHEN 创建新的ComputationFrame THEN 系统 SHALL 包含新的计算节点
2. WHEN 合并ComputationFrame THEN 系统 SHALL 正确组合原始和新的计算图
3. WHEN 可视化结果 THEN 系统 SHALL 显示完整的计算图结构
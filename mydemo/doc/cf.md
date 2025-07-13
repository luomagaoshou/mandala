# ComputationFrame 类完整文档

## 概述

`ComputationFrame` 是 mandala 框架中的核心类，提供了对存储切片的高级视图，支持对记忆化计算图的批量操作。它类似于 `pandas.DataFrame` 的计算图版本，其中节点是变量和操作，边定义了变量和操作的（部分）顺序。

## 辅助函数

### `get_name_proj(op: Op) -> Callable[[str], str]`
**用途**: 获取操作的名称投影函数，用于将输入/输出名称映射到边标签
**参数**:
- `op: Op` - 操作对象
**返回**: 名称投影函数
**内部逻辑**: 
- 如果是 `__make_list__` 操作，将 `elts_*` 形式的名称映射为 `elts`
- 其他操作保持原名称不变

### `get_reverse_proj(call: Call) -> Callable[[str], Set[str]]`
**用途**: 获取调用的反向投影函数，用于从边标签反推输入/输出名称
**参数**:
- `call: Call` - 调用对象
**返回**: 反向投影函数
**内部逻辑**:
- 如果是 `__make_list__` 调用，`elts` 标签映射到所有输入名称
- 其他调用直接返回标签名称

## 类定义

```python
class ComputationFrame:
    """
    A high-level view of a slice of storage that enables bulk operations on the
    memoized computation graph.
    """
```

## 初始化方法

### `__init__(self, storage, inp=None, out=None, vs=None, fs=None, refinv=None, callinv=None, creator=None, consumers=None, refs=None, calls=None)`
**用途**: 初始化 ComputationFrame 实例
**参数详解**:

| 参数名 | 类型 | 默认值 | 详细描述 |
|--------|------|--------|----------|
| `storage` | `Storage` | 必需 | 关联的存储实例，用于管理计算历史和数据持久化 |
| `inp` | `Dict[str, Dict[str, Set[str]]]` | `None` | 输入邻接表：节点名 -> 输入标签 -> {连接的源节点名} |
| `out` | `Dict[str, Dict[str, Set[str]]]` | `None` | 输出邻接表：节点名 -> 输出标签 -> {连接的目标节点名} |
| `vs` | `Dict[str, Set[str]]` | `None` | 变量集合：变量名 -> {包含的 ref history_id} |
| `fs` | `Dict[str, Set[str]]` | `None` | 函数集合：函数名 -> {包含的 call history_id} |
| `refinv` | `Dict[str, Set[str]]` | `None` | 引用反向索引：ref history_id -> {包含此引用的变量名} |
| `callinv` | `Dict[str, Set[str]]` | `None` | 调用反向索引：call history_id -> {包含此调用的函数名} |
| `creator` | `Dict[str, str]` | `None` | 创建者映射：ref history_id -> 创建它的 call history_id |
| `consumers` | `Dict[str, Set[str]]` | `None` | 消费者映射：ref history_id -> {消费它的 call history_id} |
| `refs` | `Dict[str, Union[Ref, Any]]` | `None` | 引用对象：history_id -> Ref 对象 |
| `calls` | `Dict[str, Call]` | `None` | 调用对象：history_id -> Call 对象 |

**初始化逻辑**:
- 所有 None 参数都会被初始化为空字典
- 设置存储引用
- 建立双向索引结构以支持高效查询

## 核心验证方法

### `_check()`
**用途**: 检查 ComputationFrame 的所有不变量，确保数据结构的一致性
**参数**: 无
**返回**: 无（通过断言验证）
**检查项目**:
1. **引用一致性**: `vs` 中的所有 history_id 必须在 `refs` 中存在
2. **调用一致性**: `fs` 中的所有 history_id 必须在 `calls` 中存在  
3. **反向索引一致性**: `refinv` 和 `callinv` 的值必须是有效的节点名
4. **创建者映射一致性**: `creator` 的键必须是有效的 ref，值必须是有效的 call
5. **消费者映射一致性**: `consumers` 的键必须是有效的 ref，值必须是有效的 call 集合
6. **边的有效性**: 所有边的源和目标必须是有效的节点
7. **调用输入输出一致性**: 每个调用的输入输出必须正确映射到图中的变量
8. **ID 一致性**: 对象的 hid 必须与字典的键匹配

**实现逻辑**:
- 使用多个 `assert` 语句验证各种不变量
- 调用 `get_nullable_union` 等工具函数进行集合操作
- 遍历所有调用验证输入输出映射
**调用**: 内部调用 `edges()`, `get_name_proj()` 等方法
**使用场景**: 调试、测试、开发时验证数据结构正确性

## 实例变量

### 图模式变量
- **`inp`**: `Dict[str, Dict[str, Set[str]]]` - 输入邻接表，节点名 -> 输入标签 -> {连接的源节点名}
- **`out`**: `Dict[str, Dict[str, Set[str]]]` - 输出邻接表，节点名 -> 输出标签 -> {连接的目标节点名}

### 图实例数据变量
- **`vs`**: `Dict[str, Set[str]]` - 变量名到包含的 ref history_id 集合的映射
- **`fs`**: `Dict[str, Set[str]]` - 函数名到包含的 call history_id 集合的映射
- **`refinv`**: `Dict[str, Set[str]]` - ref history_id 到包含它的变量名集合的反向映射
- **`callinv`**: `Dict[str, Set[str]]` - call history_id 到包含它的函数名集合的反向映射
- **`creator`**: `Dict[str, str]` - ref history_id 到创建它的 call history_id 的映射（每个 ref 最多一个创建者）
- **`consumers`**: `Dict[str, Set[str]]` - ref history_id 到消费它的 call history_id 集合的映射（每个 ref 可有多个消费者）

### 对象变量
- **`refs`**: `Dict[str, Union[Ref, Any]]` - history_id 到 Ref 对象的映射，存储实际的引用对象
- **`calls`**: `Dict[str, Call]` - history_id 到 Call 对象的映射，存储实际的调用对象
- **`storage`**: `Storage` - 关联的存储实例，用于数据持久化和对象解析

## 属性（Properties）

### `vnames` -> `Set[str]`
**用途**: 获取所有变量节点的名称集合
**实现**: `return set(self.vs.keys())`
**调用场景**: 遍历所有变量、检查变量存在性、统计变量数量

### `fnames` -> `Set[str]`
**用途**: 获取所有函数节点的名称集合
**实现**: `return set(self.fs.keys())`
**调用场景**: 遍历所有函数、检查函数存在性、统计函数数量

### `nodes` -> `Set[str]`
**用途**: 获取所有节点（变量和函数）的名称集合
**实现**: `return self.vnames | self.fnames`
**依赖**: 调用 `vnames` 和 `fnames` 属性
**调用场景**: 图遍历、节点验证、整体图操作

### `sources` -> `Set[str]`
**用途**: 获取没有输入边的变量节点集合（图的源节点）
**实现**: `return {node for node in self.vs.keys() if len(self.inp[node]) == 0}`
**调用场景**: 查找计算起点、数据流分析、拓扑排序

### `sinks` -> `Set[str]`
**用途**: 获取没有输出边的变量节点集合（图的汇点）
**实现**: `return {node for node in self.vs.keys() if len(self.out[node]) == 0}`
**调用场景**: 查找计算终点、数据流分析、结果提取

### `sets` -> `Dict[str, Set[str]]`
**用途**: 获取所有节点到其元素集合的映射
**实现**: `return {**self.vs, **self.fs}`
**调用场景**: 统一访问变量和函数的元素、集合操作

### `values` -> `Dict[str, Union[Set[Ref], Set[Call]]]`
**用途**: 获取所有节点到其值集合的映射
**实现**: 
- 变量节点：`{vname: self.get_var_values(vname) for vname in self.vnames}`
- 函数节点：`{fname: {self.calls[call_hid] for call_hid in call_hids} for fname, call_hids in self.fs.items()}`
**依赖**: 调用 `get_var_values` 方法
**调用场景**: 获取实际的 Ref 和 Call 对象而非 ID

## 核心方法

### 图操作方法

#### `ops() -> Dict[str, Op]`
**用途**: 获取函数名到 Op 对象的映射
**参数**: 无
**返回**: `Dict[str, Op]` - 函数名到操作对象的字典
**实现逻辑**:
- 遍历所有函数节点
- 从每个函数的第一个调用中提取 Op 对象
- 如果函数节点为空则抛出 NotImplementedError
**调用场景**: 获取函数对应的操作定义、操作元数据查询
**异常**: 当函数节点为空时抛出 `NotImplementedError`

#### `refs_by_var() -> Dict[str, Set[Ref]]`
**用途**: 获取变量名到 Ref 对象集合的映射
**参数**: 无
**返回**: `Dict[str, Set[Ref]]` - 变量名到引用对象集合的字典
**实现**: `{vname: {self.refs[hid] for hid in hids} for vname, hids in self.vs.items()}`
**依赖**: 访问 `self.vs` 和 `self.refs`
**调用场景**: 获取变量的实际引用对象、数据提取、值访问

#### `calls_by_func() -> Dict[str, Set[Call]]`
**用途**: 获取函数名到 Call 对象集合的映射
**参数**: 无
**返回**: `Dict[str, Set[Call]]` - 函数名到调用对象集合的字典
**实现**: `{fname: {self.calls[hid] for hid in hids} for fname, hids in self.fs.items()}`
**依赖**: 访问 `self.fs` 和 `self.calls`
**调用场景**: 获取函数的实际调用对象、调用历史分析、参数检查

#### `edges() -> List[Tuple[str, str, str]]`
**用途**: 获取计算图中所有边的列表
**参数**: 无
**返回**: `List[Tuple[str, str, str]]` - (源节点, 目标节点, 边标签) 元组列表
**实现逻辑**:
- 遍历输出邻接表 `self.out`
- 对每个节点的每个输出标签和目标节点生成边元组
**调用场景**: 图遍历、拓扑排序、依赖分析、可视化

### 修改 ComputationFrame 的方法

#### 批量操作

##### `drop(nodes: Iterable[str], inplace: bool = False, with_dependents: bool = False) -> Optional[ComputationFrame]`
**用途**: 批量删除指定的节点
**参数**:
- `nodes: Iterable[str]` - 要删除的节点名称列表
- `inplace: bool = False` - 是否就地修改
- `with_dependents: bool = False` - 是否同时删除依赖节点（未实现）
**返回**: 如果 `inplace=False` 返回新的 ComputationFrame，否则返回 None
**实现**: 遍历节点列表，对每个节点调用 `drop_node`
**调用**: 内部调用 `drop_node(node, inplace=True)`
**异常**: 当 `with_dependents=True` 时抛出 `NotImplementedError`

##### `drop_node(node: str, inplace: bool = False) -> Optional[ComputationFrame]`
**用途**: 删除单个节点（变量或函数）
**参数**:
- `node: str` - 要删除的节点名称
- `inplace: bool = False` - 是否就地修改
**返回**: 如果 `inplace=False` 返回新的 ComputationFrame，否则返回 None
**实现逻辑**:
- 检查节点类型（变量或函数）
- 调用相应的 `drop_var` 或 `drop_func` 方法
**调用**: 根据节点类型调用 `drop_var` 或 `drop_func`
**异常**: 当节点不存在时抛出 `ValueError`

##### `rename(vars: Optional[Dict[str, str]] = None, funcs: Optional[Dict[str, str]] = None, inplace: bool = False) -> Optional[ComputationFrame]`
**用途**: 批量重命名变量或函数
**参数**:
- `vars: Optional[Dict[str, str]]` - 变量重命名映射 {旧名: 新名}
- `funcs: Optional[Dict[str, str]]` - 函数重命名映射 {旧名: 新名}（未实现）
- `inplace: bool = False` - 是否就地修改
**返回**: 如果 `inplace=False` 返回新的 ComputationFrame，否则返回 None
**实现**: 遍历重命名映射，对每个变量调用 `rename_var`
**调用**: 内部调用 `rename_var(vname, new_vname, inplace=True)`
**异常**: 当重命名函数时抛出 `NotImplementedError`

#### 变量操作

##### `_add_var(vname: Optional[str]) -> str`
**用途**: 内部方法，向计算框架中添加新的变量节点
**参数**:
- `vname: Optional[str]` - 变量名，如果为 None 则自动生成
**返回**: `str` - 实际使用的变量名
**实现逻辑**:
- 如果 vname 为 None，调用 `get_new_vname("v")` 生成新名称
- 初始化变量的集合、输入和输出邻接表
**调用**: 内部调用 `get_new_vname` 方法
**使用场景**: 扩展操作、构造方法中创建新变量

##### `drop_var(vname: str, inplace: bool = False) -> Optional[ComputationFrame]`
**用途**: 删除变量节点及其所有相关数据
**参数**:
- `vname: str` - 要删除的变量名
- `inplace: bool = False` - 是否就地修改
**返回**: 如果 `inplace=False` 返回新的 ComputationFrame，否则返回 None
**实现逻辑**:
- 删除所有与该变量相关的边
- 删除变量包含的所有引用
- 清理变量的邻接表
**调用**: 内部调用 `_drop_edge` 和 `drop_ref` 方法
**副作用**: 可能删除不被其他变量引用的 Ref 对象

##### `rename_var(vname: str, new_vname: str, inplace: bool = False) -> Optional[ComputationFrame]`
**用途**: 重命名变量节点
**参数**:
- `vname: str` - 原变量名
- `new_vname: str` - 新变量名
- `inplace: bool = False` - 是否就地修改
**返回**: 如果 `inplace=False` 返回新的 ComputationFrame，否则返回 None
**实现逻辑**:
- 更新变量集合和邻接表
- 更新所有邻接表中对该变量的引用
- 更新引用反向索引
**复杂度**: O(节点数 + 边数)，需要更新所有相关引用

##### `add_ref(vname: str, ref: Ref, allow_existing: bool = False)`
**用途**: 向变量添加引用对象
**参数**:
- `vname: str` - 目标变量名
- `ref: Ref` - 要添加的引用对象
- `allow_existing: bool = False` - 是否允许添加已存在的引用
**返回**: 无
**实现逻辑**:
- 检查引用是否已存在
- 更新引用字典和变量集合
- 更新引用反向索引
**异常**: 当引用已存在且 `allow_existing=False` 时抛出 `ValueError`

##### `drop_ref(vname: str, hid: str)`
**用途**: 从变量中删除指定的引用
**参数**:
- `vname: str` - 变量名
- `hid: str` - 引用的 history_id
**返回**: 无
**实现逻辑**:
- 从变量集合中移除引用
- 如果这是唯一引用该对象的变量，则完全删除引用及其相关数据
- 否则只更新反向索引
**副作用**: 可能删除创建者和消费者映射

#### 函数操作
- **`drop_func(fname, inplace=False)`** - 删除函数节点
- **`add_call(fname, call, with_refs, allow_existing=False)`** - 添加调用到函数
- **`drop_call(fname, hid)`** - 从函数中删除调用

#### 边操作
- **`_add_edge(src, dst, label, allow_existing=False)`** - 添加边（内部方法）
- **`_drop_edge(src, dst, label)`** - 删除边（内部方法）

### 图遍历和导航方法

#### 邻居查询
- **`in_neighbors(node) -> Set[str]`** - 获取节点的输入邻居
- **`out_neighbors(node) -> Set[str]`** - 获取节点的输出邻居
- **`in_edges(node) -> Set[Tuple[str, str, str]]`** - 获取指向节点的所有边
- **`out_edges(node) -> Set[Tuple[str, str, str]]`** - 获取从节点出发的所有边

#### 路径和可达性
- **`get_reachable_nodes(nodes, direction) -> Set[str]`** - 获取可达节点
- **`get_all_edges_on_paths_between(start, end) -> Set[Tuple[str, str]]`** - 获取路径上的所有边

#### 拓扑排序
- **`topsort_modulo_sccs() -> List[str]`** - 返回几乎拓扑的排序
- **`sort_nodes(nodes) -> List[str]`** - 对给定节点进行拓扑排序

### 选择和过滤方法

#### 节点选择
- **`select_nodes(nodes) -> ComputationFrame`** - 选择指定节点的子图
- **`select_subsets(elts) -> ComputationFrame`** - 限制到每个节点的指定元素

#### 方向性选择
- **`downstream(*nodes, how="strong") -> ComputationFrame`** - 获取下游计算
- **`upstream(*nodes, how="strong") -> ComputationFrame`** - 获取上游计算
- **`midstream(*nodes, how="strong") -> ComputationFrame`** - 获取节点间的子程序

#### 条件过滤
- **`__lt__(other) -> ComputationFrame`** - 小于比较过滤
- **`isin(values, by="val", node_class="var") -> ComputationFrame`** - 成员检查过滤

### 扩展方法

#### 单向扩展

##### `expand_back(varnames=None, recursive=False, skip_existing=False, inplace=False, verbose=False, reuse_existing=True) -> Optional[ComputationFrame]`
**用途**: 向后扩展计算框架，添加创建当前变量的调用
**参数**:
- `varnames: Optional[Union[str, Iterable[str]]]` - 要扩展的变量名，None 表示扩展所有变量
- `recursive: bool = False` - 是否递归扩展直到固定点
- `skip_existing: bool = False` - 是否跳过已存在的调用
- `inplace: bool = False` - 是否就地修改
- `verbose: bool = False` - 是否显示详细信息
- `reuse_existing: bool = True` - 是否重用现有节点
**返回**: 扩展后的 ComputationFrame 或 None（如果 inplace=True）
**实现逻辑**:
- 找到没有创建者的引用（源元素）
- 从存储中获取创建这些引用的调用
- 按输出分组调用并添加到图中
**调用**: 内部调用 `_expand_unidirectional(direction="back", ...)`
**使用场景**: 追踪数据来源、构建完整的计算历史

##### `expand_forward(varnames=None, recursive=False, skip_existing=False, inplace=False, verbose=False, reuse_existing=True) -> Optional[ComputationFrame]`
**用途**: 向前扩展计算框架，添加消费当前变量的调用
**参数**:
- `varnames: Optional[Union[str, Set[str]]]` - 要扩展的变量名，None 表示扩展所有变量
- `recursive: bool = False` - 是否递归扩展直到固定点
- `skip_existing: bool = False` - 是否跳过已存在的调用
- `inplace: bool = False` - 是否就地修改
- `verbose: bool = False` - 是否显示详细信息
- `reuse_existing: bool = True` - 是否重用现有节点
**返回**: 扩展后的 ComputationFrame 或 None（如果 inplace=True）
**实现逻辑**:
- 找到没有消费者的引用（汇元素）
- 从存储中获取消费这些引用的调用
- 按输入分组调用并添加到图中
**调用**: 内部调用 `_expand_unidirectional(direction="forward", ...)`
**使用场景**: 追踪数据使用、发现下游计算

##### `expand_all(inplace=False, skip_existing=False, verbose=False, reuse_existing=True) -> Optional[ComputationFrame]`
**用途**: 全方向扩展计算框架直到固定点
**参数**:
- `inplace: bool = False` - 是否就地修改
- `skip_existing: bool = False` - 是否跳过已存在的调用
- `verbose: bool = False` - 是否显示详细信息
- `reuse_existing: bool = True` - 是否重用现有节点
**返回**: 完全扩展的 ComputationFrame 或 None（如果 inplace=True）
**实现逻辑**:
- 反复调用 `expand_back` 和 `expand_forward`
- 直到图的大小不再变化（固定点）
**调用**: 循环调用 `expand_back` 和 `expand_forward`
**使用场景**: 获取完整的计算图、全面的依赖分析

#### 内部扩展方法

##### `_expand_unidirectional(direction, reuse_existing, recursive, varnames=None, skip_existing=False, inplace=False, verbose=False) -> Optional[ComputationFrame]`
**用途**: 单向扩展的核心实现
**参数**:
- `direction: Literal["back", "forward"]` - 扩展方向
- `reuse_existing: bool` - 是否重用现有节点
- `recursive: bool` - 是否递归扩展
- 其他参数同公共扩展方法
**实现逻辑**:
- 获取可扩展的元素（源或汇）
- 从存储获取相关调用
- 调用 `_group_calls` 和 `_expand_from_call_groups`
**调用**: 被 `expand_back` 和 `expand_forward` 调用

##### `_group_calls(calls, available_nodes, by) -> Dict[Tuple, List[Call]]`
**用途**: 按连接方式对调用进行分组
**参数**:
- `calls: List[Call]` - 要分组的调用列表
- `available_nodes: Iterable[str]` - 可用的节点
- `by: Literal["inputs", "outputs"]` - 按输入还是输出分组
**返回**: 分组后的调用字典，键为 (op_id, connections) 元组
**实现逻辑**:
- 分析每个调用的输入/输出如何连接到现有变量
- 生成规范化的分组键
- 确保确定性的分组行为
**使用场景**: 扩展过程中的调用组织

##### `_expand_from_call_groups(call_groups, side_to_glue, reuse_existing, verbose=False)`
**用途**: 从调用组扩展计算框架
**参数**:
- `call_groups: Dict` - 分组的调用
- `side_to_glue: Literal["inputs", "outputs"]` - 要连接的一侧
- `reuse_existing: bool` - 是否重用现有节点
- `verbose: bool = False` - 是否显示详细信息
**实现逻辑**:
- 为每个调用组创建或重用函数节点
- 创建必要的变量节点和边
- 添加调用到相应的函数节点
**调用**: 内部调用 `_add_func`, `_add_var`, `_add_edge`, `add_call`

### 集合操作方法

#### 二元操作
- **`_binary_union(a, b) -> ComputationFrame`** - 两个 CF 的并集
- **`_binary_intersection(a, b) -> ComputationFrame`** - 两个 CF 的交集
- **`_binary_setwise_difference(a, b) -> ComputationFrame`** - 集合差集
- **`_binary_difference(a, b) -> ComputationFrame`** - 结构差集

#### 多元操作
- **`union(*cfs) -> ComputationFrame`** - 多个 CF 的并集
- **`intersection(*cfs) -> ComputationFrame`** - 多个 CF 的交集

#### 运算符重载
- **`__or__(other) -> ComputationFrame`** - 并集运算符 `|`
- **`__and__(other) -> ComputationFrame`** - 交集运算符 `&`
- **`__sub__(other) -> ComputationFrame`** - 差集运算符 `-`

### 计算历史和评估方法

#### 历史追踪

##### `get_direct_history(vname: str, hids: Set[str], include_calls: bool) -> Dict[str, Set[str]]`
**用途**: 获取指定引用的直接计算历史（一步依赖）
**参数**:
- `vname: str` - 变量名
- `hids: Set[str]` - 要追踪的引用 history_id 集合
- `include_calls: bool` - 是否在结果中包含调用节点
**返回**: `Dict[str, Set[str]]` - 节点名到相关元素 ID 集合的映射
**实现逻辑**:
- 对每个引用查找其创建者调用
- 追踪创建者调用的输入引用
- 通过图的边关系确定连接的变量
**调用**: 内部调用 `get_name_proj`, `get_reverse_proj`
**使用场景**: 构建计算依赖树、调试数据流

##### `get_total_history(node: str, hids: Set[str], result=None, include_calls=False) -> Dict[str, Set[str]]`
**用途**: 递归获取完整的计算历史（所有上游依赖）
**参数**:
- `node: str` - 起始节点名
- `hids: Set[str]` - 起始元素 ID 集合
- `result: Optional[Dict[str, Set[str]]]` - 累积结果（用于递归）
- `include_calls: bool = False` - 是否包含调用节点
**返回**: `Dict[str, Set[str]]` - 完整历史的节点到元素映射
**实现逻辑**:
- 递归调用 `get_direct_history`
- 使用固定点算法避免无限递归
- 合并所有层级的历史信息
**调用**: 递归调用 `get_direct_history` 和自身
**使用场景**: 完整的血缘分析、影响性分析

##### `get_history_df(vname: str, include_calls=True, verbose=False) -> pd.DataFrame`
**用途**: 将变量的完整历史转换为 DataFrame 格式
**参数**:
- `vname: str` - 变量名
- `include_calls: bool = True` - 是否包含调用列
- `verbose: bool = False` - 是否显示详细信息
**返回**: `pd.DataFrame` - 每行代表一个引用的完整历史
**实现逻辑**:
- 对变量中的每个引用调用 `get_total_history`
- 将历史信息组织为表格行
- 处理单例集合的解包
**调用**: 内部调用 `get_total_history`, `_sort_df`
**使用场景**: 数据谱系分析、历史查询

##### `get_joint_history_df(varnames, how="outer", include_calls=True, verbose=False) -> pd.DataFrame`
**用途**: 获取多个变量的联合计算历史
**参数**:
- `varnames: Iterable[str]` - 变量名列表
- `how: Literal["inner", "outer"] = "outer"` - 连接方式
- `include_calls: bool = True` - 是否包含调用列
- `verbose: bool = False` - 是否显示详细信息
**返回**: `pd.DataFrame` - 联合历史表
**实现逻辑**:
- 为每个变量获取历史 DataFrame
- 按共同列进行连接操作
- 处理复杂的引用对象类型
**调用**: 内部调用 `get_history_df`, `pd.merge`
**使用场景**: 多变量关联分析、复杂查询

#### 数据提取

##### `eval(*nodes, values="objs", verbose=True) -> pd.DataFrame`
**用途**: 一站式数据加载方法，简化的 df() 调用
**参数**:
- `*nodes: str` - 要提取的节点名
- `values: Literal["refs", "objs"] = "objs"` - 返回引用还是实际对象
- `verbose: bool = True` - 是否显示详细信息
**返回**: `pd.DataFrame` - 提取的数据
**实现**: 直接调用 `self.df(*nodes, include_calls=True, values=values, verbose=verbose)`
**使用场景**: 快速数据提取、交互式分析

##### `df(*nodes, values="objs", lazy_vars=None, verbose=False, include_calls=True, join_how="outer") -> pd.DataFrame`
**用途**: 通用数据提取方法，从计算框架提取结构化数据
**参数**:
- `*nodes: str` - 要包含的节点名
- `values: Literal["refs", "objs"] = "objs"` - 返回类型
- `lazy_vars: Optional[Iterable[str]] = None` - 延迟评估的变量
- `verbose: bool = False` - 详细模式
- `include_calls: bool = True` - 是否包含调用列
- `join_how: Literal["inner", "outer"] = "outer"` - 连接方式
**返回**: `pd.DataFrame` - 结构化的计算数据
**实现逻辑**:
- 使用 `midstream` 获取相关子图
- 调用 `get_joint_history_df` 获取联合历史
- 根据参数评估或保持引用形式
**调用**: 内部调用 `midstream`, `get_joint_history_df`, `eval_df`
**使用场景**: 复杂数据提取、自定义查询

##### `eval_df(df, skip_cols=None, skip_calls=False) -> pd.DataFrame`
**用途**: 评估 DataFrame 中的引用和调用对象
**参数**:
- `df: pd.DataFrame` - 包含引用的 DataFrame
- `skip_cols: Optional[Iterable[str]] = None` - 跳过评估的列
- `skip_calls: bool = False` - 是否跳过调用列
**返回**: `pd.DataFrame` - 评估后的 DataFrame
**实现逻辑**:
- 分类对象类型（Ref, Call, 值）
- 对引用对象调用 `storage.unwrap`
- 保持指定列的原始形式
**调用**: 内部调用 `self.storage.unwrap`
**使用场景**: 延迟评估、选择性对象解析

#### 值获取

##### `get(hids: Set[str]) -> Set[Ref]`
**用途**: 根据 history_id 集合获取对应的 Ref 对象
**参数**: `hids: Set[str]` - history_id 集合
**返回**: `Set[Ref]` - 对应的 Ref 对象集合
**实现**: `return {self.refs[hid] for hid in hids}`
**使用场景**: ID 到对象的转换、批量对象获取

##### `get_var_values(vname: str) -> Set[Ref]`
**用途**: 获取变量包含的所有 Ref 对象
**参数**: `vname: str` - 变量名
**返回**: `Set[Ref]` - 变量包含的 Ref 对象集合
**实现**: `return {self.refs[ref_uid] for ref_uid in self.vs[vname]}`
**使用场景**: 变量内容访问、数据提取

##### `get_func_table(fname: str) -> pd.DataFrame`
**用途**: 获取函数的调用表，包含所有调用的输入输出信息
**参数**: `fname: str` - 函数名
**返回**: `pd.DataFrame` - 调用表，列为输入输出参数，行为各次调用
**实现逻辑**:
- 遍历函数的所有调用
- 提取每次调用的输入输出引用
- 组织为表格形式
**使用场景**: 函数调用分析、参数统计、调试

### 可达性分析方法

#### 元素可达性
- **`get_adj_elts_edge(edge, hids, direction)`** - 获取沿边连接的元素
- **`get_adj_elts(node, hids, direction)`** - 获取邻接元素
- **`get_reachable_elts(initial_state, direction, how, pad=True)`** - 获取可达元素
- **`get_reachable_elts_acyclic(...)`** - 无环图的可达元素

#### 源和汇元素
- **`get_source_elts() -> Dict[str, Set[str]]`** - 获取源元素
- **`get_sink_elts() -> Dict[str, Set[str]]`** - 获取汇元素

### 工具和辅助方法

#### 内部工具
- **`get_names_projecting_to(call_hid, label) -> Set[str]`** - 获取投影到标签的名称
- **`get_io_proj(call_hid, name) -> str`** - 获取 I/O 名称的投影标签
- **`_check()`** - 检查不变量
- **`_sort_df(df) -> pd.DataFrame`** - 按拓扑顺序排序数据框

#### 名称生成
- **`get_new_vname(name_hint) -> str`** - 生成新的变量名
- **`get_new_fname(name_hint) -> str`** - 生成新的函数名

### 合并和清理方法

#### 节点合并
- **`move_ref(source_vname, target_vname, hid, inplace=True)`** - 移动引用
- **`merge_into(node_to_merge, merge_into, inplace=False)`** - 合并节点
- **`merge_vars(inplace=False)`** - 合并变量
- **`merge(vars, new_name=None) -> str`** - 合并变量（未实现）
- **`split(var)`** - 分割变量（未实现）

#### 清理操作
- **`drop_unreachable(direction, how="strong")`** - 删除不可达元素
- **`simplify()`** - 简化图结构
- **`cleanup(inplace=False)`** - 清理空节点

### 构造方法（静态方法）

#### 从不同源创建 ComputationFrame
- **`from_op(storage, f) -> ComputationFrame`** - 从操作创建
- **`from_refs(storage, refs) -> ComputationFrame`** - 从引用创建
- **`from_vars(storage, vars) -> ComputationFrame`** - 从变量创建

### 删除方法

#### 存储删除
- **`delete_calls()`** - 从存储中删除调用
- **`delete_calls_from_df(df)`** - 从数据框删除调用

### 可视化和信息方法

#### 图形可视化
- **`draw(show_how=None, path=None, verbose=False, ...)`** - 绘制计算图

#### 信息显示
- **`print_graph()`** - 打印图描述
- **`get_graph_desc() -> str`** - 获取图描述字符串
- **`info(*nodes)`** - 显示节点信息
- **`var_info(vname)`** - 显示变量信息
- **`func_info(fname)`** - 显示函数信息

#### 统计信息
- **`get_var_stats() -> pd.DataFrame`** - 获取变量统计
- **`get_func_stats() -> pd.DataFrame`** - 获取函数统计

### 其他方法

#### 对象操作
- **`copy() -> ComputationFrame`** - 复制 ComputationFrame
- **`attach()`** - 附加到存储
- **`apply(f, to="vals") -> ComputationFrame`** - 应用函数到值

#### 索引和访问
- **`__getitem__(indexer) -> ComputationFrame`** - 索引访问
- **`__repr__() -> str`** - 字符串表示
- **`_ipython_key_completions_()`** - IPython 自动补全

#### 内部工具方法
- **`_unify_subobjects(a, b) -> Dict[str, Set[str]]`** - 统一子对象
- **`_is_subobject(a, b) -> bool`** - 检查子对象关系
- **`_get_prettytable_str(df) -> str`** - 获取美化表格字符串
- **`_add_adj_calls(vars_view) -> Dict[str, Set[str]]`** - 添加邻接调用

## 使用模式

### 基本使用
```python
# 创建 ComputationFrame
cf = storage.cf(some_function)

# 扩展以获取完整计算图
cf = cf.expand_all()

# 获取数据
df = cf.eval()
```

### 图操作
```python
# 选择特定节点
sub_cf = cf.select_nodes(['var1', 'func1'])

# 获取下游计算
downstream_cf = cf.downstream('input_var')

# 合并多个 ComputationFrame
combined_cf = cf1 | cf2
```

### 数据提取
```python
# 获取特定变量的值
values = cf.get_var_values('variable_name')

# 获取函数调用表
table = cf.get_func_table('function_name')

# 获取联合历史
df = cf.df('var1', 'var2', 'func1')
```

## 设计理念

ComputationFrame 的设计基于以下核心理念：

1. **图结构**: 计算被表示为有向图，其中节点是变量和操作，边表示数据流
2. **批量操作**: 支持对整个计算图进行批量操作，而不是逐个处理元素
3. **pandas 兼容性**: API 设计尽可能与 pandas DataFrame 保持一致
4. **计算可达性**: 强调计算上的可达性而不仅仅是图上的可达性
5. **记忆化**: 利用存储中的记忆化调用和引用进行高效计算

这个类是 mandala 框架的核心，提供了强大而灵活的计算图操作能力。

## 文档完善状态

### ✅ 已详细完善的部分
1. **辅助函数** - `get_name_proj`, `get_reverse_proj` 的详细说明
2. **初始化方法** - `__init__` 的完整参数说明和初始化逻辑
3. **核心验证** - `_check` 方法的详细不变量检查说明
4. **实例变量** - 所有变量的详细用途和数据结构说明
5. **属性方法** - 7个属性的实现细节和使用场景
6. **图操作方法** - 4个核心图操作方法的详细说明
7. **批量操作** - `drop`, `drop_node`, `rename` 的完整实现逻辑
8. **变量操作** - 5个变量操作方法的详细参数和实现说明
9. **扩展方法** - 6个扩展方法的完整参数、逻辑和调用关系
10. **计算历史和评估** - 9个历史追踪和数据提取方法的详细说明

### 📋 待进一步完善的部分
1. **函数操作方法** - `_add_func`, `drop_func`, `add_call`, `drop_call` 等
2. **边操作方法** - `_add_edge`, `_drop_edge` 的详细实现
3. **图遍历方法** - 邻居查询、路径查找、拓扑排序等方法
4. **选择和过滤方法** - 节点选择、方向性选择、条件过滤等
5. **集合操作方法** - 并集、交集、差集等二元和多元操作
6. **可达性分析方法** - 元素可达性、源汇分析等复杂算法
7. **工具和辅助方法** - 内部工具、名称生成、数据格式化等
8. **合并和清理方法** - 节点合并、图简化、清理操作等
9. **构造方法** - 静态构造方法的详细说明
10. **可视化和信息方法** - 图形可视化、统计信息、调试输出等

### 📊 文档统计
- **总方法数**: 100+ 个方法和属性
- **已详细完善**: 约 30 个核心方法（30%）
- **基础覆盖**: 所有方法都有基本说明
- **深度覆盖**: 核心方法有详细的参数、实现、调用关系说明

### 🎯 使用建议
1. **入门用户**: 重点阅读"设计理念"、"使用模式"和"属性方法"部分
2. **开发者**: 关注"扩展方法"、"计算历史"和"数据提取"部分
3. **调试分析**: 参考"核心验证"、"可达性分析"和"工具方法"部分
4. **高级用户**: 深入了解"集合操作"、"图遍历"和"内部实现"部分

这份文档为 ComputationFrame 类提供了全面的技术参考，涵盖了从基础使用到高级功能的完整说明。 
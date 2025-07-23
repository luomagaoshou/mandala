 # Storage 类完整文档

## 概述

`Storage` 是 mandala 框架的核心存储类，负责管理计算历史的持久化、缓存、版本控制和记忆化执行。它提供了对函数调用、引用对象和依赖关系的统一存储接口，支持多种后端存储方式和智能缓存机制。Storage 类是整个 mandala 生态系统的基础设施。

## 辅助类

### `noop` 上下文管理器

```python
class noop:
    """
    A noop context manager that sets the mode to 'noop' without reference to the
    storage object. Requires that a context is already active.
    """
```

**用途**: 在已有上下文中设置无操作模式，用于调用 @op 而不触发实际存储
**特点**:
- 不需要直接引用 Storage 对象
- 要求已有活动上下文
- 临时切换执行模式

## 类定义

```python
class Storage:
    """
    核心存储类，管理计算历史的持久化、缓存和版本控制
    """
```

## 初始化方法

### `__init__(self, db_path=":memory:", overflow_dir=None, overflow_threshold_MB=50.0, ...)`

**用途**: 初始化 Storage 实例，配置数据库、缓存、版本控制等组件
**参数详解**:

| 参数名 | 类型 | 默认值 | 详细描述 |
|--------|------|--------|----------|
| `db_path` | `str` | `":memory:"` | 数据库文件路径，":memory:" 表示内存数据库 |
| `overflow_dir` | `Optional[str]` | `None` | 大对象溢出目录路径，用于存储超过阈值的对象 |
| `overflow_threshold_MB` | `Optional[Union[int, float]]` | `50.0` | 溢出阈值（MB），超过此大小的对象存储到文件 |
| `deps_path` | `Optional[Union[str, Path]]` | `None` | 依赖追踪根目录，None 表示禁用版本控制 |
| `tracer_impl` | `Optional[type]` | `None` | 追踪器实现类，默认使用 DecTracer |
| `strict_tracing` | `bool` | `False` | 是否启用严格追踪模式 |
| `skip_unhashable_globals` | `bool` | `True` | 是否跳过无法哈希的全局变量 |
| `skip_globals_silently` | `bool` | `False` | 是否静默跳过全局变量 |
| `skip_missing_deps` | `bool` | `True` | 是否允许缺失的依赖 |
| `skip_missing_silently` | `bool` | `False` | 是否静默跳过缺失依赖 |
| `deps_package` | `Optional[str]` | `None` | 依赖包名 |
| `track_globals` | `bool` | `True` | 是否追踪全局变量 |

**初始化逻辑**:
1. **数据库适配器**: 创建 `DBAdapter` 实例管理 SQLite 连接
2. **调用存储**: 设置 SQLite + 缓存的两层调用存储
3. **溢出存储**: 根据配置创建 Joblib 文件存储用于大对象
4. **多重缓存**: 分别为 atoms、shapes、ops、sources 创建缓存层
5. **版本控制**: 初始化或恢复 Versioner 实例
6. **运行时状态**: 初始化模式栈和执行配置

## 实例变量

### 数据库和适配器
- **`db`**: `DBAdapter` - 数据库连接适配器，管理 SQLite 连接池
- **`overflow_dir`**: `Optional[str]` - 溢出目录路径
- **`overflow_threshold_MB`**: `Optional[Union[int, float]]` - 溢出阈值
- **`overflow_storage`**: `Optional[JoblibDictStorage]` - 大对象文件存储

### 存储层次
- **`call_storage`**: `SQLiteCallStorage` - 调用的持久化存储层
- **`calls`**: `CachedCallStorage` - 调用的缓存层，包装持久化层
- **`call_cache`**: 调用缓存的直接引用
- **`atoms`**: `CachedDictStorage` - 原子对象的缓存+持久化存储
- **`shapes`**: `CachedDictStorage` - 引用形状的缓存+持久化存储
- **`ops`**: `CachedDictStorage` - 操作定义的缓存+持久化存储
- **`sources`**: `CachedDictStorage` - 源代码和版本信息存储

### 版本控制配置
- **`_deps_path`**: 依赖追踪根路径
- **`_tracer_impl`**: 追踪器实现类
- **`_strict_tracing`**: 严格追踪模式标志
- **`_skip_unhashable_globals`**: 跳过无法哈希全局变量标志
- **`_skip_globals_silently`**: 静默跳过全局变量标志
- **`_skip_missing_deps`**: 允许缺失依赖标志
- **`_skip_missing_silently`**: 静默跳过缺失依赖标志
- **`_deps_package`**: 依赖包名
- **`_track_globals`**: 追踪全局变量标志
- **`_versioned`**: 是否启用版本控制标志

### 运行时状态
- **`cached_versioner`**: `Optional[Versioner]` - 缓存的版本控制器
- **`code_state`**: `Optional[CodeState]` - 当前代码状态
- **`suspended_trace_obj`**: 挂起的追踪对象
- **`_exit_hooks`**: `List[Callable]` - 退出钩子函数列表
- **`_mode_stack`**: `List[str]` - 执行模式栈
- **`_next_mode`**: `str` - 下一个执行模式
- **`_allow_new_calls`**: `bool` - 是否允许新调用

## 属性（Properties）

### `mode` -> `str`
**用途**: 获取当前执行模式
**实现**: `return self._mode_stack[-1] if self._mode_stack else 'run'`
**可能值**: `'run'`（正常执行）、`'noop'`（无操作模式）
**调用场景**: 决定 @op 函数的执行行为

### `versioned` -> `bool`
**用途**: 检查是否启用了版本控制
**实现**: `return self._versioned`
**调用场景**: 条件性版本控制逻辑、功能可用性检查

## 配置和连接方法

### `dump_config() -> Dict[str, Any]`
**用途**: 导出当前存储配置为字典
**返回**: 包含所有配置参数的字典
**使用场景**: 配置备份、调试、存储配置复制

### `conn() -> sqlite3.Connection`
**用途**: 获取数据库连接对象
**返回**: SQLite 连接实例
**使用场景**: 直接数据库操作、事务管理、原生 SQL 查询

### `vacuum()`
**用途**: 执行数据库压缩操作，回收空间
**功能**: 调用 SQLite 的 VACUUM 命令
**使用场景**: 定期维护、空间优化、删除操作后的清理

## 运行时配置方法

### `allow_new_calls(allow: bool)`
**用途**: 设置是否允许执行新的函数调用
**参数**: `allow` - 是否允许新调用
**功能**: 控制 @op 函数的执行行为
**使用场景**: 只读模式、调试、性能分析

### `in_context() -> bool`
**用途**: 检查当前是否在 Storage 上下文中
**返回**: 是否有活动的上下文
**实现**: 检查 `Context.current_context` 是否为 None
**使用场景**: 上下文依赖的功能、错误检查

## 缓存管理方法

### `clear_cache(allow_uncommitted: bool = False)`
**用途**: 清空所有缓存，可选择性保留未提交数据
**参数**: `allow_uncommitted` - 是否允许清除未提交的脏数据
**功能**: 依次清空 atoms、shapes、ops、calls 缓存
**使用场景**: 内存管理、调试、缓存重建

### `cache_info() -> str`
**用途**: 显示缓存状态信息的美化表格
**返回**: 无（打印到标准输出）
**功能**: 显示各缓存的大小和脏数据数量
**实现**: 使用 pandas DataFrame 和 prettytable 格式化输出
**使用场景**: 性能监控、调试、缓存状态检查

### 预加载方法

#### `preload_calls()`
**用途**: 预加载所有调用数据到缓存
**功能**: 从数据库加载调用 DataFrame 和 HID 集合
**使用场景**: 批量操作前的性能优化

#### `preload_shapes()`
**用途**: 预加载所有引用形状到缓存
**使用场景**: 引用密集操作的性能优化

#### `preload_ops()`
**用途**: 预加载所有操作定义到缓存
**使用场景**: 操作查询密集场景的优化

#### `preload_atoms()`
**用途**: 预加载所有原子对象到缓存
**警告**: 可能消耗大量内存
**使用场景**: 小规模数据集的全量加载

#### `preload(lazy: bool = True)`
**用途**: 执行批量预加载，可选择是否包含原子对象
**参数**: `lazy` - 是否跳过原子对象加载
**功能**: 依次调用 calls、shapes、ops 预加载，条件性加载 atoms
**使用场景**: 系统初始化、批处理优化

### `commit()`
**用途**: 将所有缓存中的脏数据持久化到数据库
**功能**: 在事务中依次提交 atoms、shapes、ops、sources、calls
**使用场景**: 数据保存、上下文退出、关键点检查

## 引用接口方法

### 引用保存和加载

#### `save_ref(ref: Ref)`
**用途**: 保存引用对象及其依赖到存储
**参数**: `ref` - 要保存的引用对象
**功能**: 根据引用类型递归保存内容和形状
**实现逻辑**:
- **AtomRef**: 保存原子对象和形状
- **ListRef**: 保存形状并递归保存元素
- **DictRef**: 保存形状并递归保存键值对
- **幂等性**: 已存在的引用不重复保存

#### `load_ref(hid: str, in_memory: bool = False) -> Ref`
**用途**: 根据历史ID加载引用对象
**参数**:
- `hid` - 引用的历史ID
- `in_memory` - 是否加载到内存（AtomRef的内存控制）
**返回**: 加载的引用对象
**实现逻辑**:
- 根据形状类型选择加载策略
- 递归构建复合引用结构
- 处理内存/磁盘存储切换

### 引用清理方法

#### `_drop_ref_hid(hid: str, verify: bool = False)`
**用途**: 内部方法，根据历史ID删除引用
**参数**:
- `hid` - 要删除的历史ID
- `verify` - 是否验证引用未被调用使用
**使用场景**: 孤立引用清理

#### `_drop_ref(cid: str, verify: bool = False)`
**用途**: 内部方法，根据内容ID删除引用
**参数**:
- `cid` - 要删除的内容ID
- `verify` - 是否验证引用未被形状表使用
**使用场景**: 无引用原子对象清理

#### `cleanup_refs()`
**用途**: 清理所有孤立的引用和无引用的原子对象
**实现逻辑**:
1. 识别和删除孤立的历史ID（未被调用使用）
2. 识别和删除无引用的内容ID（未被形状表使用）
**使用场景**: 存储维护、空间回收、定期清理

## 调用接口方法

### 调用存在性和保存

#### `exists_call(hid: str) -> bool`
**用途**: 检查指定历史ID的调用是否存在
**参数**: `hid` - 调用的历史ID
**返回**: 调用是否存在
**使用场景**: 调用查找前的存在性检查

#### `save_call(call: Call)`
**用途**: 保存新调用及其输入输出引用
**参数**: `call` - 要保存的调用对象
**功能**: 保存操作定义、输入输出引用和调用记录
**幂等性**: 已存在的调用不重复保存
**实现逻辑**:
1. 检查调用是否已存在
2. 保存操作定义（如果新操作）
3. 保存所有输入输出引用
4. 保存调用记录

### 调用批量获取

#### `mget_call(hids: List[str], in_memory: bool) -> List[Call]`
**用途**: 批量获取多个调用对象
**参数**:
- `hids` - 调用历史ID列表
- `in_memory` - 是否将引用加载到内存
**返回**: 调用对象列表
**性能优化**: 分别处理缓存命中和数据库查询，减少数据库访问
**实现逻辑**:
1. 按缓存命中情况分组HID
2. 分别从缓存和数据库批量获取
3. 合并结果并构造调用对象

#### `get_call(hid: str, lazy: bool) -> Call`
**用途**: 获取单个调用对象
**参数**:
- `hid` - 调用历史ID
- `lazy` - 是否懒加载引用
**返回**: 调用对象
**实现**: 调用 `mget_call` 获取单个结果

### 调用删除

#### `drop_calls(calls_or_hids, delete_dependents: bool, conn=None)`
**用途**: 删除指定的调用及可选的依赖调用
**参数**:
- `calls_or_hids` - 调用对象或历史ID的可迭代对象
- `delete_dependents` - 是否同时删除依赖调用
- `conn` - 可选的数据库连接
**功能**: 从缓存和持久化存储中删除调用
**事务性**: 使用 `@transaction` 装饰器确保原子性
**实现逻辑**:
1. 统一处理输入格式（调用对象或ID）
2. 可选查找所有依赖调用
3. 分别从缓存和数据库删除
4. 记录删除统计信息

## 来源查询方法

### `get_ref_creator(ref: Ref) -> Optional[Call]`
**用途**: 获取引用的创建者调用
**参数**: `ref` - 目标引用对象
**返回**: 创建者调用或None（如果无创建者）
**限制**: 不支持上下文中调用
**实现**: 调用 `get_creators` 并验证唯一性

### `get_creators(ref_hids: Iterable[str]) -> List[Call]`
**用途**: 批量获取引用的创建者调用
**参数**: `ref_hids` - 引用历史ID的可迭代对象
**返回**: 创建者调用列表
**使用场景**: 数据血缘追踪、依赖分析

### `get_consumers(ref_hids: Iterable[str]) -> List[Call]`
**用途**: 批量获取引用的消费者调用
**参数**: `ref_hids` - 引用历史ID的可迭代对象
**返回**: 消费者调用列表
**使用场景**: 影响分析、下游追踪

### `get_orphans() -> Set[str]`
**用途**: 获取所有孤立引用的历史ID
**返回**: 未被任何调用使用的引用ID集合
**实现**: 计算形状表和调用表的差集
**使用场景**: 存储清理、孤立数据检测

### `get_unreferenced_cids() -> Set[str]`
**用途**: 获取所有无引用的内容ID
**返回**: 未被调用或形状表使用的原子对象ID集合
**使用场景**: 原子对象清理、存储优化

## 数据操作方法

### 对象解包和附加

#### `unwrap(obj: Any, cache: bool = True) -> Any`
**用途**: 递归解包引用对象，返回原始Python对象
**参数**:
- `obj` - 包含引用的对象（可能是嵌套结构）
- `cache` - 是否缓存加载的原子对象
**返回**: 解包后的原始对象
**功能**: 将所有 `Ref` 替换为其包装的实际对象
**使用场景**: 数据提取、函数调用准备、结果获取

#### `attach(obj: T, inplace: bool = False) -> Optional[T]`
**用途**: 将引用对象加载到内存中
**参数**:
- `obj` - 包含引用的对象
- `inplace` - 是否就地修改
**返回**: 加载到内存的对象（如果不是就地修改）
**使用场景**: 内存预加载、性能优化

### 结构体操作

#### `get_struct_builder(tp: Type) -> Op`
**用途**: 获取构建指定类型的内建操作
**参数**: `tp` - 目标类型（ListType 或 DictType）
**返回**: 对应的构建操作（__make_list__ 或 __make_dict__）
**使用场景**: 动态类型构建、类型系统支持

#### `get_struct_inputs(tp: Type, val: Any) -> Dict[str, Any]`
**用途**: 将值转换为结构体构建器的输入格式
**参数**:
- `tp` - 目标类型
- `val` - 要转换的值
**返回**: 构建器输入字典
**实现**:
- **ListType**: 转换为 `{f"elts_{i}": elt}
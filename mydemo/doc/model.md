# Model 模型系统模块

## 概述

Model 模块是 mandala 框架的核心模型系统，定义了计算图的基本组件和数据结构。该模块提供了引用（Ref）、操作（Op）、调用（Call）等核心概念的实现，支持函数的缓存和记忆化，以及复杂数据结构的处理。

## 导入依赖

```python
import textwrap
import functools
from collections import deque
from .common_imports import *
from .common_imports import sess
from typing import Literal
from .tps import *
from .config import *
from .utils import (
    parse_output_name,
    serialize, deserialize, get_content_hash
)
```

## 引用系统

### Ref 基类

```python
class Ref:
    """
    Base class, should not be instantiated directly.
    """
    def __init__(self, cid: str, hid: str, in_memory: bool, obj: Optional[Any]) -> None:
        self.cid = cid
        self.hid = hid
        self.obj = obj
        self.in_memory = in_memory
```

**核心属性:**
- `cid`: 内容ID，基于对象内容的哈希值
- `hid`: 历史ID，基于对象历史和上下文的哈希值
- `obj`: 实际的对象数据
- `in_memory`: 是否在内存中

**核心方法:**

#### with_hid()
```python
def with_hid(self, hid: str) -> "Ref":
    return type(self)(cid=self.cid, hid=hid, in_memory=self.in_memory, obj=self.obj)
```
返回具有新历史ID的引用副本。

#### detached()
```python
def detached(self) -> "Ref":
    """
    Return a *copy* of this ref
    """
    return type(self)(cid=self.cid, hid=self.hid, in_memory=False, obj=None)
```
返回分离的引用副本（不在内存中）。

#### attached()
```python
def attached(self, obj: Any) -> "Ref":
    """
    Return a *copy* of this ref that is in memory (taking the object from
    `obj`)
    """
    return type(self)(cid=self.cid, hid=self.hid, in_memory=True, obj=obj)
```
返回附加到内存中对象的引用副本。

#### shallow_copy()
```python
def shallow_copy(self) -> "Ref":
    return type(self)(
        cid=self.cid, hid=self.hid, in_memory=self.in_memory, obj=self.obj
    )
```
返回浅拷贝的引用。

### AtomRef 类

```python
class AtomRef(Ref):
    def __repr__(self) -> str:
        return "Atom" + super().__repr__()
```

**特点:**
- 表示原子值（基本类型）的引用
- 继承自 Ref 基类
- 专门用于处理不可分解的数据类型

## 特殊值包装器

### _Ignore 类

```python
class _Ignore:
    """
    Used to mark values that should be ignored by the storage, but still
    passed to the function. In this case, the wrapped value `value` will be 
    directly passed to the function.
    """
    def __init__(self, value: Any = None) -> None:
        self.value = value
```

**用途:**
- 标记应被存储忽略但仍传递给函数的值
- 不参与哈希计算和缓存
- 用于处理不影响计算结果的参数

### _NewArgDefault 类

```python
class _NewArgDefault(_Ignore):
    """
    Like `_Ignore`, but should be used as default value when adding new
    arguments to functions to enable backwards compatibility.
    """
    pass
```

**用途:**
- 处理函数签名变化的向后兼容性
- 当参数值等于默认值时自动忽略
- 支持函数演化而不破坏现有缓存

### ValuePointer 类

```python
class ValuePointer:
    """
    Replace an object by a human-readable name from the point of view of the
    storage.
    """
    def __init__(self, id: str, obj: Any):
        if not isinstance(id, str) or not id:
            raise ValueError("The `id` must be a non-empty string.")
        self.id = id
        self.obj = obj
```

**特点:**
- 通过ID标识对象而不是内容
- 不会保存到存储中
- 适用于大型、不可序列化或外部管理的对象

**用途:**
- 机器学习模型的引用
- 大型数据集的引用
- 外部资源的引用

### 辅助函数

```python
def Ignore(value: T = None) -> T:
    return _Ignore(value)

def NewArgDefault(value: T = None) -> T:
    return _NewArgDefault(value)

def unwrap_special_value(obj: ValuePointer | _Ignore | Any) -> Any:
    if isinstance(obj, ValuePointer):
        return obj.obj
    elif isinstance(obj, _Ignore):
        return obj.value
    else:
        return obj
```

## 操作系统

### Op 类

```python
class Op:
    def __init__(
        self,
        name: str,
        f: Callable,
        nout: Union[Literal["var", "auto"], int] = "auto",
        output_names: Optional[List[str]] = None,
        version: Optional[int] = 0,
        ignore_args: Optional[Tuple[str,...]] = None,
        __structural__: bool = False,
        __allow_side_effects__: bool = False,
    ) -> None:
```

**初始化参数:**
- `name`: 操作名称
- `f`: 要包装的函数
- `nout`: 输出数量（"var"、"auto"或具体数字）
- `output_names`: 输出名称列表
- `version`: 操作版本号
- `ignore_args`: 忽略的参数名称
- `__structural__`: 是否为结构化操作
- `__allow_side_effects__`: 是否允许副作用

**核心方法:**

#### get_call_history_id()
```python
def get_call_history_id(self,
                        inputs: Dict[str, Ref],
                        semantic_version: Optional[str] = None,
                        ) -> str:
    """
    Combine the inputs' history IDs, the name of the op, and the semantic
    version to get a unique id for the call history.
    """
    hashable_inputs = self._get_hashable_inputs(inputs)
    obj = ({k: v.hid for k, v in hashable_inputs.items()}, self.name, self.version)
    if semantic_version is not None:
        obj = obj + (semantic_version,)
    return get_content_hash(obj)
```

#### get_call_content_id()
```python
def get_call_content_id(self, inputs: Dict[str, Ref],
                        semantic_version: Optional[str] = None) -> str:
    hashable_inputs = self._get_hashable_inputs(inputs)
    obj = ({k: v.cid for k, v in hashable_inputs.items()}, self.name, self.version)
    if semantic_version is not None:
        obj = obj + (semantic_version,)
    return get_content_hash(obj)
```

#### get_pre_call_id()
```python
def get_pre_call_id(self, inputs: Dict[str, Ref]) -> str:
    """
    Combine the inputs' content IDs and the name of the op to get a unique
    id for the pre-call, to be used to search for matching semantic
    versions.
    """
    hashable_inputs = self._get_hashable_inputs(inputs)
    return get_content_hash((self.name, {k: v.cid for k, v in hashable_inputs.items()}))
```

#### get_output_history_ids()
```python
def get_output_history_ids(
    self, call_history_id: str, output_names: List[str]
) -> Dict[str, str]:
    return {k: get_content_hash((call_history_id, k)) for k in output_names}
```

#### get_ordered_outputs()
```python
def get_ordered_outputs(self, output_dict: Dict[str, Any]) -> Tuple[Any, ...]:
    if (
        self.output_names is None
    ):  # output names must be generic output_0, output_1, etc.
        output_dict_by_int = {
            parse_output_name(name): value for name, value in output_dict.items()
        }
        return tuple([output_dict_by_int[i] for i in range(len(output_dict))])
    else:  # we use the order of the keys in self.output_names
        return tuple([output_dict[k] for k in self.output_names])
```

#### __call__()
```python
def __call__(self, *args, **kwargs) -> Union[Tuple[Ref, ...], Ref]:
    if Context.current_context is None:  # act as noop
        return self.f(*args, **kwargs)
    else:
        storage = Context.current_context.storage
        return storage.call(self, args, kwargs, config={"save_calls": True})
```

### Call 类

```python
class Call:
    def __init__(
        self,
        op: Op,
        cid: str,
        hid: str,
        inputs: Dict[str, Ref],
        outputs: Dict[str, Ref],
        semantic_version: Optional[str] = None,
        content_version: Optional[str] = None,
    ) -> None:
```

**属性:**
- `op`: 关联的操作对象
- `cid`: 调用的内容ID
- `hid`: 调用的历史ID
- `inputs`: 输入参数字典
- `outputs`: 输出结果字典
- `semantic_version`: 语义版本
- `content_version`: 内容版本

**核心方法:**

#### detached()
```python
def detached(self) -> "Call":
    """
    Return the call with the inputs, outputs and op detached.
    """
    return Call(
        op=self.op.detached(),
        cid=self.cid,
        hid=self.hid,
        inputs={k: v.detached() for k, v in self.inputs.items()},
        outputs={k: v.detached() for k, v in self.outputs.items()},
        semantic_version=self.semantic_version,
        content_version=self.content_version,
    )
```

## 包装函数

### wrap_atom()

```python
def wrap_atom(obj: Any, history_id: Optional[str] = None) -> AtomRef:
    """
    Wrap a Python object in an AtomRef. If the object is already a Ref, return
    it unchanged. If `history_id` is not provided, it will be initialized
    from the object's content hash (thereby representing an object without any
    history).
    """
```

**参数:**
- `obj`: 要包装的对象
- `history_id`: 可选的历史ID

**返回值:**
- `AtomRef`: 包装后的原子引用

**处理逻辑:**
1. 如果对象已经是 Ref，直接返回
2. 如果是 ValuePointer，使用其ID创建引用
3. 其他情况创建基于内容哈希的引用

## 集合类型支持

### ListRef 类

```python
class ListRef(Ref):
    def __len__(self) -> int:
        return len(self.obj)

    def __getitem__(self, i: int) -> Ref:
        assert self.in_memory
        return self.obj[i]

    def shape(self) -> "ListRef":
        return ListRef(
            cid=self.cid,
            hid=self.hid,
            in_memory=True,
            obj=[elt.detached() for elt in self.obj],
        )
```

**特点:**
- 支持长度查询和索引访问
- 提供 shape() 方法返回结构信息
- 专门处理列表结构的引用

### DictRef 类

```python
class DictRef(Ref):
    """
    For now, we only support dictionaries where keys are strings.
    """
    def __len__(self) -> int:
        return len(self.obj)
    
    def __getitem__(self, key: str) -> Ref:
        assert self.in_memory
        if isinstance(key, str):
            return self.obj[key]
        elif isinstance(key, Ref):
            assert key.in_memory
            return self.obj[key.obj]
        else:
            raise ValueError(key)
    
    def items(self) -> Iterable[Tuple[str, Ref]]:
        return self.obj.items()
    
    def values(self) -> Iterable[Ref]:
        return self.obj.values()
    
    def shape(self) -> "DictRef":
        return DictRef(
            cid=self.cid,
            hid=self.hid,
            in_memory=True,
            obj={k: v.detached() for k, v in self.obj.items()},
        )
```

**特点:**
- 支持字符串键的字典
- 提供标准字典接口
- 支持键值对遍历

### SetRef 类

```python
class SetRef(Ref):
    def __len__(self) -> int:
        return len(self.obj)

    def __iter__(self):
        return iter(self.obj)

    def __contains__(self, elt: Ref) -> bool:
        return elt in self.obj
```

**特点:**
- 支持集合的基本操作
- 提供迭代和包含检查
- 专门处理集合结构的引用

### 递归处理函数

```python
def recurse_on_ref_collections(f: Callable, obj: Any, **kwargs: Any) -> Any:
    if isinstance(obj, AtomRef):
        return f(obj, **kwargs)
    elif isinstance(obj, (list, ListRef)):
        return [recurse_on_ref_collections(f, elt, **kwargs) for elt in obj]
    elif isinstance(obj, (dict, DictRef)):
        return {k: recurse_on_ref_collections(f, v, **kwargs) for k, v in obj.items()}
    elif isinstance(obj, tuple):
        return tuple(recurse_on_ref_collections(f, elt, **kwargs) for elt in obj)
    elif isinstance(obj, set):
        return {recurse_on_ref_collections(f, elt, **kwargs) for elt in obj}
    elif isinstance(obj, RefCollection):
        return ValueCollection(values=[recurse_on_ref_collections(f, ref, **kwargs) for ref in obj.refs])
    else:
        return obj
```

**功能:**
- 递归地对引用集合应用函数
- 支持列表、字典、元组、集合等结构
- 保持原始数据结构的类型

## 内置结构操作

### 列表操作

```python
def __make_list__(**items: Any) -> MList[Any]:
    # items must be a dict with keys "elts_0", "elts_1", etc.
    elts = [items[f"elts_{i}"] for i in range(len(items))]
    return ListRef(
        cid=get_content_hash([elt.cid for elt in elts]),
        hid=get_content_hash([elt.hid for elt in elts]),
        in_memory=True,
        obj=elts,
    )

def __list_getitem__(list: MList[Any], i: Any) -> Any:
    return list[i.obj]
```

### 字典操作

```python
def __make_dict__(**kwargs: Any) -> dict:
    return DictRef(
        cid=get_content_hash(sorted([(k, v.cid) for k, v in kwargs.items()])),
        hid=get_content_hash(sorted([(k, v.hid) for k, v in kwargs.items()])),
        in_memory=True,
        obj=kwargs,
    )

def __dict_getitem__(dict: MDict[Any, Any], key: Any) -> Any:
    return dict[key]
```

### 集合操作

```python
def __make_set__(**kwargs: Any) -> MSet[Any]:
    elts = [kwargs[f"elts_{i}"] for i in range(len(kwargs))]
    return SetRef(
        cid=get_content_hash(sorted([elt.cid for elt in elts])),
        hid=get_content_hash(sorted([elt.hid for elt in elts])),
        in_memory=True,
        obj=set(elts),
    )
```

### 结构操作符

```python
# 创建结构操作符
__make_list__ = Op(name=__make_list__.__name__, f=__make_list__, __structural__=True, output_names=["list"])
__make_dict__ = Op(name=__make_dict__.__name__, f=__make_dict__, __structural__=True, output_names=["dict"])
__make_set__ = Op(name=__make_set__.__name__, f=__make_set__, __structural__=True, output_names=["set"])
__make_tuple__ = Op(name=__make_tuple__.__name__, f=__make_tuple__, __structural__=True, output_names=["tuple"])
__list_getitem__ = Op(name=__list_getitem__.__name__, f=__list_getitem__, __structural__=True, output_names=["list_item"])
__dict_getitem__ = Op(name=__dict_getitem__.__name__, f=__dict_getitem__, __structural__=True, output_names=["dict_value"])
```

## 装饰器接口

### @op 装饰器

```python
def op(
    output_names: Union[Optional[List[str]], Callable] = None,
    nout: Union[Literal["var", "auto"], int] = "auto",
    ignore_args: Optional[Tuple[str,...]] = None,
    __structural__: bool = False,
    __allow_side_effects__: bool = False,
):
    """
    Decorator used to make a function memoized by the storage.
    """
    def decorator(f: Callable, output_names = None) -> 'f':
        res = Op(
            f.__name__,
            f,
            output_names=output_names,
            nout=nout,
            ignore_args=ignore_args,
            __structural__=__structural__,
            __allow_side_effects__=__allow_side_effects__,
        )
        return functools.wraps(f)(res)

    if callable(output_names):
        return decorator(output_names, None)
    else:
        return lambda f: decorator(f, output_names)
```

**参数说明:**
- `output_names`: 输出名称列表
- `nout`: 输出数量
- `ignore_args`: 要忽略的参数名称
- `__structural__`: 是否为结构化操作
- `__allow_side_effects__`: 是否允许副作用

## 上下文管理

### Context 类

```python
class Context:
    current_context: Optional["Context"] = None
    _profiling_stats: Dict[str, float] = {
        'total_time': 0.0,
        'get_call_time': 0.0,
        'call_exists_time': 0.0,
    }

    def __init__(self, storage: "Storage") -> None:
        self.storage = storage

    def __enter__(self) -> "Storage":
        Context.current_context = self
        return self.storage

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        Context.current_context = None
```

**功能:**
- 管理全局上下文状态
- 提供性能统计功能
- 支持上下文管理器协议

## 集合类型

### RefCollection 类

```python
class RefCollection:
    def __init__(self, refs: Iterable[Ref]):
        self.refs = sorted(refs, key=lambda ref: ref.hid)
    
    def __repr__(self):
        return f"RefCollection({self.refs})"
```

### ValueCollection 类

```python
class ValueCollection:
    def __init__(self, values: List[None]):
        self.values = values
    
    def __repr__(self):
        return f"ValueCollection({self.values})"
```

### CallCollection 类

```python
class CallCollection:
    def __init__(self, calls: Iterable[Call]):
        self.calls = sorted(calls, key=lambda call: call.hid)
    
    def __repr__(self):
        return f"CallCollection({self.calls})"
```

## 使用示例

### 基本操作定义

```python
from mandala1.model import op, Ignore, NewArgDefault

@op
def add_numbers(a: int, b: int) -> int:
    return a + b

@op
def process_data(data: list, config: dict = Ignore({'debug': True})) -> list:
    # config 不参与缓存
    return [x * 2 for x in data]

@op
def enhanced_function(x: int, y: int = NewArgDefault(10)) -> int:
    # 支持函数演化
    return x + y
```

### 复杂数据结构

```python
from mandala1.model import ListRef, DictRef, wrap_atom

# 创建引用
atom_ref = wrap_atom(42)
list_ref = ListRef(
    cid="list_cid",
    hid="list_hid",
    in_memory=True,
    obj=[wrap_atom(1), wrap_atom(2), wrap_atom(3)]
)

dict_ref = DictRef(
    cid="dict_cid",
    hid="dict_hid",
    in_memory=True,
    obj={'key1': wrap_atom('value1'), 'key2': wrap_atom('value2')}
)

# 访问元素
print(f"列表长度: {len(list_ref)}")
print(f"第一个元素: {list_ref[0]}")
print(f"字典值: {dict_ref['key1']}")
```

### 特殊值处理

```python
from mandala1.model import ValuePointer, Ignore, NewArgDefault

# 使用 ValuePointer
large_model = ValuePointer("my_model", actual_model_object)

@op
def train_model(data: list, model: ValuePointer) -> dict:
    # model 通过 ID 引用，不序列化
    return {'accuracy': 0.95}

# 使用 Ignore 参数
@op
def debug_function(data: list, debug_level: int = Ignore(1)) -> list:
    # debug_level 不影响缓存
    if debug_level > 0:
        print(f"Processing {len(data)} items")
    return [x * 2 for x in data]
```

### 上下文使用

```python
from mandala1.imports import Storage
from mandala1.model import Context

storage = Storage()

# 方式1：使用 Storage 的上下文管理
with storage:
    result = add_numbers(1, 2)

# 方式2：直接使用 Context
with Context(storage):
    result = add_numbers(3, 4)

# 方式3：无上下文调用（直接执行）
result = add_numbers(5, 6)  # 直接执行，不缓存
```

## 设计理念

### 引用透明性

- 所有计算都通过引用进行
- 支持内容寻址和历史追踪
- 确保计算的可重现性

### 结构化数据支持

- 原生支持列表、字典、集合、元组
- 递归处理嵌套结构
- 保持数据类型的语义

### 灵活的参数处理

- 支持参数忽略和特殊值
- 处理函数签名演化
- 支持大型对象的引用

## 扩展指南

### 添加新的引用类型

```python
class CustomRef(Ref):
    def __len__(self) -> int:
        return len(self.obj)
    
    def custom_method(self) -> Any:
        return self.obj.custom_operation()
    
    def shape(self) -> "CustomRef":
        return CustomRef(
            cid=self.cid,
            hid=self.hid,
            in_memory=True,
            obj=self.obj.get_shape(),
        )
```

### 创建结构化操作

```python
def __make_custom__(**kwargs: Any) -> CustomType:
    return CustomRef(
        cid=get_content_hash(kwargs),
        hid=get_content_hash(kwargs),
        in_memory=True,
        obj=CustomType(**kwargs),
    )

__make_custom__ = Op(
    name=__make_custom__.__name__, 
    f=__make_custom__, 
    __structural__=True, 
    output_names=["custom"]
)
```

### 自定义装饰器

```python
def custom_op(cache_policy: str = "default"):
    def decorator(f: Callable) -> Op:
        # 自定义缓存策略
        return Op(
            f.__name__,
            f,
            # 根据 cache_policy 设置参数
        )
    return decorator
```

## 注意事项

1. **内存管理**: 注意引用的 `in_memory` 状态
2. **哈希一致性**: 确保内容哈希的一致性
3. **类型兼容**: 使用适当的引用类型
4. **上下文管理**: 正确使用上下文管理器
5. **性能考虑**: 大型对象使用 ValuePointer

## 相关模块

- `storage.py`: 使用模型系统进行数据管理
- `cf.py`: 使用模型系统构建计算图
- `tps.py`: 提供类型系统支持
- `utils.py`: 提供哈希和序列化工具

Model 模块是 mandala 框架的核心，为整个系统提供了基础的数据模型和计算抽象。 
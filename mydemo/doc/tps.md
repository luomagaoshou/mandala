# TPS 类型系统模块

## 概述

TPS（Type System）模块是 mandala 框架的类型系统实现，提供了专门针对计算图和缓存系统优化的类型定义。该模块扩展了 Python 的标准类型系统，支持复杂数据结构的类型推断和转换，是框架类型安全和性能优化的重要基础。

## 导入依赖

```python
from .common_imports import *
import typing
from typing import Hashable, Generic
```

该模块依赖于公共导入模块和 Python 标准的 typing 模块。

## 类型变量定义

### 泛型类型变量

```python
T = TypeVar("T")
_KT = TypeVar("_KT")  # Key Type
_VT = TypeVar("_VT")  # Value Type
```

**说明:**
- `T`: 通用类型变量，用于泛型容器
- `_KT`: 字典键的类型变量
- `_VT`: 字典值的类型变量

## Mandala 集合类型

### MList 类

```python
class MList(List[T], Generic[T]):
    def identify(self):
        return "Type annotation for `mandala` lists"
```

**继承关系:**
- 继承自 `List[T]` 和 `Generic[T]`
- 支持类型参数化的列表

**方法:**
- `identify()`: 返回类型标识字符串

**用途:**
- 为 mandala 框架提供专用的列表类型注解
- 支持计算图中的列表结构表示
- 优化列表操作的缓存和序列化

### MDict 类

```python
class MDict(Dict[_KT, _VT], Generic[_KT, _VT]):
    def identify(self):
        return "Type annotation for `mandala` dictionaries"
```

**继承关系:**
- 继承自 `Dict[_KT, _VT]` 和 `Generic[_KT, _VT]`
- 支持键值类型参数化的字典

**方法:**
- `identify()`: 返回类型标识字符串

**用途:**
- 为 mandala 框架提供专用的字典类型注解
- 支持计算图中的字典结构表示
- 优化字典操作的缓存和序列化

### MSet 类

```python
class MSet(Set[T], Generic[T]):
    def identify(self):
        return "Type annotation for `mandala` sets"
```

**继承关系:**
- 继承自 `Set[T]` 和 `Generic[T]`
- 支持类型参数化的集合

**方法:**
- `identify()`: 返回类型标识字符串

**用途:**
- 为 mandala 框架提供专用的集合类型注解
- 支持计算图中的集合结构表示
- 优化集合操作的缓存和序列化

### MTuple 类

```python
class MTuple(Tuple, Generic[T]):
    def identify(self):
        return "Type annotation for `mandala` tuples"
```

**继承关系:**
- 继承自 `Tuple` 和 `Generic[T]`
- 支持类型参数化的元组

**方法:**
- `identify()`: 返回类型标识字符串

**用途:**
- 为 mandala 框架提供专用的元组类型注解
- 支持计算图中的元组结构表示
- 优化元组操作的缓存和序列化

## 类型系统核心

### Type 基类

```python
class Type:
    @staticmethod
    def from_annotation(annotation: Any) -> "Type":
        # 类型注解转换逻辑
        pass
    
    def __eq__(self, other: Any) -> bool:
        # 类型比较逻辑
        pass
```

**核心方法:**

#### from_annotation() 静态方法

```python
@staticmethod
def from_annotation(annotation: Any) -> "Type":
```

**参数:**
- `annotation`: Python 类型注解

**返回值:**
- `Type`: 对应的 Mandala 类型对象

**转换逻辑:**
1. **None 或空注解**: 返回 `AtomType()`
2. **typing.Any**: 返回 `AtomType()`
3. **泛型类型**: 根据 `__origin__` 属性判断类型
   - `MList`: 返回 `ListType`
   - `MDict`: 返回 `DictType`
   - `MSet`: 返回 `SetType`
   - `MTuple`: 返回 `TupleType`
4. **Type 实例**: 直接返回
5. **其他**: 返回 `AtomType()`

#### __eq__() 方法

```python
def __eq__(self, other: Any) -> bool:
    if type(self) != type(other):
        return False
    elif isinstance(self, AtomType):
        return True
    else:
        raise NotImplementedError
```

**功能:**
- 比较两个类型对象是否相等
- 原子类型之间总是相等
- 其他类型的比较需要子类实现

## 具体类型实现

### AtomType 类

```python
class AtomType(Type):
    def __repr__(self):
        return "AnyType()"
```

**特点:**
- 表示原子类型（基本类型）
- 所有非结构化类型都视为原子类型
- 提供统一的原子类型表示

### ListType 类

```python
class ListType(Type):
    struct_id = "__list__"
    model = list

    def __init__(self, elt: Type):
        self.elt = elt

    def __repr__(self):
        return f"ListType(elt_type={self.elt})"
```

**属性:**
- `struct_id`: 结构标识符，固定为 "__list__"
- `model`: 对应的 Python 类型，为 `list`
- `elt`: 元素类型

**初始化参数:**
- `elt`: 列表元素的类型

### DictType 类

```python
class DictType(Type):
    struct_id = "__dict__"
    model = dict

    def __init__(self, val: Type, key: Type = None):
        self.key = key
        self.val = val

    def __repr__(self):
        return f"DictType(val_type={self.val})"
```

**属性:**
- `struct_id`: 结构标识符，固定为 "__dict__"
- `model`: 对应的 Python 类型，为 `dict`
- `key`: 键类型
- `val`: 值类型

**初始化参数:**
- `val`: 字典值的类型
- `key`: 字典键的类型（可选）

### SetType 类

```python
class SetType(Type):
    struct_id = "__set__"
    model = set

    def __init__(self, elt: Type):
        self.elt = elt

    def __repr__(self):
        return f"SetType(elt_type={self.elt})"
```

**属性:**
- `struct_id`: 结构标识符，固定为 "__set__"
- `model`: 对应的 Python 类型，为 `set`
- `elt`: 元素类型

**初始化参数:**
- `elt`: 集合元素的类型

### TupleType 类

```python
class TupleType(Type):
    struct_id = "__tuple__"
    model = tuple

    def __init__(self, *elt_types: Type):
        self.elt_types = elt_types

    def __repr__(self):
        return f"TupleType(elt_types={self.elt_types})"
```

**属性:**
- `struct_id`: 结构标识符，固定为 "__tuple__"
- `model`: 对应的 Python 类型，为 `tuple`
- `elt_types`: 元素类型的元组

**初始化参数:**
- `*elt_types`: 元组中各个位置的元素类型

## 使用示例

### 基本类型注解

```python
from mandala1.tps import MList, MDict, MSet, MTuple

# 列表类型注解
def process_numbers(numbers: MList[int]) -> MList[float]:
    return [x * 1.5 for x in numbers]

# 字典类型注解
def process_mapping(data: MDict[str, int]) -> MDict[str, float]:
    return {k: v * 2.0 for k, v in data.items()}

# 集合类型注解
def unique_elements(items: MList[str]) -> MSet[str]:
    return set(items)

# 元组类型注解
def create_point(x: float, y: float) -> MTuple[float, float]:
    return (x, y)
```

### 类型转换和检查

```python
from mandala1.tps import Type, AtomType, ListType, DictType

# 从类型注解创建类型对象
list_type = Type.from_annotation(MList[int])
dict_type = Type.from_annotation(MDict[str, float])
atom_type = Type.from_annotation(int)

print(f"列表类型: {list_type}")  # ListType(elt_type=AnyType())
print(f"字典类型: {dict_type}")  # DictType(val_type=AnyType())
print(f"原子类型: {atom_type}")  # AnyType()

# 类型比较
another_list_type = Type.from_annotation(MList[str])
print(f"类型相等: {list_type == another_list_type}")  # 需要实现比较逻辑

# 检查类型特性
if isinstance(list_type, ListType):
    print(f"元素类型: {list_type.elt}")
    print(f"结构标识: {list_type.struct_id}")
    print(f"模型类型: {list_type.model}")
```

### 复杂类型结构

```python
from mandala1.tps import MList, MDict, MTuple

# 嵌套类型
nested_list_type = Type.from_annotation(MList[MList[int]])
nested_dict_type = Type.from_annotation(MDict[str, MList[float]])
complex_tuple_type = Type.from_annotation(MTuple[str, MList[int], MDict[str, float]])

print(f"嵌套列表类型: {nested_list_type}")
print(f"嵌套字典类型: {nested_dict_type}")
print(f"复杂元组类型: {complex_tuple_type}")
```

### 在函数装饰器中使用

```python
from mandala1.imports import op
from mandala1.tps import MList, MDict

@op
def data_analysis(
    raw_data: MList[MDict[str, float]],
    config: MDict[str, int]
) -> MDict[str, float]:
    """
    数据分析函数，使用 mandala 类型系统
    """
    results = {}
    for item in raw_data:
        for key, value in item.items():
            if key in results:
                results[key] += value
            else:
                results[key] = value
    
    # 应用配置
    multiplier = config.get('multiplier', 1)
    return {k: v * multiplier for k, v in results.items()}

# 使用函数
from mandala1.imports import Storage

storage = Storage()
with storage:
    data = [
        {'A': 1.0, 'B': 2.0},
        {'A': 3.0, 'C': 4.0}
    ]
    config = {'multiplier': 2}
    result = data_analysis(data, config)
    print(f"分析结果: {storage.unwrap(result)}")
```

## 设计理念

### 类型安全

- 提供编译时类型检查
- 支持泛型类型参数
- 确保类型一致性

### 性能优化

- 专为计算图优化的类型系统
- 支持高效的序列化和缓存
- 减少类型转换开销

### 扩展性

- 易于添加新的类型支持
- 支持复杂的嵌套类型结构
- 兼容 Python 标准类型系统

## 扩展指南

### 添加新的集合类型

```python
class MCustomType(CustomType[T], Generic[T]):
    def identify(self):
        return "Type annotation for `mandala` custom types"

class CustomType(Type):
    struct_id = "__custom__"
    model = custom_type
    
    def __init__(self, elt: Type):
        self.elt = elt
    
    def __repr__(self):
        return f"CustomType(elt_type={self.elt})"
```

### 扩展类型转换逻辑

```python
# 在 Type.from_annotation 中添加新的转换逻辑
elif annotation.__origin__ is MCustomType:
    elt_annotation = annotation.__args__[0]
    return CustomType(elt=Type.from_annotation(annotation=elt_annotation))
```

### 实现类型比较

```python
def __eq__(self, other: Any) -> bool:
    if type(self) != type(other):
        return False
    elif isinstance(self, AtomType):
        return True
    elif isinstance(self, ListType):
        return self.elt == other.elt
    elif isinstance(self, DictType):
        return self.key == other.key and self.val == other.val
    # ... 其他类型的比较逻辑
```

## 注意事项

1. **类型注解一致性**: 确保使用 mandala 类型注解而不是标准 Python 类型
2. **性能考虑**: 复杂的嵌套类型可能影响性能
3. **序列化支持**: 自定义类型需要考虑序列化和反序列化
4. **版本兼容**: 类型系统变更需要考虑向后兼容性
5. **错误处理**: 类型转换失败时的错误处理

## 相关模块

- `model.py`: 使用类型系统进行参数类型检查
- `storage.py`: 使用类型系统进行数据序列化
- `common_imports.py`: 提供基础的类型提示支持
- `imports.py`: 导出类型系统的公共接口

TPS 模块是 mandala 框架类型系统的核心，为整个框架提供了类型安全和性能优化的基础设施。 
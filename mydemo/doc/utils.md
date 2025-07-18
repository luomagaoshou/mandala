# Utils 工具模块

## 概述

Utils 模块提供了 mandala 框架中使用的各种工具函数，包括数据序列化、哈希计算、集合操作、图算法、类型检查等功能。该模块是框架的基础设施，为其他模块提供了必要的支持功能。

## 导入依赖

```python
from .common_imports import *
import joblib
import io
import inspect
from inspect import Parameter
import sqlite3
from .config import *
from abc import ABC, abstractmethod
from typing import Hashable, TypeVar
if Config.has_prettytable:
    import prettytable
```

## 数据展示工具

### dataframe_to_prettytable()

```python
def dataframe_to_prettytable(df: pd.DataFrame) -> str:
    if not Config.has_prettytable:
        logger.info(
            "Install the 'prettytable' package to get prettier tables in the console."
        )
        return df.to_string()
    # Initialize a PrettyTable object
    table = prettytable.PrettyTable()
    
    # Set the column names
    table.field_names = df.columns.tolist()
    
    # Add rows to the table
    for row in df.itertuples(index=False):
        table.add_row(row)
    
    # Return the pretty-printed table as a string
    return table.get_string()
```

**参数:**
- `df`: 要格式化的 pandas DataFrame

**返回值:**
- `str`: 格式化后的表格字符串

**功能:**
- 将 DataFrame 转换为美观的表格格式
- 自动检测 prettytable 可用性
- 不可用时回退到 pandas 默认格式

## 序列化工具

### serialize()

```python
def serialize(obj: Any) -> bytes:
    """
    ! this may lead to different serializations for objects x, y such that x
    ! == y in Python. This is because of things like set ordering, which is not
    ! determined by the contents of the set. For example, {1, 2} and {2, 1} would
    ! `serialize()` to different things, but they would be equal in Python.
    """
    buffer = io.BytesIO()
    joblib.dump(obj, buffer)
    return buffer.getvalue()
```

**参数:**
- `obj`: 要序列化的对象

**返回值:**
- `bytes`: 序列化后的字节数据

**注意事项:**
- 可能对等价对象产生不同的序列化结果
- 主要是由于集合等无序数据结构的内部顺序不确定

### deserialize()

```python
def deserialize(value: bytes) -> Any:
    buffer = io.BytesIO(value)
    return joblib.load(buffer)
```

**参数:**
- `value`: 要反序列化的字节数据

**返回值:**
- `Any`: 反序列化后的对象

## 相等性检查

### _conservative_equality_check()

```python
def _conservative_equality_check(safe_value: Any, unknown_value: Any) -> bool:
    """
    An equality checker that treats `safe_value` as a "simple" type, but is 
    conservative about how __eq__ can be applied to `unknown_value`. This is
    necessary when comparing against e.g. numpy arrays.
    """
    if type(safe_value) != type(unknown_value):
        return False
    if isinstance(unknown_value, (int, float, str, bytes, bool, type(None))):
        return safe_value == unknown_value
    # handle some common cases
    if isinstance(unknown_value, np.ndarray):
        return np.array_equal(safe_value, unknown_value)
    elif isinstance(unknown_value, pd.DataFrame):
        return safe_value.equals(unknown_value)
    else:
        # fall back to the default equality check
        return safe_value == unknown_value
```

**参数:**
- `safe_value`: 已知为简单类型的值
- `unknown_value`: 需要谨慎处理的值

**返回值:**
- `bool`: 是否相等

**功能:**
- 安全的相等性检查
- 特别处理 numpy 数组和 pandas DataFrame
- 避免复杂类型的 __eq__ 方法问题

## 哈希工具

### get_content_hash()

```python
def get_content_hash(obj: Any) -> str:
    if hasattr(obj, "__get_mandala_dict__"):
        obj = obj.__get_mandala_dict__()
    if Config.has_torch:
        # TODO: ideally, should add a label to distinguish this from a numpy
        # array with the same contents!
        obj = tensor_to_numpy(obj) 
    if isinstance(obj, pd.DataFrame):
        # DataFrames cause collisions for joblib hashing for some reason
        # TODO: the below may be incomplete
        obj = {
            "columns": obj.columns,
            "values": obj.values,
            "index": obj.index,
        }
    result = joblib.hash(obj)  # this hash is canonical wrt python collections
    if result is None:
        raise RuntimeError("joblib.hash returned None")
    return result
```

**参数:**
- `obj`: 要计算哈希的对象

**返回值:**
- `str`: 内容哈希值

**功能:**
- 生成对象的内容哈希
- 处理特殊类型（PyTorch 张量、DataFrame）
- 支持自定义哈希接口

## 输出名称工具

### dump_output_name()

```python
def dump_output_name(index: int, output_names: Optional[List[str]] = None) -> str:
    if output_names is not None and index < len(output_names):
        return output_names[index]
    else:
        return f"output_{index}"
```

**参数:**
- `index`: 输出索引
- `output_names`: 可选的输出名称列表

**返回值:**
- `str`: 输出名称

### parse_output_name()

```python
def parse_output_name(name: str) -> int:
    return int(name.split("_")[-1])
```

**参数:**
- `name`: 输出名称字符串

**返回值:**
- `int`: 解析出的索引

## 集合操作工具

### get_setdict_union()

```python
def get_setdict_union(
    a: Dict[str, Set[str]], b: Dict[str, Set[str]]
) -> Dict[str, Set[str]]:
    return {k: a.get(k, set()) | b.get(k, set()) for k in a.keys() | b.keys()}
```

**功能:** 计算两个集合字典的并集

### get_setdict_intersection()

```python
def get_setdict_intersection(
    a: Dict[str, Set[str]], b: Dict[str, Set[str]]
) -> Dict[str, Set[str]]:
    return {k: a[k] & b[k] for k in a.keys() & b.keys()}
```

**功能:** 计算两个集合字典的交集

### get_dict_union_over_keys()

```python
def get_dict_union_over_keys(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    return {k: a[k] if k in a else b[k] for k in a.keys() | b.keys()}
```

**功能:** 计算两个字典在键上的并集

### get_dict_intersection_over_keys()

```python
def get_dict_intersection_over_keys(
    a: Dict[str, Any], b: Dict[str, Any]
) -> Dict[str, Any]:
    return {k: a[k] for k in a.keys() & b.keys()}
```

**功能:** 计算两个字典在键上的交集

### get_adjacency_union()

```python
def get_adjacency_union(
    a: Dict[str, Dict[str, Set[str]]], b: Dict[str, Dict[str, Set[str]]]
) -> Dict[str, Dict[str, Set[str]]]:
    return {
        k: get_setdict_union(a.get(k, {}), b.get(k, {})) for k in a.keys() | b.keys()
    }
```

**功能:** 计算两个邻接表的并集

### get_adjacency_intersection()

```python
def get_adjacency_intersection(
    a: Dict[str, Dict[str, Set[str]]], b: Dict[str, Dict[str, Set[str]]]
) -> Dict[str, Dict[str, Set[str]]]:
    return {k: get_setdict_intersection(a[k], b[k]) for k in a.keys() & b.keys()}
```

**功能:** 计算两个邻接表的交集

### get_nullable_union()

```python
def get_nullable_union(*sets: Set[str]) -> Set[str]:
    return set.union(*sets) if len(sets) > 0 else set()
```

**功能:** 安全的集合并集操作（处理空集合）

### get_nullable_intersection()

```python
def get_nullable_intersection(*sets: Set[str]) -> Set[str]:
    return set.intersection(*sets) if len(sets) > 0 else set()
```

**功能:** 安全的集合交集操作（处理空集合）

## 图操作工具

### get_adj_from_edges()

```python
def get_adj_from_edges(
    edges: Set[Tuple[str, str, str]], node_support: Optional[Set[str]] = None
) -> Tuple[Dict[str, Dict[str, Set[str]]], Dict[str, Dict[str, Set[str]]]]:
    """
    Given edges, convert them into the adjacency representation used by the
    `ComputationFrame` class.
    """
    out = {}
    inp = {}
    for src, dst, label in edges:
        if src not in out:
            out[src] = {}
        if label not in out[src]:
            out[src][label] = set()
        out[src][label].add(dst)
        if dst not in inp:
            inp[dst] = {}
        if label not in inp[dst]:
            inp[dst][label] = set()
        inp[dst][label].add(src)
    if node_support is not None:
        for node in node_support:
            if node not in out:
                out[node] = {}
            if node not in inp:
                inp[node] = {}
    return out, inp
```

**参数:**
- `edges`: 边的集合（源节点、目标节点、标签）
- `node_support`: 可选的节点支持集合

**返回值:**
- `Tuple`: 输出邻接表和输入邻接表

## 参数处理工具

### boundargs_to_args_kwargs()

```python
def boundargs_to_args_kwargs(bound_args: inspect.BoundArguments) -> Tuple[Tuple[Any,...], Dict[str, Any]]:
    """
    Convert a BoundArguments object into a tuple of args and a dict of kwargs.
    """
    args_list = []
    kwargs_dict = {}

    for param_name, param in bound_args.signature.parameters.items():
        kind = param.kind
        value = bound_args.arguments[param_name]

        if kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD):
            args_list.append(value)
        elif kind == Parameter.VAR_POSITIONAL:
            args_list.extend(value)
        elif kind == Parameter.KEYWORD_ONLY:
            kwargs_dict[param_name] = value
        elif kind == Parameter.VAR_KEYWORD:
            kwargs_dict.update(value)

    return tuple(args_list), kwargs_dict
```

**参数:**
- `bound_args`: 绑定的参数对象

**返回值:**
- `Tuple`: 位置参数元组和关键字参数字典

### parse_returns()

```python
def parse_returns(
    sig: inspect.Signature,
    returns: Any,
    nout: Union[Literal["auto", "var"], int],
    output_names: Optional[List[str]] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Return two dicts based on the returns:
    - {output name: output value}
    - {output name: output type annotation}, where things like `Tuple[T, ...]` are expanded.
    """
```

**参数:**
- `sig`: 函数签名
- `returns`: 返回值
- `nout`: 输出数量（"auto"、"var"或整数）
- `output_names`: 可选的输出名称列表

**返回值:**
- `Tuple`: 输出字典和类型注解字典

**功能:**
- 解析函数返回值
- 处理多返回值情况
- 提取类型注解信息

## 装饰器工具

### unwrap_decorators()

```python
def unwrap_decorators(
    obj: Callable, strict: bool = True
) -> Union[types.FunctionType, types.MethodType]:
    while hasattr(obj, "__wrapped__"):
        obj = obj.__wrapped__
    if not isinstance(obj, (types.FunctionType, types.MethodType)):
        msg = f"Expected a function or method, but got {type(obj)}"
        if strict:
            raise RuntimeError(msg)
        else:
            logger.debug(msg)
    return obj
```

**参数:**
- `obj`: 被装饰的可调用对象
- `strict`: 是否严格模式

**返回值:**
- `Union[types.FunctionType, types.MethodType]`: 原始函数或方法

**功能:**
- 解除装饰器包装
- 获取原始函数对象
- 支持严格和非严格模式

## 字典工具

### is_subdict()

```python
def is_subdict(a: Dict, b: Dict) -> bool:
    """
    Check that all keys in `a` are in `b` with the same value.
    """
    return all((k in b and a[k] == b[k]) for k in a)
```

**功能:** 检查字典 a 是否为字典 b 的子字典

### invert_dict()

```python
def invert_dict(d: Dict[_KT, _VT]) -> Dict[_VT, List[_KT]]:
    """
    Invert a dictionary
    """
    out = {}
    for k, v in d.items():
        if v not in out:
            out[v] = []
        out[v].append(k)
    return out
```

**功能:** 反转字典，值成为键，键成为值的列表

## 图算法

### 强连通分量算法

#### find_strongly_connected_components()

```python
def find_strongly_connected_components(graph: Dict[str, Set[str]]) -> Tuple[Tuple[str,...],...]:
    """
    Find the strongly connected components of a directed graph using Tarjan's
    algorithm. The graph is represented as a dictionary mapping nodes to lists
    of their neighbors.
    """
```

**参数:**
- `graph`: 图的邻接表表示

**返回值:**
- `Tuple[Tuple[str,...],...]`: 强连通分量的元组

**功能:**
- 使用 Tarjan 算法查找强连通分量
- 结果是确定性的（排序后的）
- 处理有向图的循环结构

#### create_super_graph()

```python
def create_super_graph(graph: Dict[str, Set[str]], 
                       sccs: Tuple[Tuple[str,...],...]
                       ) -> Dict[str, Set[int]]:
    """
    Given the original graph and the strongly connected components, create a
    supergraph where each node is an SCC and there is an edge from SCC A to SCC
    B if there is an edge from a node in A to a node in B in the original graph.
    """
```

**参数:**
- `graph`: 原始图
- `sccs`: 强连通分量

**返回值:**
- `Dict[str, Set[int]]`: 超图表示

**功能:**
- 创建强连通分量的超图
- 每个 SCC 成为超图中的一个节点
- 保持 SCC 之间的连接关系

### 拓扑排序

#### topological_sort()

```python
def topological_sort(graph: Dict[T, Set[T]]) -> List[T]:
    """
    Topological sort of a directed acyclic graph using depth-first search.
    """
```

**参数:**
- `graph`: 有向无环图

**返回值:**
- `List[T]`: 拓扑排序后的节点列表

**功能:**
- 使用深度优先搜索进行拓扑排序
- 要求输入图是有向无环图
- 结果是确定性的

#### almost_topological_sort()

```python
def almost_topological_sort(graph: Dict[str, Set[str]]) -> List[str]:
    """
    An almost-topological sort of a directed graph:
    - between SCCs, the order is topological
    - within an SCC, the order is arbitrary
    """
```

**参数:**
- `graph`: 有向图（可能有环）

**返回值:**
- `List[str]`: 几乎拓扑排序的节点列表

**功能:**
- 处理有环图的拓扑排序
- SCC 之间保持拓扑顺序
- SCC 内部顺序任意

### 路径查找

#### get_edges_in_paths()

```python
def get_edges_in_paths(
        graph: Dict[str, Set[str]],
        start: str,
        end: str) -> Set[Tuple[str, str]]:
    """
    Find all edges belonging to some *simple* path from A to B in a directed
    graph that may contain cycles. 
    """
```

**参数:**
- `graph`: 有向图
- `start`: 起始节点
- `end`: 终止节点

**返回值:**
- `Set[Tuple[str, str]]`: 路径上的边集合

**功能:**
- 查找所有简单路径上的边
- 处理有环图
- 返回路径上的所有边

## 用户交互工具

### ask_user()

```python
def ask_user(question: str, valid_options: List[str]) -> str:
    """
    Ask the user a question and return their response.
    """
    prompt = f"{question} "
    while True:
        print(prompt)
        response = input().strip().lower()
        if response in valid_options:
            return response
        else:
            print(f"Invalid response: {response}")
```

**参数:**
- `question`: 问题文本
- `valid_options`: 有效选项列表

**返回值:**
- `str`: 用户选择的选项

**功能:**
- 交互式用户输入
- 验证输入的有效性
- 循环直到获得有效输入

### mock_input()

```python
def mock_input(prompts):
    ### simulate user input non-interactively
    it = iter(prompts)
    def mock_input_func(*args):
        return next(it)
    return mock_input_func
```

**参数:**
- `prompts`: 预设的输入响应

**返回值:**
- `Callable`: 模拟输入函数

**功能:**
- 非交互式输入模拟
- 用于测试和自动化
- 按顺序返回预设响应

## 使用示例

### 基本序列化操作

```python
from mandala1.utils import serialize, deserialize, get_content_hash

# 序列化和反序列化
data = {'key': 'value', 'numbers': [1, 2, 3]}
serialized = serialize(data)
deserialized = deserialize(serialized)

# 计算内容哈希
hash_value = get_content_hash(data)
print(f"数据哈希: {hash_value}")

# 相等性检查
import numpy as np
array1 = np.array([1, 2, 3])
array2 = np.array([1, 2, 3])
is_equal = _conservative_equality_check(array1, array2)
print(f"数组相等: {is_equal}")
```

### 集合操作

```python
from mandala1.utils import get_setdict_union, get_setdict_intersection

# 集合字典操作
dict_a = {'x': {'a', 'b'}, 'y': {'c', 'd'}}
dict_b = {'x': {'b', 'c'}, 'z': {'e', 'f'}}

union_result = get_setdict_union(dict_a, dict_b)
intersection_result = get_setdict_intersection(dict_a, dict_b)

print(f"并集: {union_result}")
print(f"交集: {intersection_result}")
```

### 图算法应用

```python
from mandala1.utils import find_strongly_connected_components, topological_sort

# 强连通分量
graph = {
    'A': {'B'},
    'B': {'C'},
    'C': {'A', 'D'},
    'D': {'E'},
    'E': set()
}

sccs = find_strongly_connected_components(graph)
print(f"强连通分量: {sccs}")

# 拓扑排序（有向无环图）
dag = {
    'A': {'B', 'C'},
    'B': {'D'},
    'C': {'D'},
    'D': set()
}

topo_order = topological_sort(dag)
print(f"拓扑排序: {topo_order}")
```

### 函数参数处理

```python
from mandala1.utils import parse_returns, boundargs_to_args_kwargs
import inspect

def example_function(a: int, b: str, c: float = 1.0) -> tuple[int, str]:
    return a * 2, b.upper()

# 解析返回值
sig = inspect.signature(example_function)
returns = (10, "HELLO")
outputs_dict, annotations_dict = parse_returns(sig, returns, nout="auto")

print(f"输出字典: {outputs_dict}")
print(f"注解字典: {annotations_dict}")

# 参数绑定处理
bound_args = sig.bind(5, "world", c=2.0)
args, kwargs = boundargs_to_args_kwargs(bound_args)
print(f"位置参数: {args}")
print(f"关键字参数: {kwargs}")
```

### 用户交互

```python
from mandala1.utils import ask_user, mock_input

# 交互式输入
choice = ask_user("选择操作类型:", ["create", "update", "delete"])
print(f"用户选择: {choice}")

# 模拟输入（用于测试）
mock_func = mock_input(["create", "yes", "no"])
# 现在可以用 mock_func 代替 input
```

## 设计理念

### 功能模块化

- 每个函数专注于单一功能
- 函数之间保持独立性
- 易于测试和维护

### 类型安全

- 提供完整的类型注解
- 支持泛型类型参数
- 运行时类型检查

### 性能优化

- 使用高效的算法实现
- 避免不必要的计算
- 支持大规模数据处理

## 扩展指南

### 添加新的序列化格式

```python
def serialize_json(obj: Any) -> str:
    """JSON 序列化"""
    import json
    return json.dumps(obj, default=str)

def deserialize_json(value: str) -> Any:
    """JSON 反序列化"""
    import json
    return json.loads(value)
```

### 添加新的图算法

```python
def shortest_path(graph: Dict[str, Set[str]], start: str, end: str) -> List[str]:
    """最短路径算法"""
    from collections import deque
    
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        node, path = queue.popleft()
        if node == end:
            return path
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return []
```

### 添加新的数据处理工具

```python
def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """深度合并字典"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result
```

## 注意事项

1. **序列化兼容性**: 注意不同版本间的序列化兼容性
2. **哈希一致性**: 确保哈希函数的一致性和稳定性
3. **性能考虑**: 大数据量时注意内存使用
4. **类型检查**: 使用适当的类型检查方法
5. **错误处理**: 对异常情况进行适当处理

## 相关模块

- `common_imports.py`: 提供基础导入和类型支持
- `config.py`: 提供配置信息和可选依赖检测
- `model.py`: 使用工具函数进行数据处理
- `storage.py`: 使用序列化和哈希功能
- `cf.py`: 使用图算法和集合操作

Utils 模块是 mandala 框架的工具库，为整个系统提供了基础的功能支持。 
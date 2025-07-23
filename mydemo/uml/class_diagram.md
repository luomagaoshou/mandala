# Mandala框架核心类图

## 1. 核心存储和计算框架类图

```mermaid
classDiagram
    class Storage {
        -db_path: str
        -call_storage: CallStorage
        -ref_storage: RefStorage
        -cache: Dict
        +__init__(db_path: str)
        +attach(refs: List[Ref])
        +unwrap(obj: Any) Any
        +cf(result: Any) ComputationFrame
        +mget_call(hids: List[str]) List[Call]
        +drop_calls(calls_or_hids: Any, delete_dependents: bool)
        +cache_info()
        +clear_cache()
    }

    class ComputationFrame {
        -storage: Storage
        -inp: Dict[str, Dict[str, Set[str]]]
        -out: Dict[str, Dict[str, Set[str]]]
        -vs: Dict[str, Set[str]]
        -fs: Dict[str, Set[str]]
        -refinv: Dict[str, Set[str]]
        -callinv: Dict[str, Set[str]]
        -creator: Dict[str, str]
        -consumers: Dict[str, Set[str]]
        -refs: Dict[str, Ref]
        -calls: Dict[str, Call]
        +__init__(storage: Storage, ...)
        +vnames() Set[str]
        +fnames() Set[str]
        +nodes() Set[str]
        +edges() List[Tuple[str, str, str]]
        +expand_back(recursive: bool) ComputationFrame
        +expand_forward(recursive: bool) ComputationFrame
        +expand_all() ComputationFrame
        +drop_node(node: str) ComputationFrame
        +drop_var(vname: str) ComputationFrame
        +drop_func(fname: str) ComputationFrame
        +rename_var(vname: str, new_vname: str) ComputationFrame
        +merge_into(node_to_merge: str, merge_into: str) ComputationFrame
        +merge_vars() ComputationFrame
        +cleanup() ComputationFrame
        +df(*nodes: str) DataFrame
        +eval(*nodes: str) DataFrame
        +draw(path: str, orientation: str)
        +__or__(other: ComputationFrame) ComputationFrame
        +__and__(other: ComputationFrame) ComputationFrame
        +__sub__(other: ComputationFrame) ComputationFrame
    }

    class Ref {
        +hid: str
        +cid: str
        +__init__(hid: str, cid: str)
    }

    class Call {
        +hid: str
        +op: Op
        +inputs: Dict[str, Ref]
        +outputs: Dict[str, Ref]
        +__init__(hid: str, op: Op, inputs: Dict, outputs: Dict)
    }

    class Op {
        +name: str
        +func: Callable
        +output_names: List[str]
        +__init__(name: str, func: Callable, output_names: List[str])
        +__call__(*args, **kwargs) Any
    }

    Storage ||--o{ ComputationFrame : creates
    ComputationFrame ||--o{ Ref : contains
    ComputationFrame ||--o{ Call : contains
    Call ||--o{ Op : uses
    Call ||--o{ Ref : inputs/outputs
```

## 2. 栈回放系统类图

```mermaid
classDiagram
    class StackReplayDemo {
        -storage: Storage
        -原始结果: Any
        -原始cf: ComputationFrame
        +__init__(storage_path: str)
        +创建计算历史() None
        +查找目标函数(函数名: str) List[Call]
        +修改参数重新执行(原始调用: Call, 新参数: Dict) Any
        +替换节点生成新CF(新结果: Any) ComputationFrame
        +合并ComputationFrame(原始cf: ComputationFrame, 新cf: ComputationFrame) ComputationFrame
        +可视化结果(cf: ComputationFrame, 文件名: str) None
        +分析结果(原始结果: Any, 新结果: Any) None
        +运行完整演示() None
    }

    class 数据处理 {
        <<function>>
        +数据处理(数据: List[int], 乘数: int) List[int]
    }

    class 批量计算 {
        <<function>>
        +批量计算(输入列表: List[List[int]], 处理参数: int) Dict[str, Any]
    }

    StackReplayDemo --> Storage : uses
    StackReplayDemo --> ComputationFrame : manipulates
    数据处理 --> Op : decorated_by
    批量计算 --> Op : decorated_by
    批量计算 --> 数据处理 : calls
```

## 3. 工具函数和辅助类图

```mermaid
classDiagram
    class RefCollection {
        +refs: Tuple[Ref, ...]
        +__init__(refs: Tuple[Ref, ...])
        +hid: str
    }

    class CallCollection {
        +calls: Tuple[Call, ...]
        +__init__(calls: Tuple[Call, ...])
        +hid: str
    }

    class get_name_proj {
        <<function>>
        +get_name_proj(op: Op) Callable[[str], str]
    }

    class get_reverse_proj {
        <<function>>
        +get_reverse_proj(call: Call) Callable[[str], Set[str]]
    }

    RefCollection ||--o{ Ref : contains
    CallCollection ||--o{ Call : contains
    ComputationFrame --> RefCollection : creates
    ComputationFrame --> CallCollection : creates
    ComputationFrame --> get_name_proj : uses
    ComputationFrame --> get_reverse_proj : uses
```

## 4. 存储层类图

```mermaid
classDiagram
    class CallStorage {
        +execute_df(query: str) DataFrame
        +store_call(call: Call)
        +get_call(hid: str) Call
    }

    class RefStorage {
        +store_ref(ref: Ref)
        +get_ref(hid: str) Ref
    }

    Storage --> CallStorage : uses
    Storage --> RefStorage : uses
    CallStorage --> Call : stores
    RefStorage --> Ref : stores
```
# `@op` vs `@track`: 深度原理与实现解析

本文档结合 `op_vs_track_example.py` 示例，从 `mandala` 源代码层面深入剖析 `@op` 和 `@track` 装饰器的核心工作原理、实现差异以及协作模式。

## 一、核心概念：两种不同的"承诺"

可以将这两个装饰器理解为向 `mandala` 系统做出的两种完全不同的承诺：

-   **`@op` (Operation - 操作)**:
    -   **承诺**: "这个函数是一个独立的、可重复的 **计算单元**。请 **记住** 它的每次调用（输入、代码版本、依赖版本）和对应的 **输出**。如果将来遇到完全相同的调用，请不要重新计算，直接告诉我结果。"
    -   **结果**: 函数的返回值被 `mandala` 拦截，替换为一个指向数据库记录的 **`Ref`（引用）对象**。函数体只有在缓存未命中时才执行。

-   **`@track` (Tracked Dependency - 被追踪的依赖)**:
    -   **承诺**: "我本身只是一个普通的函数，你 **不需要记住我的输出**。但是，我的 **实现逻辑** 很重要，很多 `@op` 函数都依赖我。请你 **追踪我的代码**，如果我的代码变了，请务必通知那些依赖我的 `@op` 函数，告诉它们缓存已失效。"
    -   **结果**: 函数返回的是 **原始值 (raw value)**，而非 `Ref` 对象。函数体 **每次调用都会执行**。它的核心价值在于为其他 `@op` 函数提供一个可追踪的版本指纹。

## 二、源代码层面的实现原理

### 1. `@track` 的实现: "依赖注册处"

`@track` 的源代码位于 `mandala1/deps/tracers/dec_impl.py`，其核心逻辑极为轻量：

```python
# from mandala1/deps/tracers/dec_impl.py
def track(obj: Union[types.FunctionType, type]) -> "obj":
    # ...
    elif isinstance(obj, types.FunctionType):
        # 1. 为函数创建一个追踪器，它会分析函数源码、AST等
        tracer = DecTracer(func=obj)
        # 2. 【核心】将追踪器注册到全局的状态管理器中
        TracerState.add_tracer(tracer)
        # 3. 返回未经任何包装的原始函数
        return obj
```

**工作流程**:
1.  当你用 `@track` 装饰 `get_config_value` 时，`mandala` 为它创建了一个 `DecTracer` 对象，该对象持有函数的元信息，最重要的是它的 **源代码内容**。
2.  `TracerState.add_tracer(tracer)` 将这个追踪器"登记"在一个全局的"依赖注册处"(`TracerState`)。
3.  装饰器返回 **原始的 `get_config_value` 函数**。这就是为什么调用它时行为和普通函数完全一样。

`@track` 本身不改变函数的行为，它只做一件事：**在系统中挂一个号，让别人能查到它**。

### 2. `@op` 的实现: "版本化缓存守卫"

`@op` 的实现位于 `mandala1/storage.py`，它要复杂得多，因为它扮演着缓存和版本检查的"守卫"角色。其调用过程的伪代码如下：

```python
# from mandala1/storage.py - 逻辑伪代码
class Op:
    def __call__(self, *args, **kwargs):
        # 当 @op 函数被调用时，此方法被触发
        # 它不直接执行函数体，而是请求 Storage 来处理调用
        return self.storage.call_op(self, bound_args)

class Storage:
    def call_op(self, op: Op, bound_args) -> "Ref":
        # 1. 计算当前调用的"版本密钥" (Version Key)
        #    - 获取 @op 函数自身的代码哈希
        op_version = op.versioner.get_op_version() 
        #    - 深入 @op 函数的AST，查找所有调用的函数
        #    - 去"依赖注册处"(TracerState)查询这些函数是否为 @track 函数
        #    - 如果是，获取这些 @track 函数的代码哈希
        deps_versions = op.versioner.get_deps_versions()
        #    - 将 op_version 和 deps_versions 组合成 version_key
        version_key = (op_version, deps_versions)

        # 2. 缓存查询
        #    - 将 version_key 和输入参数组合成一个唯一的查询ID
        #    - 在数据库中查找此ID
        cached_ref = self.query_database_for_call(version_key, bound_args)

        # 3. 决策
        if cached_ref is not None:
            # 3a. 命中缓存: 直接返回数据库中记录的输出 Ref
            return cached_ref
        else:
            # 3b. 未命中缓存:
            #   i.   执行原始函数体（这里才会调用 get_config_value）
            raw_output = op.func(*unwrapped_args) 
            #   ii.  将原始输出存入数据库，获得一个指向它的 Ref
            output_ref = self.save(raw_output)
            #   iii. 记录本次完整的调用信息（版本密钥、输入、输出Ref）到数据库
            self.log_call(version_key, bound_args, output_ref)
            #   iv.  返回新的输出 Ref
            return output_ref
```

## 三、`op_vs_track_example.py` 演练

结合上述原理，我们来分析示例代码的每一步：

-   **1. 首次运行**:
    -   `process_data` 被调用。`storage.call_op` 开始工作。
    -   **版本检查**: 计算 `process_data` (V1) 和 `get_config_value` (V1) 的代码哈希，生成 `version_key_v1`。
    -   **缓存查询**: 数据库是空的，未命中。
    -   **执行**: `process_data` 函数体执行，打印 "Executing @op..."。在其内部，`get_config_value` 被调用，打印 "Executing @track..."。耗时1秒。
    -   **存储**: `[10, 20, 30]` 被存入数据库。本次调用 (`version_key_v1`, `input_data`, `output_ref`) 被记录。

-   **2. 再次运行 (无变更)**:
    -   `process_data` 被调用。`storage.call_op` 开始工作。
    -   **版本检查**: 再次计算版本，得到与上次完全相同的 `version_key_v1`。
    -   **缓存查询**: 在数据库中找到了 `(version_key_v1, input_data)` 的记录。**命中缓存**。
    -   **决策**: 直接返回记录中的 `output_ref`。函数体完全不执行。耗时接近0秒。

-   **3. 修改 `@track` 函数**:
    -   `get_config_value` 被重新定义为 `get_config_value_v2`。
    -   `process_data` 被调用。`storage.call_op` 开始工作。
    -   **版本检查**: 计算 `process_data` (V1) 的哈希，**但 `get_config_value` 的哈希现在是 V2 了**。生成的 `version_key_v2` 与数据库中的 `version_key_v1` **不匹配**。
    -   **缓存查询**: 未命中。
    -   **执行**: `process_data` 重新执行，调用了新版的 `get_config_value_v2`。
    -   **存储**: 新的结果 `[15, 30, 45]` 和新的调用记录 (`version_key_v2`, ...) 被存入数据库。

-   **5. 仅修改 `@op` 函数**:
    -   `process_data` 被重新定义为 `process_data_v2`。
    -   `process_data` 被调用。`storage.call_op` 开始工作。
    -   **版本检查**: `process_data` 的哈希是 V2，依赖 `get_config_value` 的哈希也是 V2。生成 `version_key_v3`。**不匹配** 数据库中任何记录。
    -   **缓存查询**: 未命中，重新执行。

## 四、Mermaid 流程图: `@op` 函数调用决策过程

```mermaid
graph TD
    subgraph "@op Function Call: Internal Flow"
        A[Start: call @op function, e.g., process_data()] --> B{storage.call_op};
        
        B --> C{1. Compute Version Key};
        C --> C1["Compute hash of<br/>@op's own code<br/>(process_data)"];
        C --> C2["Scan @op's AST for calls"];
        C2 --> C3{"Is called function<br/>in @track registry?"};
        C3 -- Yes --> C4["Compute hash of<br/>@track's code<br/>(get_config_value)"];
        C3 -- No --> C5[Ignore non-tracked function];
        C4 & C5 --> C6[Combine all hashes into<br/>a single Version Key];
        
        C1 & C6 --> D{2. Query Cache};
        D --> D1["Combine Version Key<br/>and Input Arguments<br/>to create Query ID"];
        D1 --> E{"Find Query ID<br/>in Storage?"};
        
        E -- "Yes (HIT)" --> F[Return existing Ref<br/>from Storage];
        
        E -- "No (MISS)" --> G{3. Execute & Save};
        G --> G1["Execute original<br/>@op function body"];
        G1 --> G2["Save raw output to<br/>Storage, get new Ref"];
        G2 --> G3["Log the entire call:<br/>(Version Key, Inputs, new Ref)"];
        G3 --> H[Return new Ref];

        F --> Z[End];
        H --> Z[End];
    end

    %% Styling
    style A fill:#87CEEB,stroke:#4682B4
    style Z fill:#87CEEB,stroke:#4682B4
    style F fill:#90EE90,stroke:#2E8B57
    style G fill:#FFB6C1,stroke:#C71585
    style H fill:#90EE90,stroke:#2E8B57
``` 
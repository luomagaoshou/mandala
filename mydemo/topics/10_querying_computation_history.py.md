# `10_querying_computation_history.py` 深度解析：像查询数据库一样探索计算历史

本文档对 `mydemo/topics/10_querying_computation_history.py` 文件进行全面深入的分析，旨在阐明 `mandala` 框架的核心查询功能、实现原理、具体用法和关键应用场景。

## 一、代码总览

该脚本的核心目的是演示 `mandala` 最强大的功能之一：在计算发生并被记录后，如何通过 **`ComputationFrame` (计算框架，简称 cf)** 这一工具，以结构化、可编程的方式查询、分析和可视化所有被 `Storage` 捕获的计算历史。

其核心思想是：**将 `Storage` 视为一个专门为你的计算过程建立的数据库，而 `ComputationFrame` 就是这个数据库的查询语言（Query Builder）。**

## 二、核心组件与查询原理

`mandala` 的查询系统是其区别于普通缓存库的根本所在。它不仅仅是存储结果，更是存储了结果之间的 **关系**。

### 1. `ComputationFrame (cf)`: 动态查询构建器

- **定义**: `ComputationFrame` 对象本身不包含任何计算数据。相反，它是一个 **查询的描述** 或 **蓝图**。你通过链式调用一系列方法来构建这个蓝图，告诉 `mandala` 你对哪些计算历史感兴趣。
- **构建入口**: `storage.cf(...)` 是所有查询的起点。你可以从两种主要类型的对象开始：
    1.  **从具体结果开始**: `storage.cf(final_result)`。这里的 `final_result` 不是原始值 `15`，而是一个 `mandala` 的 `Ref` 对象，它像数据库中的主键一样，唯一指向 `Storage` 中的某条计算结果。
    2.  **从操作函数开始**: `storage.cf(add)`。这里的 `add` 是被 `@op` 装饰后的函数对象 (`Op` 对象)，代表了 `add` 这个操作本身。以此为起点，查询将默认选中所有对 `add` 函数的历史调用。

### 2. 查询扩展方法：探索计算图

构建查询蓝图的核心在于扩展初始选中的节点，以包含更多相关的计算历史。

- **`expand_back(recursive=True)`**: **向上游追溯**。这是最有用的方法之一。它从当前选中的节点（例如 `final_result`）开始，通过查询 `Storage` 来 **递归地** 寻找"创建"这些节点的所有上游计算，直到最原始的输入。它动态地从数据库中拉取数据，重构出完整的计算谱系。
- **`expand_all()`**: **双向全图探索**。从初始节点出发，同时向上游（它的来源）和下游（它被用在了哪里）两个方向进行探索，直到找到所有通过数据流连接在一起的计算节点，形成一个完整的、独立的计算故事。
- **其他方法**（如 `.upstream()`, `.downstream()`）: 这些方法在更细粒度的查询构建中有用，但 `expand_back` 和 `expand_all` 是进行历史分析时最常用的宏命令。

### 3. 查询执行方法：获取结果

当查询蓝图构建完毕后，你需要执行它以获取真实数据。

- **`.eval()`**: **执行查询并返回 DataFrame**。这是最核心的执行方法。它将 `ComputationFrame` 中描述的查询图转化为对后端数据库的复杂查询，并将结果格式化为一个 `pandas.DataFrame`。DataFrame 的每一 **行** 代表一个完整的、端到端的计算实例（一条完整的计算路径），每一 **列** 代表计算图中的一个节点（一个函数调用或一个值）。
- **`.get_func_table(fname)`**: **获取特定函数的调用表**。这是一个便捷方法，专门用于获取某个函数（如 `add`）所有调用的详细信息（输入参数和输出），通常比使用 `.eval()` 更直接、更简单。
- **`.draw()`**: **可视化查询**。将当前 `ComputationFrame` 所描述的计算图渲染成 SVG 图像，非常便于理解和调试。

## 三、代码分步解析

`demonstrate_querying` 函数清晰地展示了三种最典型的查询模式。

### 阶段一：生成计算历史

- 通过 `with storage:` 上下文，脚本执行了一系列 `add`, `multiply`, `subtract` 操作。
- `mandala` 自动捕获了这些函数调用，包括它们的输入、输出以及它们之间的依赖关系（例如 `multiply` 的输入 `v1` 是 `add` 的输出），并将这些信息存入 `Storage`。

### 阶段二：上游查询（从结果追溯源头）

- **目标**: "我想知道 `final_result` 是如何得到的？"
- **实现**:
    1.  `storage.cf(final_result)`: 从最终结果的引用 `final_result` 开始查询。
    2.  `.expand_back(recursive=True)`: 向上游递归探索，找到 `subtract` 调用，再找到 `v2` 和 `v3` 的来源，即 `multiply` 和 `add` 的调用，最终追溯到原始输入 `1, 2, 5, 10`。
    3.  `.eval()`: 将这条完整的计算链条转换成一个单行的 DataFrame，其中每一列都清晰地展示了计算路径上的每一个值。

### 阶段三：函数调用查询（分析特定操作）

- **目标**: "我想查看 `add` 函数的所有历史调用记录。"
- **实现**:
    1.  `storage.cf(add)`: 从 `add` 函数本身开始，选中所有对它的调用。
    2.  `.get_func_table('add')`: 使用这个便捷函数，直接将所有 `add` 调用的输入（`x`, `y`）和输出（`return`）提取到一个整洁的 DataFrame 中。

### 阶段四：全图查询（理解完整上下文）

- **目标**: "我想了解与 `subtract` 操作相关的所有计算是什么？"
- **实现**:
    1.  `storage.cf(subtract)`: 从 `subtract` 函数开始。
    2.  `.expand_all()`: 双向探索。向上游找到其输入 `v2` 和 `v3` 的完整来源；向下游（如果 `final_result` 被其他计算使用的话）也会继续探索。在这个例子中，它找到了整个计算网络。
    3.  `.eval()`: 将这个网络中的所有计算路径提取到 DataFrame 中。

## 四、Mermaid 流程图

```mermaid
graph TD
    subgraph "10_querying_computation_history.py 流程"
    
    A[开始: main()] --> B(demonstrate_querying);

    subgraph "阶段一: 生成计算历史"
        direction LR
        B1(Storage.new) --> B2(执行 add, multiply, subtract);
        B2 --> B3(历史记录存入 Storage);
    end
    B --> B3;

    subgraph "阶段二: 上游查询 (从结果追溯)"
        direction TB
        Q1_Start("storage.cf(final_result)\n(从 'Ref' 对象开始)") --> Q1_Expand("expand_back(recursive=True)\n(递归向上追溯)");
        Q1_Expand --> Q1_Eval("eval()\n(获取 DataFrame)");
        Q1_Expand --> Q1_Draw("draw()\n(生成上游图 a.svg)");
    end
    B3 --> Q1_Start;

    subgraph "阶段三: 函数调用查询"
        direction TB
        Q2_Start("storage.cf(add)\n(从 'Op' 对象开始)") --> Q2_GetTable("get_func_table('add')\n(获取函数调用表)");
    end
    B3 --> Q2_Start;

    subgraph "阶段四: 全图查询"
        direction TB
        Q3_Start("storage.cf(subtract)\n(从 'Op' 对象开始)") --> Q3_Expand("expand_all()\n(双向探索全图)");
        Q3_Expand --> Q3_Eval("eval()\n(获取 DataFrame)");
        Q3_Expand --> Q3_Draw("draw()\n(生成全景图 b.svg)");
    end
    B3 --> Q3_Start;

    Q1_Eval & Q1_Draw & Q2_GetTable & Q3_Eval & Q3_Draw --> Z[结束];
    
    %% Styling
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style Q1_Start fill:#ccf,stroke:#333
    style Q2_Start fill:#cfc,stroke:#333
    style Q3_Start fill:#fcf,stroke:#333
    end
```

## 五、应用场景与实现细节

### 为什么这很重要？—— 应用场景

1.  **科学调试 (Scientific Debugging)**: 当你得到一个意料之外或错误的结果时（比如一个模型的准确率异常），你可以使用 **上游查询** (`expand_back`) 从这个坏结果开始，精确地追溯出导致它的完整输入数据和每一步中间计算，就像一个针对计算过程的调试器。
2.  **影响性分析 (Impact Analysis)**: 在你准备修改一个核心函数（比如 `multiply`）之前，你可以使用 **全图查询** (`expand_all`) 来找到所有依赖这个函数的下游计算，以及所有它依赖的上游数据源，从而全面评估修改可能带来的影响。
3.  **实验对比与审计**: 你可以运行多次实验，然后使用 **函数调用查询** (`get_func_table`) 或 `.eval()` 将所有实验的参数和结果提取到一个大的 DataFrame 中，利用 `pandas` 的强大功能进行分组、排序和对比分析，这对于超参数调优和结果审计至关重要。

### 底层实现细节

- **`Ref` 对象**: `@op` 函数的返回值不是 Python 的原始对象（如 `int`），而是一个 `Ref`（引用）对象。这个对象本质上是指向 `Storage` 中数据的一个指针。`mandala` 通过重载操作符（如 `+`, `*`），使得你可以像操作普通 Python 对象一样操作 `Ref` 对象，但所有操作都会被框架拦截并记录。这是实现自动依赖追踪和构建计算图的基石。
- **懒查询 (Lazy Execution)**: 构建 `ComputationFrame` 的过程（如调用 `expand_back`）是 **懒执行** 的。它只修改查询蓝图，不执行任何数据库操作。只有当你调用 `.eval()` 或 `.draw()` 这样的执行方法时，`mandala` 才会将这个蓝图翻译成真正的数据库查询指令并执行，从而提高了效率。 
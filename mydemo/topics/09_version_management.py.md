# `09_version_management.py` 代码深度解析与流程图

本文档对 `mydemo/topics/09_version_management.py` 文件进行全面深入的分析，旨在阐明其核心功能、实现原理、具体用法和适用场景。

## 一、代码总览

该脚本的核心目的是演示 `mandala` 库强大的 **版本管理** 和 **依赖追踪** 功能。它通过一个典型的机器学习流程（数据加载、预处理、模型训练、评估）来展示 `mandala` 如何自动捕捉代码和其依赖（如函数、全局变量）的变更，并智能地决定是否需要重新计算，从而实现高效、可复现的实验流程。

## 二、核心组件与原理

`mandala` 的版本管理系统主要围绕以下几个核心概念构建：

### 1. `Storage`：存储引擎

- **定义**: `Storage` 是 `mandala` 的核心对象，它连接到一个后端数据库（默认为本地文件），用于存储所有计算的结果、代码版本和依赖关系。
- **用法**: `storage = Storage(deps_path='__main__')`
- **原理**: 初始化时，`deps_path='__main__'` 参数告诉 `mandala` 需要追踪在当前主脚本 (`__main__`) 中定义的依赖项。所有被 `@op` 或 `@track` 装饰的函数以及它们引用的全局变量都会被监控。

### 2. `@op`：操作装饰器

- **定义**: 将一个函数标记为㴡个可记忆的 **操作 (Operation)**。`mandala` 会自动缓存 `@op` 函数的返回值。
- **原理**: 当一个 `@op` 函数被调用时，`mandala` 会检查：
    1.  该函数的代码（内容哈希）。
    2.  传入的参数（值或指向其他操作结果的指针）。
    3.  所有依赖（`@track` 函数和全局变量）的版本。
    如果这个组合之前已经执行过，`mandala` 会直接从 `Storage` 中返回缓存的结果，避免重复计算。如果任何一部分发生变化，则会触发重新计算。

### 3. `@track`：依赖追踪装饰器

- **定义**: 将一个函数标记为另一个 `@op` 函数的 **依赖项 (Dependency)**。它本身的结果不会被直接缓存，但它的代码变更会被追踪。
- **原理**: 如果一个 `@track` 函数（例如 `scale_data`）的源代码发生变化，那么所有依赖于它的 `@op` 函数（例如 `train_model`）在下一次调用时都会被强制重新计算，即使 `@op` 函数本身的代码和参数没有变。这确保了计算图的完整性和结果的准确性。

### 4. 全局变量追踪

- **原理**: `mandala` 能够自动检测 `@op` 函数对全局变量的依赖（如 `load_data` 对 `N_CLASS` 的依赖）。当全局变量的值发生变化时，`mandala` 会将其视为一个 **破坏性变更 (Breaking Change)**，并要求用户确认是否要基于新值进行重新计算。

## 三、代码分步解析

`demonstrate_version_management` 函数是整个演示的核心，其执行流程可以分为四个阶段。

### 阶段一：初始版本运行

1.  **初始化**: `storage = Storage(deps_path='__main__')` 创建存储实例。
2.  **执行**: 在 `with storage:` 上下文中，依次调用 `load_data`, `train_model`, `eval_model`。
3.  **缓存**: 由于是首次运行，所有 `@op` 函数都会被实际执行，其代码版本、依赖、参数和返回值被完整地记录在 `Storage` 中。
4.  **版本查询**: `storage.versions(train_model)` 可以查询 `train_model` 函数当前已知的版本信息。

### 阶段二：模拟代码与依赖变更

脚本通过重新定义函数和修改全局变量来模拟开发过程中的代码演进：

1.  **全局变量变更 (破坏性)**: `N_CLASS` 从 `10` 修改为 `5`。这会影响 `load_data` 函数。
2.  **依赖函数变更 (破坏性)**: `scale_data` 函数被重新定义，从 V1（只中心化）升级到 V2（中心化和标准化）。这会影响 `train_model` 和 `eval_model`。
3.  **操作函数变更 (非破坏性)**: `eval_model` 函数被重新定义，从 V1（返回原始准确率）升级到 V2（返回四舍五入的准确率）。`mandala` 会将此视为一个新版本的函数。

### 阶段三：运行更新后的代码

1.  **变更检测**: 再次进入 `with storage:` 上下文并调用函数时，`mandala` 会检测到上述所有变更。
2.  **用户交互 (模拟)**: 对于破坏性变更（`N_CLASS` 和 `scale_data`），`mandala` 会暂停并询问用户如何处理。脚本使用 `patch` 和 `mock_input` 自动回答 "y" (yes)，确认变更并同意重新计算。
3.  **智能执行**:
    - `load_data` 因其依赖 `N_CLASS` 变更而重新执行。
    - `train_model` 因其依赖 `scale_data` 变更而重新执行。
    - `eval_model` 本身也已更新，因此也会重新执行。
    `mandala` 确保了只有受变更影响的计算路径被重新执行。

### 阶段四：分析与验证

1.  **计算历史分析**: `storage.cf(eval_model).expand_all()` 创建一个 **计算框架 (ComputationFrame)**，这是一个强大的工具，可以用来查询和分析 `eval_model` 的所有历史运行记录，包括不同版本、不同参数的调用。
2.  **版本验证**: `storage.versions(eval_model)` 此时会显示 `eval_model` 存在两个版本，反映了代码的变更历史。

## 四、Mermaid 流程图

```mermaid
graph TD
    subgraph "09_version_management.py 业务流程"

    A[开始: main()] --> B(demonstrate_version_management);

    subgraph "阶段一: 初始版本运行"
        direction LR
        B1(Storage.new) --> B2(load_data V1\n(N_CLASS=10));
        B2 --> B3(train_model V1);
        B3 -- X, y --> B4(eval_model V1);
        B4 --> B5(打印 V1 结果);
        B5 --> B6(storage.versions\n(train_model));
    end

    B --> C{阶段二: 模拟代码变更};

    subgraph "变更内容"
        direction TB
        C1[修改全局变量 N_CLASS=5];
        C2[重定义 @track scale_data];
        C3[重定义 @op eval_model];
    end
    
    C --> D{阶段三: 运行更新后代码};
    subgraph "变更检测与重新计算"
        direction LR
        D1(mandala 检测到\nN_CLASS 变更);
        D1 --> D2(模拟用户输入 'y');
        D2 --> D3(load_data V2 执行);

        D4(mandala 检测到\nscale_data 变更);
        D4 --> D5(模拟用户输入 'y');
        D5 --> D6(train_model V2 执行);

        D6 --> D7(eval_model V2 执行);
        D7 --> D8(打印 V2 结果);
    end

    D --> E{阶段四: 分析与验证};
    subgraph "历史分析"
        direction LR
        E1(storage.cf(eval_model).expand_all()) --> E2(打印计算历史);
        E3(storage.versions(eval_model)) --> E4(打印 eval_model 的所有版本);
    end

    E --> F[结束];

    %% Styling
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#f90,stroke:#333,stroke-width:2px
    style D fill:#0cf,stroke:#333,stroke-width:2px
    style E fill:#0f9,stroke:#333,stroke-width:2px
    end
```

## 五、使用场景

`mandala` 的版本管理功能在以下场景中尤其有用：

1.  **机器学习实验**: 在调整模型架构、特征工程步骤或超参数时，`mandala` 可以避免对未改变的部分进行不必要的重复计算，极大地节省了时间和计算资源。
2.  **数据流水线 (Data Pipeline)**: 当数据处理流程中的某个步骤发生改变时，`mandala` 能够智能地只重新运行该步骤及其下游依赖，确保数据的一致性和时效性。
3.  **可复现性研究**: `mandala` 将代码、数据和结果绑定在一起，并记录了完整的演化历史。这使得任何一次实验的结果都可以被精确复现，是科学研究和合规性审查的有力保障。
4.  **探索性数据分析**: 在交互式环境中（如 Jupyter Notebook），分析师可以自由地修改代码和参数进行探索，`mandala` 在后台默默地管理着所有计算的版本，让探索过程既高效又不会混乱。 
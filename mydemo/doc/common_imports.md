# Common Imports 公共导入模块

## 概述

Common Imports 模块是 mandala 框架的基础导入模块，提供了项目中常用的 Python 标准库、第三方库的统一导入，以及日志系统的配置。该模块确保了整个项目的依赖管理一致性，并提供了调试会话功能。

## 标准库导入

### 核心功能库

```python
import time
import traceback
import random
import logging
import itertools
import copy
import hashlib
import io
import os
import shutil
import sys
import joblib
import inspect
import binascii
import asyncio
import ast
import types
import tempfile
```

**导入说明:**
- `time`: 时间处理功能
- `traceback`: 异常跟踪和调试
- `random`: 随机数生成
- `logging`: 日志记录系统
- `itertools`: 迭代器工具
- `copy`: 对象拷贝操作
- `hashlib`: 哈希算法
- `io`: 输入输出操作
- `os`: 操作系统接口
- `shutil`: 高级文件操作
- `sys`: 系统相关参数和函数
- `joblib`: 并行处理和持久化
- `inspect`: 对象检查和内省
- `binascii`: 二进制和ASCII转换
- `asyncio`: 异步I/O
- `ast`: 抽象语法树
- `types`: 动态类型创建
- `tempfile`: 临时文件和目录

### 数据结构库

```python
from collections import defaultdict, OrderedDict
```

**导入说明:**
- `defaultdict`: 提供默认值的字典
- `OrderedDict`: 保持插入顺序的字典

### 类型提示库

```python
from typing import (
    Any,
    Dict,
    List,
    Callable,
    Tuple,
    Iterable,
    Optional,
    Set,
    Union,
    TypeVar,
    Literal,
)
```

**类型说明:**
- `Any`: 任意类型
- `Dict`: 字典类型
- `List`: 列表类型
- `Callable`: 可调用对象类型
- `Tuple`: 元组类型
- `Iterable`: 可迭代对象类型
- `Optional`: 可选类型（Union[T, None]）
- `Set`: 集合类型
- `Union`: 联合类型
- `TypeVar`: 类型变量
- `Literal`: 字面量类型

### 路径处理库

```python
from pathlib import Path
```

**功能:** 现代化的路径操作接口

## 第三方库导入

### 数据处理库

```python
import pandas as pd
import pyarrow as pa
import numpy as np
```

**导入说明:**
- `pandas`: 数据分析和操作库
- `pyarrow`: 高性能列式数据格式
- `numpy`: 数值计算库

## 日志系统配置

### Rich 增强日志

```python
try:
    import rich
    has_rich = True
except ImportError:
    has_rich = False

if has_rich:
    from rich.logging import RichHandler
    logger = logging.getLogger("mandala")
    logging_handler = RichHandler(enable_link_path=False)
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="INFO", format=FORMAT, datefmt="[%X]", handlers=[logging_handler]
    )
```

**配置特点:**
- **优雅降级**: 如果 Rich 不可用，回退到标准日志
- **增强显示**: 使用 Rich 提供彩色和格式化输出
- **禁用链接**: 设置 `enable_link_path=False` 避免路径链接
- **简化格式**: 使用简单的消息格式
- **时间显示**: 使用 `[%X]` 格式显示时间

### 标准日志配置

```python
else:
    logger = logging.getLogger("mandala")
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel(logging.INFO)
```

**配置特点:**
- **详细格式**: 包含文件名、行号、函数名
- **调试友好**: 便于定位问题源头
- **固定级别**: 设置为 INFO 级别

## 调试会话功能

### Session 类

```python
class Session:
    # for debugging

    def __init__(self):
        self.items = []
        self._scope = None
```

**初始化参数:**
- `items`: 存储会话项目的列表
- `_scope`: 存储当前作用域的变量

### d() 方法

```python
def d(self):
    scope = inspect.currentframe().f_back.f_locals
    self._scope = scope
```

**功能描述:**
- 捕获调用者的本地变量作用域
- 使用 `inspect.currentframe()` 获取调用栈
- 存储到 `_scope` 属性中

### dump() 方法

```python
def dump(self):
    assert self._scope is not None
    scope = inspect.currentframe().f_back.f_locals
    print(f"Dumping {self._scope.keys()} into local scope")
    scope.update(self._scope)
```

**功能描述:**
- 将之前捕获的作用域变量导入到当前作用域
- 通过 `scope.update()` 更新本地变量
- 打印导入的变量名称

### 全局会话实例

```python
sess = Session()
```

**用途:** 提供全局可用的调试会话实例

## 使用示例

### 基本导入使用

```python
from mandala1.common_imports import *

# 使用标准库
current_time = time.time()
random_number = random.randint(1, 100)

# 使用数据处理库
df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
array = np.array([1, 2, 3, 4, 5])

# 使用类型提示
def process_data(data: Dict[str, Any]) -> Optional[List[int]]:
    return [1, 2, 3] if data else None

# 使用路径处理
config_path = Path("config.json")
if config_path.exists():
    print("配置文件存在")
```

### 日志系统使用

```python
from mandala1.common_imports import logger

# 记录不同级别的日志
logger.info("这是一条信息日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
logger.debug("这是一条调试日志")

# 在函数中使用
def my_function():
    logger.info("函数开始执行")
    try:
        # 一些操作
        result = "成功"
        logger.info(f"操作结果: {result}")
        return result
    except Exception as e:
        logger.error(f"操作失败: {e}")
        raise
```

### 调试会话使用

```python
from mandala1.common_imports import sess

def debug_function():
    local_var = "调试变量"
    debug_data = {"key": "value"}
    
    # 捕获当前作用域
    sess.d()
    
    # 在其他地方使用
    def another_function():
        # 导入之前捕获的变量
        sess.dump()
        # 现在可以使用 local_var 和 debug_data
        print(f"导入的变量: {local_var}")
        print(f"导入的数据: {debug_data}")
    
    another_function()
```

## 设计理念

### 统一导入管理

- 所有常用库的导入集中管理
- 避免重复导入声明
- 确保项目中导入的一致性

### 优雅降级

- 可选依赖的安全检测
- 功能在依赖不可用时的回退机制
- 不影响核心功能的运行

### 调试支持

- 提供便捷的调试工具
- 支持作用域变量的捕获和传递
- 简化开发过程中的调试操作

## 扩展指南

### 添加新的标准库导入

```python
# 在适当的位置添加新的导入
import new_standard_library
```

### 添加新的第三方库导入

```python
# 使用安全导入模式
try:
    import new_third_party_library
    has_new_library = True
except ImportError:
    has_new_library = False
```

### 自定义日志格式

```python
# 修改日志格式
if has_rich:
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level="INFO", format=FORMAT, datefmt="[%Y-%m-%d %H:%M:%S]", 
        handlers=[logging_handler]
    )
```

## 注意事项

1. **导入顺序**: 确保标准库先于第三方库导入
2. **依赖管理**: 所有可选依赖都应该使用 try-except 块
3. **日志级别**: 根据环境调整日志级别
4. **性能影响**: 避免导入不必要的大型库
5. **版本兼容**: 考虑不同版本库的兼容性

## 相关模块

- `config`: 使用本模块的基础导入
- `storage`: 依赖日志系统和基础库
- `model`: 使用类型提示和基础功能
- `utils`: 使用工具函数和数据处理库

Common Imports 模块是 mandala 框架的基础设施，为整个项目提供了统一的导入管理和基础功能支持。 
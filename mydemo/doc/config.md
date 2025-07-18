# Config 配置管理模块

## 概述

Config 模块提供了 mandala 框架的全局配置管理功能，包括路径管理、可选依赖检测、以及特定库的实用工具函数。该模块负责检测和管理系统中各种可选依赖的可用性，并提供相应的配置参数。

## 导入依赖

```python
from .common_imports import *
```

该模块依赖于 `common_imports` 模块，后者提供了基础的 Python 标准库导入和第三方库导入。

## 路径管理

### get_mandala_path()

获取 mandala 包的安装路径。

```python
def get_mandala_path() -> Path:
    import mandala
    return Path(os.path.dirname(mandala.__file__))
```

**返回值:**
- `Path`: mandala 包的安装目录路径

**功能描述:**
- 动态获取 mandala 包的安装位置
- 返回 `Path` 对象，方便路径操作
- 用于确定框架的根目录位置

## Config 类

### 核心配置属性

```python
class Config:
    func_interface_cls_name = "Op"
    mandala_path = get_mandala_path()
    module_name = "mandala"
    tests_module_name = "mandala.tests"
```

**配置说明:**
- `func_interface_cls_name`: 函数接口类名，固定为 "Op"
- `mandala_path`: mandala 包的安装路径
- `module_name`: 主模块名称
- `tests_module_name`: 测试模块名称

### 可选依赖检测

Config 类通过 try-except 块检测各种可选依赖的可用性：

#### PIL 图像处理库

```python
try:
    import PIL
    has_pil = True
except ImportError:
    has_pil = False
```

**用途:** 图像处理和可视化功能

#### PyTorch 机器学习框架

```python
try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False
```

**用途:** 深度学习模型支持和张量操作

#### Rich 美化输出库

```python
try:
    import rich
    has_rich = True
except ImportError:
    has_rich = False
```

**用途:** 增强终端输出格式和日志美化

#### PrettyTable 表格格式化库

```python
try:
    import prettytable
    has_prettytable = True
except ImportError:
    has_prettytable = False
```

**用途:** 数据表格的美化显示

## PyTorch 支持功能

### tensor_to_numpy()

当 PyTorch 可用时，提供张量到 NumPy 数组的转换功能。

```python
def tensor_to_numpy(obj: Union[torch.Tensor, dict, list, tuple, Any]) -> Any:
    """
    Recursively convert PyTorch tensors in a data structure to numpy arrays.

    Parameters
    ----------
    obj : any
        The input data structure.

    Returns
    -------
    any
        The data structure with tensors converted to numpy arrays.
    """
```

**参数:**
- `obj`: 输入数据结构，可以是张量、字典、列表、元组或任何其他类型

**返回值:**
- `Any`: 转换后的数据结构，其中所有张量都被转换为 NumPy 数组

**功能特点:**
- **递归转换**: 能够处理嵌套的数据结构
- **类型保持**: 保持原始数据结构的类型（dict、list、tuple）
- **GPU 支持**: 自动处理 GPU 张量的 CPU 转换
- **梯度分离**: 自动调用 `detach()` 分离梯度

**实现逻辑:**
1. 如果是 `torch.Tensor`，调用 `detach().cpu().numpy()` 转换
2. 如果是字典，递归处理所有值
3. 如果是列表，递归处理所有元素
4. 如果是元组，递归处理所有元素并保持元组类型
5. 其他类型直接返回

## 使用示例

### 基本配置访问

```python
from mandala1.config import Config

# 检查可选依赖
if Config.has_torch:
    print("PyTorch 可用")
    
if Config.has_pil:
    print("PIL 可用")
    
if Config.has_rich:
    print("Rich 可用")
    
if Config.has_prettytable:
    print("PrettyTable 可用")

# 获取路径信息
print(f"Mandala 路径: {Config.mandala_path}")
print(f"模块名称: {Config.module_name}")
```

### 张量转换示例

```python
import torch
from mandala1.config import tensor_to_numpy

# 单个张量转换
tensor = torch.tensor([1, 2, 3, 4])
numpy_array = tensor_to_numpy(tensor)
print(f"转换结果: {numpy_array}")

# 复杂数据结构转换
complex_data = {
    'tensor1': torch.tensor([1.0, 2.0, 3.0]),
    'tensor2': torch.tensor([[1, 2], [3, 4]]),
    'list': [torch.tensor([5, 6]), torch.tensor([7, 8])],
    'tuple': (torch.tensor([9, 10]), "string"),
    'scalar': 42
}

converted_data = tensor_to_numpy(complex_data)
print(f"转换结果: {converted_data}")
```

## 设计理念

### 优雅降级

Config 模块采用优雅降级的设计理念：
- 所有可选依赖都通过 try-except 安全检测
- 不可用的依赖不会阻止核心功能运行
- 通过布尔标志提供功能可用性信息

### 中心化配置

- 所有全局配置集中在一个类中管理
- 提供统一的配置访问接口
- 便于维护和扩展

### 动态适应

- 动态检测系统环境和可用库
- 根据可用性调整功能特性
- 提供条件性功能支持

## 扩展指南

### 添加新的可选依赖

```python
# 在 Config 类中添加新的依赖检测
try:
    import new_library
    has_new_library = True
except ImportError:
    has_new_library = False
```

### 添加条件性功能

```python
# 在模块末尾添加条件性功能
if Config.has_new_library:
    import new_library
    
    def new_library_function():
        # 使用新库的功能
        pass
```

## 注意事项

1. **导入顺序**: 确保 `common_imports` 先于其他模块导入
2. **路径处理**: 使用 `Path` 对象而不是字符串进行路径操作
3. **异常处理**: 所有可选依赖检测都应该使用 try-except 块
4. **版本兼容**: 考虑不同版本库的兼容性问题

## 相关模块

- `common_imports`: 提供基础导入功能
- `storage`: 使用配置信息进行存储管理
- `viz`: 使用 PIL 和 Rich 进行可视化
- `model`: 使用 PyTorch 相关功能

Config 模块是 mandala 框架的配置中心，为整个系统提供了灵活的环境适应能力和统一的配置管理接口。 
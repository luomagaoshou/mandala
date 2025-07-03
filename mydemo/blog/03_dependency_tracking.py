"""
文档来源：
- 文件：docs_source/blog/02_deps.ipynb
- 主题：依赖追踪（Dependency Tracking）
- 描述：演示了 mandala 的依赖追踪功能，包括装饰器方法追踪、类方法追踪等
- 关键概念：
  1. TracerState：追踪器状态管理
  2. TrackedDict：被追踪的字典对象
  3. track 装饰器：用于追踪函数调用
  4. 嵌套类方法追踪：展示复杂调用场景
- 相关文档：
  - docs/docs/blog/02_deps.md
  - docs/docs/topics/02_retracing.md

本示例展示了如何使用 mandala 的依赖追踪功能来监控和分析函数调用关系。
主要功能包括：
1. 基本函数调用追踪
2. 类方法和嵌套方法追踪
3. 依赖图的生成和可视化
4. 追踪状态的管理和控制
"""

from types import FunctionType
from functools import wraps, update_wrapper
import copy
from typing import Optional, Any, Callable

class TracerState:
    """全局追踪器状态，用于存储当前活动的追踪器。"""
    current: Optional['Tracer'] = None

class TrackedDict(dict):
    """
    特殊的字典类，用于追踪对全局变量的访问。
    当访问字典中的值时，会通知追踪器。
    """
    def __init__(self, original: dict):
        self.__original__ = original

    def __getitem__(self, __key: str) -> Any:
        value = self.__original__.__getitem__(__key)
        if TracerState.current is not None:
            tracer = TracerState.current
            tracer.register_global_access(key=__key, value=value)
        return value

def make_tracked_copy(f: FunctionType) -> FunctionType:
    """
    创建函数的副本，将其全局变量字典替换为可追踪的版本。
    
    参数:
        f: 要复制的函数
    返回:
        带有可追踪全局变量的函数副本
    """
    result = FunctionType(
        code=f.__code__,
        globals=TrackedDict(f.__globals__),
        name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__,
    )
    result = update_wrapper(result, f)
    result.__module__ = f.__module__
    result.__kwdefaults__ = copy.deepcopy(f.__kwdefaults__)
    result.__annotations__ = copy.deepcopy(f.__annotations__)
    return result

def track(f: FunctionType):
    """
    追踪函数调用和全局变量访问的装饰器。
    
    参数:
        f: 要追踪的函数
    返回:
        包装后的函数
    """
    f = make_tracked_copy(f)

    @wraps(f)
    def wrapper(*args, **kwargs):
        tracer = TracerState.current
        if tracer is not None:
            tracer.register_call(func=f)
            result = f(*args, **kwargs)
            tracer.register_return()
            return result
        else:
            return f(*args, **kwargs)

    return wrapper

class Tracer:
    """
    追踪器类，用于记录函数调用和全局变量访问。
    使用上下文管理器模式，只在 with 块内进行追踪。
    """
    def __init__(self):
        # 调用栈，存储 (模块名, 函数限定名) 元组
        self.stack = []
        # 调用图，存储 (调用者模块, 调用者限定名, 被调用者模块, 被调用者限定名) 元组
        self.graph = []
    
    def register_call(self, func: Callable):
        """
        注册函数调用，更新调用栈和调用图。
        
        参数:
            func: 被调用的函数
        """
        module_name, qual_name = func.__module__, func.__qualname__
        self.stack.append((module_name, qual_name))
        if len(self.stack) > 1:
            caller_module, caller_qual_name = self.stack[-2]
            self.graph.append((
                caller_module, caller_qual_name,
                module_name, qual_name
            ))
    
    def register_return(self):
        """注册函数返回，从调用栈中移除最后一个调用。"""
        self.stack.pop()
    
    def register_global_access(self, key: str, value):
        """
        注册全局变量访问。
        
        参数:
            key: 全局变量名
            value: 全局变量值
        """
        assert len(self.stack) > 0
        caller_module, caller_qual_name = self.stack[-1]
        self.graph.append((caller_module, caller_qual_name, {key: value}))
    
    def __enter__(self):
        TracerState.current = self
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        TracerState.current = None

# 示例代码
if __name__ == "__main__":
    # 定义一些全局变量
    A = 23
    B = 42

    @track
    def f(x):
        """简单函数，访问全局变量 A"""
        return x + A

    class C:
        """
        示例类，展示方法追踪和嵌套类。
        包含普通方法和嵌套类的方法。
        """
        @track
        def __init__(self, x):
            self.x = x + B

        @track
        def m(self, y):
            return self.x + y

        class D:
            @track
            def __init__(self, x):
                self.x = x + f(x)

            @track
            def m(self, y):
                return y + A

    @track
    def g(x):
        """
        复杂函数，根据输入选择不同的执行路径。
        展示条件执行和不同类型的方法调用。
        """
        if x % 2 == 0:
            return C(x).m(x)
        else:
            return C.D(x).m(x)

    # 测试奇数输入
    print("测试奇数输入 (x=23):")
    with Tracer() as t1:
        result = g(23)
    print(f"结果: {result}")
    print("调用图:")
    for edge in t1.graph:
        print(f"  {edge}")

    print("\\n测试偶数输入 (x=42):")
    with Tracer() as t2:
        result = g(42)
    print(f"结果: {result}")
    print("调用图:")
    for edge in t2.graph:
        print(f"  {edge}") 
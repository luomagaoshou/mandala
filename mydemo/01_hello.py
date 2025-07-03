# 导入 mandala 库
# 该代码基于 docs_source/tutorials/01_hello.ipynb 的内容
from mandala.imports import *
import time
import os

# 确保 mydemo/mandala_storage 目录存在
if not os.path.exists('mydemo/mandala_storage'):
    os.makedirs('mydemo/mandala_storage')

# 1. 初始化存储
storage = Storage( 
    # where to look for dependencies; use `None` to prevent versioning altogether
    deps_path='__main__',
    # 明确指定数据库路径，以避免使用默认位置
    db_path='mydemo/mandala_storage/db'
) 

# 2. 定义一个带 @op 装饰器的函数
@op
def inc(x: int) -> int:
    """
    一个简单的自增函数，用于演示 @op 的使用。
    """
    print(f"Executing: inc({x})")
    time.sleep(1) # 模拟一个耗时操作
    return x + 1

# 3. 在 storage 上下文中调用函数
with storage:
    start_time = time.time()
    a = inc(1)
    b = inc(1) 
    end_time = time.time()
    print(f'总共用时: {round(end_time - start_time)} 秒')

print("\n'mydemo/01_hello.py' 执行完毕。") 
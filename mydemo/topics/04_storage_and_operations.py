"""
文档来源：
- 文件：docs_source/topics/01_storage_and_ops.ipynb
- 主题：存储和 @op 装饰器
- 描述：展示了 Storage 对象和 @op 装饰器的基本用法
- 关键概念：
  1. Storage：存储所有数据的容器
  2. @op 装饰器：用于记忆化函数调用
  3. Ref：对存储中对象的引用
  4. Call：存储函数调用的输入和输出
- 相关文档：
  - docs/docs/topics/01_storage_and_ops.md
  - docs/docs/topics/02_retracing.md

本示例展示了 Storage 和 @op 的基本功能：
1. 创建和配置存储
2. 定义和使用装饰器函数
3. 处理引用和调用对象
4. 管理内存中的对象
"""

import os
from mandala.imports import Storage, op

def setup_storage():
    """创建并配置存储
    
    返回:
        配置好的存储对象
    """
    # 定义数据库路径
    db_path = 'mydemo/mandala_storage/storage_demo.db'
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    # 如果存在则删除旧数据库
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # 创建存储实例
    return Storage(
        db_path=db_path,  # 持久化存储
        deps_path='__main__'  # 仅跟踪当前会话中定义的函数
    )

@op
def sum_args(a, *args, b=1, **kwargs):
    """示例操作：计算参数之和
    
    参数:
        a: 第一个参数
        *args: 位置参数
        b: 关键字参数，默认为1
        **kwargs: 其他关键字参数
    返回:
        所有参数的和
    """
    return a + sum(args) + b + sum(kwargs.values())

def demonstrate_storage_ops():
    """演示存储和操作的基本用法"""
    storage = setup_storage()
    
    print("1. 基本操作调用:")
    with storage:
        # 调用操作并保存结果
        s = sum_args(6, 7, 8, 9, c=11)
        print(f"- 计算结果: {s}")
    
    print("\n2. 重复调用（从存储加载）:")
    with storage:
        # 相同的调用将从存储中加载
        s = sum_args(6, 7, 8, 9, c=11)
        print(f"- 加载的引用: {s}")
    
    print("\n3. 引用操作:")
    # 解包引用获取实际值
    value = storage.unwrap(s)
    print(f"- 解包后的值: {value}")
    
    # 加载引用到内存
    loaded_ref = storage.attach(obj=s, inplace=False)
    print(f"- 加载到内存的引用: {loaded_ref}")
    
    print("\n4. 调用对象操作:")
    # 获取创建引用的调用
    call = storage.get_ref_creator(ref=s)
    print(f"- 创建引用的调用: {call}")
    print(f"- 调用的输入: {call.inputs}")
    print(f"- 调用的输出: {call.outputs}")

def main():
    print("演示 Storage 和 @op 的基本用法...")
    demonstrate_storage_ops()

if __name__ == '__main__':
    main() 
"""
文档来源：
- 文件：docs_source/blog/01_cf.ipynb
- 主题：整洁计算（Tidy Computations）
- 描述：展示了 ComputationFrame 数据结构的基本概念和用法
- 关键概念：
  1. 计算图：操作和变量的有向图
  2. 部分执行：支持条件执行和缺失值
  3. 数据框转换：计算历史的表格视图
  4. 图扩展：自动添加上下文信息
- 相关文档：
  - docs/docs/blog/01_cf.md
  - docs/docs/topics/03_cf.md

本示例展示了 ComputationFrame 的基本功能：
1. 运行基本计算并自动保存
2. 创建和扩展计算框架
3. 转换为数据框进行分析
4. 可视化计算图结构
"""

from mandala.imports import Storage, op

@op(output_names=['y'])
def increment(x):
    """递增函数
    
    参数:
        x: 输入数字
    返回:
        y: 递增后的数字
    """
    return x + 1

@op(output_names=['w'])
def add(y, z):
    """加法函数
    
    参数:
        y: 第一个数字
        z: 第二个数字
    返回:
        w: 两数之和
    """
    return y + z

def main():
    # 初始化存储并执行计算
    with Storage() as storage:
        print("执行基本计算...")
        # 对范围内的每个数字执行操作
        for x in range(5):
            y = increment(x)
            if x % 2 == 0:  # 仅对偶数执行加法
                w = add(y=y, z=x)
        
        print("\n创建和分析计算框架...")
        # 获取 increment 操作的计算框架
        cf = storage.cf(increment)
        print("- 初始计算框架创建完成")
        
        # 向前扩展计算框架以包含 add 操作
        cf = cf.expand_forward()
        print("- 计算框架已向前扩展")
        
        # 转换为数据框并显示
        print("\n计算历史数据框:")
        df = cf.df()
        print(df)
        
        # 可视化计算图
        print("\n计算图结构:")
        cf.draw(verbose=True, orientation='LR')

if __name__ == '__main__':
    main() 
"""
文档来源：
- 文件：docs_source/topics/06_advanced_cf.ipynb
- 主题：高级计算框架工具
- 描述：展示了计算框架的高级功能和操作
- 关键概念：
  1. 集合操作：并集和交集
  2. 图操作：上游和下游计算
  3. 计算图分析：节点和边的操作
  4. 计算历史：追踪和分析计算过程
- 相关文档：
  - docs/docs/topics/06_advanced_cf.md
  - docs/docs/topics/03_cf.md

本示例展示了计算框架的高级功能：
1. 集合操作（并集、交集）
2. 图操作（上游、下游）
3. 计算图分析
4. 计算历史追踪
"""

from mandala.imports import Storage, op

@op
def inc(x):
    """递增函数
    
    参数:
        x: 输入数字
    返回:
        递增后的数字
    """
    return x + 1

@op
def add(y, z):
    """加法函数
    
    参数:
        y: 第一个数字
        z: 第二个数字
    返回:
        两数之和
    """
    return y + z

@op
def square(w):
    """平方函数
    
    参数:
        w: 输入数字
    返回:
        平方结果
    """
    return w ** 2

@op
def divmod_(u, v):
    """除法和取模函数
    
    参数:
        u: 被除数
        v: 除数
    返回:
        商和余数的元组
    """
    return divmod(u, v)

def demonstrate_advanced_cf():
    """演示计算框架的高级功能"""
    storage = Storage()
    
    print("1. 创建复杂的计算历史:")
    with storage:
        # 创建一系列计算
        xs = [inc(i) for i in range(5)]
        ys = [add(x, z=42) for x in xs] + [square(x) for x in range(5, 10)]
        zs = [divmod_(x, y) for x, y in zip(xs, ys[3:8])]
        
        print("- xs:", [storage.unwrap(x) for x in xs])
        print("- ys:", [storage.unwrap(y) for y in ys])
        print("- zs:", [storage.unwrap(z) for z in zs])
    cf = (storage.cf(add) | storage.cf(square)).expand_all()
    cf.draw(verbose=True, path='mydemo/svg/computation_history.svg')
    return
    print("\n2. 分析中间层计算:")
    # 获取 add 和 square 操作的并集视图
    cf_union = (storage.cf(add) | storage.cf(square)).expand_all()
    print("- 并集计算框架:")
    print(cf_union)
    
    print("\n3. 分析上游计算:")
    # 获取 divmod_ 的上游计算
    cf = storage.cf(divmod_).expand_all()
    # 获取第一个变量名
    var_name = next(iter(cf.vs.keys()))
    cf_upstream = cf.upstream(var_name)
    print("- 上游计算框架:")
    print(cf_upstream)
    
    print("\n4. 分析下游计算:")
    # 获取 inc 的下游计算
    cf = storage.cf(inc).expand_all()
    var_name = next(iter(cf.vs.keys()))
    cf_downstream = cf.downstream(var_name)
    print("- 下游计算框架:")
    print(cf_downstream)

def main():
    print("演示计算框架的高级功能...")
    demonstrate_advanced_cf()

if __name__ == '__main__':
    main()

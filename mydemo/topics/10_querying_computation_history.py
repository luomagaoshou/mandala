"""
主题：查询与分析计算历史
文件：mydemo/topics/10_querying_computation_history.py
描述：本示例详细演示了在函数运行被捕获后，如何使用 ComputationFrame (cf) 
     来查询、分析和可视化存储在 Storage 中的计算历史记录。

核心概念:
1. 将 Storage 视为计算过程的数据库。
2. 使用 ComputationFrame 作为查询构建器。
3. 通过 .upstream(), .downstream(), .expand_all() 探索计算依赖关系。
4. 使用 .eval() 将查询结果提取为 pandas DataFrame 进行分析。
"""
import pandas as pd
from mandala1.imports import Storage, op

# 1. 定义一些简单的操作，并用 @op 装饰
@op
def add(x: int, y: int) -> int:
    """加法"""
    print(f"Executing: add({x}, {y})")
    return x + y

@op
def multiply(a: int, b: int) -> int:
    """乘法"""
    print(f"Executing: multiply({a}, {b})")
    return a * b

@op
def subtract(p: int, q: int) -> int:
    """减法"""
    print(f"Executing: subtract({p}, {q})")
    return p - q

def demonstrate_querying():
    """演示如何查询和分析计算历史"""
    storage = Storage()

    # 2. 运行一些计算来生成历史记录
    print("--- (1) 生成计算历史 ---")
    with storage:
        # 第一次计算
        v1 = add(1, 2)       # v1 = 3
        v2 = multiply(v1, 10)  # v2 = 30
        
        # 第二次独立计算
        v3 = add(5, 10)      # v3 = 15
        
        # 结合之前的计算结果
        final_result = subtract(v2, v3) # final_result = 15

    print("\n--- (2) 查询入门：从一个具体结果开始 ---")
    print("目标：我想知道 `final_result` 是如何计算出来的？")
    
    # .cf(final_result) 从一个具体的值（Ref对象）开始构建查询
    #
    # [修复] 这里我们使用 .expand_back(recursive=True) 来代替 .upstream()。
    # - .upstream() 用于在 *当前* 计算图内进行导航。如果图是断开的，它找不到上游节点。
    # - .expand_back() 会主动查询 Storage，拉取创建当前值的上游调用和输入，
    #   从而动态地构建和扩展计算图。recursive=True 确保了它会一直追溯到最源头的输入。
    cf_upstream = storage.cf(final_result).expand_back(recursive=True)

    print("\n计算 `final_result` 的上游图结构:")
    print(cf_upstream)

    print("\n使用 .eval() 将上游计算历史提取为 DataFrame:")
    # .eval() 是获取结果的核心方法，它返回一个 pandas DataFrame
    # 每一行代表一个完整的计算实例
    # 每一列代表计算图中的一个节点（变量或函数）
    upstream_df = cf_upstream.eval()
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
        print(upstream_df)
    
    # 我们也可以将这个计算路径可视化
    svg_path_upstream = 'mydemo/svg/10_upstream_query.svg'
    cf_upstream.draw(verbose=True, path=svg_path_upstream)
    print(f"\n上游计算图已保存到: {svg_path_upstream}")


    print("\n\n--- (3) 进阶查询：从一个操作（函数）开始 ---")
    print("目标：我想查看 `add` 函数的所有历史调用记录。")

    # .cf(add) 从一个操作（Op对象）开始，会选中所有对 `add` 的调用
    cf_add = storage.cf(add)
    
    print("\n`add` 函数的所有调用实例 (以DataFrame格式):")
    # [修复] 为了直接获取一个函数的所有调用记录，最简单、最健壮的方法是使用 .get_func_table()。
    # 它避免了 .eval() 在处理单个、非端到端计算图时的复杂性。
    # 我们首先需要获取函数节点在图中的名称（例如 'add' 或 'add_0'）
    add_func_name = next(iter(cf_add.fnames))
    add_df = cf_add.get_func_table(add_func_name)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
        print(add_df)

    print("\n\n--- (4) 高级查询：探索完整的端到端计算图 ---")
    print("目标：我想了解与 `subtract` 操作相关的完整计算流程。")

    # .expand_all() 会沿着数据流双向探索，直到找到所有相关的计算
    cf_full = storage.cf(subtract).expand_all()

    print("\n与 `subtract` 相关的完整计算图结构:")
    print(cf_full)

    print("\n将完整计算历史提取为 DataFrame:")
    full_df = cf_full.eval()
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
        print(full_df)

    svg_path_full = 'mydemo/svg/10_full_query.svg'
    cf_full.draw(verbose=True, path=svg_path_full)
    print(f"\n完整计算图已保存到: {svg_path_full}")


def main():
    """主函数入口"""
    demonstrate_querying()

if __name__ == '__main__':
    main() 
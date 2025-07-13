"""
文件: op_vs_track_example.py
位置: mydemo/案例/
目的: 深度演示 @op 和 @track 装饰器的区别与协作

场景:
我们有一个核心的计算操作 `process_data`，它的计算成本很高，因此我们希望缓存其结果。
这个操作依赖一个辅助函数 `get_config_value`，该函数负责从某个地方获取一个配置参数。
我们不关心 `get_config_value` 自身的返回值是否被缓存，但我们必须确保如果 `get_config_value` 的实现逻辑变了，
`process_data` 必须重新计算以保证结果的正确性。
"""
from mandala1.imports import Storage, op, track
import time
import os
import pandas as pd

# 模拟一个可能会变动的配置值
# 注意：@track 不会追踪全局变量的变更，但我们会通过修改函数体来模拟逻辑变更
CONFIG_SOURCE = {"value": 10}

@track
def get_config_value() -> int:
    """
    V1: 这是一个被追踪的依赖函数。
    它本身不被缓存，但它的代码变更会 invalidate 依赖它的 @op 函数。
    """
    print("      Executing @track function `get_config_value`...")
    # 假设这里有一些复杂的逻辑，比如读取文件、访问数据库等
    return CONFIG_SOURCE['value']

@op
def process_data(data: list) -> list:
    """
    V1: 这是一个被缓存的操作函数。
    它的执行结果会被记忆。
    """
    print("  Executing @op function `process_data` (costly operation)...")
    multiplier = get_config_value()
    time.sleep(1) # 模拟耗时操作
    return [x * multiplier for x in data]

def run_and_report(storage: Storage, data: list):
    """辅助函数：运行并打印结果，并显示当前的计算历史"""
    print("Running `process_data`...")
    start_time = time.time()
    with storage:
        result = process_data(data)
    end_time = time.time()
    print(f"  Result: {result.obj}, Time taken: {end_time - start_time:.2f}s")

    # 新增: 打印与当前 process_data 函数相关的计算历史
    print("  ComputationFrame for current `process_data` function:")
    # 为当前绑定到 `process_data` 变量的 @op 函数创建一个 ComputationFrame
    cf = storage.cf(process_data)
    
    if not cf.fnames:
        print("    No history recorded for this function version yet.")
    else:
        # 获取函数在计算图内部的名称
        func_name = next(iter(cf.fnames))
        # .get_func_table() 是一个便捷方法，用于获取特定函数的所有调用记录
        history_df = cf.get_func_table(func_name)
        with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 200):
            # 打印DataFrame，展示输入(data)和输出(return)
            print(history_df)

def main():
    storage = Storage()
    
    input_data = [1, 2, 3]

    print("--- 1. 首次运行 ---")
    # @op 和 @track 函数都会执行，因为没有缓存
    run_and_report(storage, input_data)

    print("\n--- 2. 再次运行 (无任何变更) ---")
    # @op 函数将命中缓存，其函数体和它依赖的 @track 函数都不会执行
    run_and_report(storage, input_data)

    # ======================================================
    # 模拟代码变更
    # ======================================================
    print("\n--- 3. 修改 @track 函数的实现 ---")
    
    @track
    def get_config_value_v2() -> int:
        """V2: 修改了实现逻辑"""
        print("      Executing @track function `get_config_value` (V2)...")
        return CONFIG_SOURCE['value'] + 5 # 逻辑变更！
    
    # 在 Python 中，我们需要将新函数赋值给旧名称来模拟文件修改
    global get_config_value
    get_config_value = get_config_value_v2
    
    # 因为 @op (process_data) 依赖的 @track (get_config_value) 的源码哈希变了，
    # 所以 @op 的缓存失效，两者都会重新执行。
    run_and_report(storage, input_data)
    
    print("\n--- 4. 再次运行 (无任何变更) ---")
    # 现在 V2 的组合被缓存了，所以再次命中缓存
    run_and_report(storage, input_data)

    print("\n--- 5. 仅修改 @op 函数自身 ---")
    @op
    def process_data_v2(data: list) -> list:
        """V2: 自身的逻辑也发生改变"""
        print("  Executing @op function `process_data` (V2)...")
        multiplier = get_config_value()
        time.sleep(1)
        return [x + multiplier for x in data] # 逻辑从乘法变为加法
    
    global process_data
    process_data = process_data_v2

    # 因为 @op (process_data) 自身的源码哈希变了，缓存失效，重新执行
    run_and_report(storage, input_data)

    print("\n--- 6. 仅改变输入参数 ---")
    new_input_data = [10, 20, 30]
    # 函数代码 (process_data_v2) 和依赖代码 (get_config_value_v2) 都没变，
    # 但输入参数从 [1, 2, 3] 变为了 [10, 20, 30]，
    # 这同样会导致缓存未命中，函数会重新执行。
    run_and_report(storage, new_input_data)

    print("\n--- 7. 关于 ComputationFrame 的重要说明 ---")
    print("""
    Q: ComputationFrame (cf) 能否修改或删除旧的计算节点来强制重新执行？

    A: 不能。这是一个核心设计理念。

    1.  CF 是一个只读的查询工具: 它的唯一目的是查询、探索和分析
        已经存在于 Storage 中的计算历史。它不能以任何方式修改历史记录。
        你找不到像 cf.delete_node() 或 storage.delete_call() 这样的方法。

    2.  重新执行由内容决定: `mandala` 的世界里，是否重新计算完全由
        "内容"决定。强制重新执行的唯一方法是改变内容，包括：
        - 修改 @op 函数自身的代码。
        - 修改其依赖的任何 @track 函数的代码。
        - 改变传入的参数值。

    3.  为什么不能手动删除？手动删除节点会破坏计算图的完整性和可追溯性，
        这违背了 `mandala` 确保计算过程可复现的核心目标。缓存的有效性
        必须由框架根据代码和数据的版本来自动管理，而不是手动干预。
    """)

    print("\n--- 8. ComputationFrame 的高级操作：复制、遍历与组合 ---")
    
    # 8.1 复制 ComputationFrame
    print("\n8.1 复制 ComputationFrame:")
    cf_current = storage.cf(process_data)
    cf_copy = cf_current.copy()
    print(f"  原始 CF: {cf_current}")
    print(f"  复制的 CF: {cf_copy}")
    print(f"  是否为同一对象: {cf_current is cf_copy}")
    
    # 8.2 遍历 ComputationFrame 的内部结构
    print("\n8.2 遍历 ComputationFrame 的内部结构:")
    print(f"  函数名称集合 (fnames): {cf_current.fnames}")
    print(f"  变量名称集合 (vnames): {cf_current.vnames}")
    print(f"  所有节点名称: {cf_current.fnames | cf_current.vnames}")
    
    # 尝试访问内部图结构
    if hasattr(cf_current, 'graph'):
        print(f"  内部图节点数: {len(cf_current.graph.nodes())}")
        print(f"  内部图边数: {len(cf_current.graph.edges())}")
        print("  图中的节点:")
        for i, node in enumerate(cf_current.graph.nodes()):
            if i < 5:  # 只显示前5个节点
                print(f"    {node}")
            elif i == 5:
                print(f"    ... 还有 {len(cf_current.graph.nodes()) - 5} 个节点")
                break
    
    # 8.3 创建多个不同的 ComputationFrame 并组合
    print("\n8.3 组合多个 ComputationFrame:")
    
    # 为了演示组合，我们创建一个新的 @op 函数
    @op
    def helper_function(x: int) -> int:
        """一个辅助函数，用于演示 CF 组合"""
        return x * 2
    
    # 执行这个新函数以产生历史记录
    with storage:
        helper_result = helper_function(42)
    
    # 获取新函数的 ComputationFrame
    cf_helper = storage.cf(helper_function)
    
    print(f"  process_data 的 CF: {cf_current}")
    print(f"  helper_function 的 CF: {cf_helper}")
    
    # 组合两个 ComputationFrame
    try:
        cf_combined = cf_current.union(cf_helper)
        print(f"  组合后的 CF: {cf_combined}")
        print(f"  组合后的函数名称: {cf_combined.fnames}")
        print(f"  组合后的变量名称: {cf_combined.vnames}")
    except Exception as e:
        print(f"  组合操作失败: {e}")
        print("  注意: 只有相关的 CF 才能成功组合")
    
    # 8.4 分析 ComputationFrame 的信息
    print("\n8.4 分析 ComputationFrame 的详细信息:")
    
    # 获取完整的计算历史
    try:
        full_df = cf_current.eval()
        print(f"  完整计算历史的形状: {full_df.shape}")
        print("  计算历史的列名:")
        for col in full_df.columns:
            print(f"    {col}")
        
        # 分析不同版本的函数调用
        if not full_df.empty:
            print(f"  总共记录了 {len(full_df)} 次完整的计算路径")
            
            # 如果有多行，说明有多个不同的计算实例
            if len(full_df) > 1:
                print("  不同计算实例的输入参数:")
                for i, row in full_df.iterrows():
                    # 尝试找到输入参数列
                    input_cols = [col for col in full_df.columns if 'data' in col.lower()]
                    if input_cols:
                        print(f"    实例 {i+1}: {row[input_cols[0]]}")
    except Exception as e:
        print(f"  分析失败: {e}")
    
    # 8.5 探索 ComputationFrame 的查询能力
    print("\n8.5 ComputationFrame 的查询扩展:")
    
    try:
        # 向上游扩展：找到创建当前结果的所有依赖
        cf_upstream = cf_current.expand_back(recursive=True)
        print(f"  向上游扩展后: {cf_upstream}")
        print(f"  上游函数名称: {cf_upstream.fnames}")
        
        # 向下游扩展：找到使用当前结果的所有计算
        cf_downstream = cf_current.expand_forward(recursive=True)
        print(f"  向下游扩展后: {cf_downstream}")
        
        # 全方向扩展：找到所有相关的计算
        cf_all = cf_current.expand_all()
        print(f"  全方向扩展后: {cf_all}")
        
    except Exception as e:
        print(f"  查询扩展失败: {e}")
        print("  注意: 某些扩展操作可能需要特定的图结构")

    print("\n--- 9. 高级操作：修改入参并替换计算节点 ---")
    
    # 9.1 分析当前计算历史的状态
    print("\n9.1 当前计算历史状态分析:")
    cf_before = storage.cf(process_data)
    
    try:
        # 获取当前所有的计算记录
        current_df = cf_before.eval()
        print(f"  当前计算历史记录数: {len(current_df)}")
        print("  当前记录的详细信息:")
        with pd.option_context('display.max_columns', None, 'display.width', 300):
            print(current_df)
    except Exception as e:
        print(f"  获取当前状态失败: {e}")
    
    # 9.2 策略一：通过版本控制强制节点替换
    print("\n9.2 策略一：通过版本控制实现节点替换")
    
    # 创建一个带版本标识的新函数
    @op
    def process_data_v3(data: list, version_id: str = "v3") -> list:
        """
        V3: 带版本标识的函数，通过改变 version_id 来强制重新计算
        这样可以实现对特定输入的"节点替换"效果
        """
        print(f"  Executing @op function `process_data_v3` with version {version_id}...")
        multiplier = get_config_value()
        time.sleep(0.5)  # 减少等待时间
        # 新的计算逻辑：既有加法又有乘法
        return [x * multiplier + x for x in data]
    
    # 使用新函数执行相同的输入，但强制重新计算
    print("  使用新版本函数处理相同输入 [1, 2, 3]:")
    with storage:
        new_result = process_data_v3([1, 2, 3], version_id="v3_replacement")
    print(f"  新结果: {new_result.obj}")
    
    # 9.3 策略二：通过存储层面的操作实现节点管理
    print("\n9.3 策略二：存储层面的节点管理")
    
    # 获取存储中的所有调用记录
    try:
        # 访问底层存储来查看所有记录
        print("  当前存储中的函数调用记录:")
        
        # 创建一个查询来获取所有相关的调用
        all_calls_cf = storage.cf(process_data_v3)
        if all_calls_cf.fnames:
            func_name = next(iter(all_calls_cf.fnames))
            calls_df = all_calls_cf.get_func_table(func_name)
            print(f"  process_data_v3 的调用记录:")
            with pd.option_context('display.max_columns', None, 'display.width', 300):
                print(calls_df)
    except Exception as e:
        print(f"  获取存储记录失败: {e}")
    
    # 9.4 策略三：计算图重构与节点替换
    print("\n9.4 策略三：计算图重构实现节点替换")
    
    # 定义一个可以"覆盖"旧计算的函数
    @op
    def replaceable_computation(data: list, replacement_flag: bool = False) -> list:
        """
        可替换的计算函数：通过 replacement_flag 来控制是否是替换操作
        """
        if replacement_flag:
            print(f"  执行替换计算，输入: {data}")
            multiplier = get_config_value()
            # 替换逻辑：完全不同的计算方式
            return [x ** 2 + multiplier for x in data]
        else:
            print(f"  执行原始计算，输入: {data}")
            multiplier = get_config_value()
            return [x * multiplier for x in data]
    
    # 首先执行原始计算
    print("  执行原始计算:")
    with storage:
        original_result = replaceable_computation([1, 2, 3], replacement_flag=False)
    print(f"  原始结果: {original_result.obj}")
    
    # 然后执行替换计算（相同输入，不同逻辑）
    print("  执行替换计算（相同输入，不同逻辑）:")
    with storage:
        replaced_result = replaceable_computation([1, 2, 3], replacement_flag=True)
    print(f"  替换结果: {replaced_result.obj}")
    
    # 分析替换后的计算历史
    print("  替换后的计算历史:")
    cf_replaceable = storage.cf(replaceable_computation)
    if cf_replaceable.fnames:
        func_name = next(iter(cf_replaceable.fnames))
        replaceable_df = cf_replaceable.get_func_table(func_name)
        print(f"  replaceable_computation 的所有调用:")
        with pd.option_context('display.max_columns', None, 'display.width', 300):
            print(replaceable_df)
    
    # 9.5 策略四：通过参数哈希实现精确节点替换
    print("\n9.5 策略四：通过参数哈希实现精确节点替换")
    
    import hashlib
    
    def get_param_hash(data: list) -> str:
        """为输入参数生成唯一哈希"""
        return hashlib.md5(str(data).encode()).hexdigest()[:8]
    
    @op
    def hash_based_computation(data: list, param_hash: str = None) -> list:
        """
        基于参数哈希的计算函数
        通过改变 param_hash 可以强制对相同输入进行重新计算
        """
        if param_hash is None:
            param_hash = get_param_hash(data)
        
        print(f"  执行哈希计算，输入: {data}, 哈希: {param_hash}")
        multiplier = get_config_value()
        return [x * multiplier * len(param_hash) for x in data]
    
    # 第一次计算
    print("  第一次计算:")
    with storage:
        first_hash_result = hash_based_computation([1, 2, 3])
    print(f"  第一次结果: {first_hash_result.obj}")
    
    # 强制替换：使用不同的哈希值
    print("  强制替换（使用不同哈希）:")
    with storage:
        replaced_hash_result = hash_based_computation([1, 2, 3], param_hash="replaced")
    print(f"  替换后结果: {replaced_hash_result.obj}")
    
    # 分析哈希计算的历史
    print("  哈希计算的历史:")
    cf_hash = storage.cf(hash_based_computation)
    if cf_hash.fnames:
        func_name = next(iter(cf_hash.fnames))
        hash_df = cf_hash.get_func_table(func_name)
        print(f"  hash_based_computation 的所有调用:")
        with pd.option_context('display.max_columns', None, 'display.width', 300):
            print(hash_df)
    
    # 9.6 总结和最佳实践
    print("\n9.6 节点替换的总结和最佳实践:")
    print("""
    节点替换的四种策略总结:
    
    1. 版本控制策略:
       - 通过添加版本参数来区分不同的计算
       - 优点: 清晰、可追溯
       - 缺点: 需要修改函数签名
    
    2. 存储层面操作:
       - 直接在存储层面管理计算记录
       - 优点: 不需要修改业务逻辑
       - 缺点: 需要深入了解存储结构
    
    3. 计算图重构:
       - 通过标志位控制计算逻辑
       - 优点: 灵活、可以实现复杂的替换逻辑
       - 缺点: 函数逻辑可能变得复杂
    
    4. 参数哈希策略:
       - 通过哈希值来强制重新计算
       - 优点: 精确控制、不影响原有逻辑
       - 缺点: 需要额外的哈希管理
    
    最佳实践建议:
    - 对于开发阶段: 使用版本控制策略
    - 对于生产环境: 使用参数哈希策略
    - 对于复杂场景: 组合使用多种策略
    """)


if __name__ == "__main__":
    main() 
"""
文档来源：
- 文件：docs_source/topics/03_cf.ipynb
- 主题：使用计算框架查询存储
- 描述：展示了如何使用 ComputationFrame 探索和查询存储的数据
- 关键概念：
  1. 计算框架：存储查询的高级数据结构
  2. 框架扩展：添加计算上下文
  3. 框架组合：合并和限制计算图
  4. 数据框转换：提取关系数据
- 相关文档：
  - docs/docs/topics/03_cf.md
  - docs/docs/topics/06_advanced_cf.md

本示例展示了计算框架的基本用法：
1. 创建计算框架
2. 扩展和探索计算历史
3. 组合和限制计算图
4. 转换为数据框进行分析
"""

import numpy as np
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from mandala.imports import Storage, op

# 设置随机种子以确保结果可重现
np.random.seed(0)

@op
def generate_dataset(random_seed: int = 42):
    """生成数字识别数据集
    
    参数:
        random_seed: 随机种子
    返回:
        训练集和测试集的特征和标签
    """
    X, y = load_digits(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_seed)
    return X_train, X_test, y_train, y_test

@op
def train_model(X_train, y_train, n_estimators: int):
    """训练随机森林模型
    
    参数:
        X_train: 训练特征
        y_train: 训练标签
        n_estimators: 树的数量
    返回:
        模型和训练集准确率
    """
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=2)
    model.fit(X_train, y_train)
    return model, round(model.score(X_train, y_train), 2)

@op
def eval_model(model, X_test, y_test):
    """评估模型性能
    
    参数:
        model: 训练好的模型
        X_test: 测试特征
        y_test: 测试标签
    返回:
        测试集准确率
    """
    return round(model.score(X_test, y_test), 2)

def demonstrate_cf_basics():
    """演示计算框架的基本用法"""
    storage = Storage()
    
    print("1. 运行机器学习流水线:")
    with storage:
        # 生成数据集
        X_train, X_test, y_train, y_test = generate_dataset()
        # 尝试不同数量的树
        for n_estimators in [10, 20, 40, 80]:
            model, train_acc = train_model(X_train, y_train, n_estimators=n_estimators)
            # 条件执行：只评估训练准确率大于0.8的模型
            if storage.unwrap(train_acc) > 0.8:
                test_acc = eval_model(model, X_test, y_test)
    
    print("\n2. 从单个引用创建计算框架:")
    # 从测试准确率创建计算框架
    cf = storage.cf(test_acc)
    print("- 初始计算框架:")
    print(cf)
    
    print("\n3. 扩展计算历史:")
    # 递归扩展计算历史
    cf.expand_back(inplace=True, recursive=True)
    print("- 扩展后的计算框架:")
    print(cf)
    
    print("\n4. 查看变量值:")
    # 解包并显示主要变量的值
    vars_to_show = ['n_estimators', 'train_acc', 'test_acc']
    values = {vname: storage.unwrap(refs) 
             for vname, refs in cf.refs_by_var().items()
             if vname in vars_to_show}
    print("- 变量值:")
    for var, val in values.items():
        print(f"  {var}: {val}")
    
    print("\n5. 从操作创建计算框架:")
    # 从训练模型操作创建计算框架
    cf_train = storage.cf(train_model)
    print("- 训练模型的计算框架:")
    print(cf_train)
    
    print("\n6. 转换为数据框:")
    # 显示训练模型的记忆化表
    df = cf_train.df()
    print("- 训练模型的记忆化表:")
    print(df)

def main():
    print("演示计算框架的基本用法...")
    demonstrate_cf_basics()

if __name__ == '__main__':
    main() 
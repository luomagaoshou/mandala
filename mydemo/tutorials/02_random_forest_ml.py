"""
文档来源：
- 文件：docs_source/tutorials/02_ml.ipynb
- 主题：随机森林机器学习项目（Random Forest ML Project）
- 描述：展示了如何使用 mandala 构建和管理机器学习项目
- 关键概念：
  1. 可查询的记忆化：自动加载和跳过过去的计算
  2. 增量迭代：在现有代码基础上添加新的逻辑
  3. 计算图分析：探索结果之间的依赖关系
  4. 版本兼容性：处理代码变更和参数更新
- 相关文档：
  - docs/docs/tutorials/02_ml.md
  - docs/docs/blog/01_cf.md

本示例展示了如何使用 mandala 管理机器学习项目：
1. 使用记忆化装饰器自动保存结果
2. 在现有代码上迭代和实验
3. 分析计算历史和依赖关系
4. 处理代码和参数的变更
"""

from typing import Tuple
import numpy as np
import pandas as pd
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from mandala.imports import Storage, op, NewArgDefault

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
    print(f"生成数据集...")
    X, y = load_digits(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_seed)
    return X_train, X_test, y_train, y_test

@op
def train_model(X_train, y_train, n_estimators=NewArgDefault(1)):
    """训练随机森林模型
    
    参数:
        X_train: 训练特征
        y_train: 训练标签
        n_estimators: 树的数量
    返回:
        模型和训练集准确率
    """
    print(f"训练模型...")
    model = RandomForestClassifier(n_estimators=n_estimators)
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
    print(f"评估模型...")
    return round(model.score(X_test, y_test), 2)

def main():
    # 初始化内存存储
    storage = Storage()
    
    print("运行基本流水线...")
    with storage:
        # 1. 使用默认设置运行一次
        X_train, X_test, y_train, y_test = generate_dataset()
        model, train_acc = train_model(X_train, y_train)
        test_acc = eval_model(model, X_test, y_test)
        print(f"训练准确率: {train_acc}\n测试准确率: {test_acc}")
        
        print("\n尝试不同数量的树...")
        # 2. 尝试不同数量的决策树
        for n_estimators in [1, 10, 100]:
            print(f"\n使用 {n_estimators} 棵树:")
            model, train_acc = train_model(X_train, y_train, n_estimators=n_estimators)
            test_acc = eval_model(model, X_test, y_test)
            print(f"    训练准确率: {train_acc}")
            print(f"    测试准确率: {test_acc}")
    
    # 3. 分析计算图
    print("\n分析计算图...")
    cf = storage.cf(eval_model)
    cf = cf.expand_back(recursive=True)
    
    # 转换为数据框并显示统计信息
    df = cf.df()
    print("\n计算历史统计:")
    print(f"总计算步骤: {len(df)}")
    print(f"计算图中的操作: {', '.join(col for col in df.columns if not col.startswith('_'))}")

if __name__ == '__main__':
    main() 
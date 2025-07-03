"""
文档来源：
- 文件：docs_source/topics/04_versions.ipynb
- 主题：版本管理
- 描述：展示了如何管理和追踪代码变更
- 关键概念：
  1. 版本定义：函数代码和全局变量的集合
  2. 变更分类：破坏性和非破坏性变更
  3. 依赖追踪：自动识别和管理依赖
  4. 版本历史：基于内容的版本控制
- 相关文档：
  - docs/docs/topics/04_versions.md
  - docs/docs/blog/02_deps.md

本示例展示了版本管理的基本功能：
1. 检查和分析版本
2. 处理代码变更
3. 管理依赖关系
4. 追踪版本历史
"""

from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from mandala.imports import Storage, op, track
from mandala.utils import mock_input
from unittest.mock import patch

# 全局变量，用于演示依赖变更
N_CLASS = 10

@track
def scale_data(X):
    """数据标准化 V1：只进行中心化
    
    参数:
        X: 输入特征矩阵
    返回:
        标准化后的特征矩阵
    """
    return StandardScaler(with_mean=True, with_std=False).fit_transform(X)

@op
def load_data():
    """加载数字识别数据集
    
    返回:
        特征矩阵和标签
    """
    X, y = load_digits(n_class=N_CLASS, return_X_y=True)
    return X, y

@op
def train_model(X, y, scale=False):
    """训练逻辑回归模型
    
    参数:
        X: 特征矩阵
        y: 标签
        scale: 是否进行标准化
    返回:
        训练好的模型
    """
    if scale:
        X = scale_data(X)
    return LogisticRegression(max_iter=1000, solver='liblinear').fit(X, y)

@op
def eval_model(model, X, y, scale=False):
    """评估模型性能 V1：返回原始准确率
    
    参数:
        model: 训练好的模型
        X: 特征矩阵
        y: 标签
        scale: 是否进行标准化
    返回:
        模型准确率
    """
    if scale:
        X = scale_data(X)
    return model.score(X, y)

def demonstrate_version_management():
    """演示版本管理功能"""
    # 声明全局变量
    global N_CLASS, scale_data, eval_model
    
    storage = Storage(deps_path='__main__')
    
    print("1. 运行初始版本:")
    with storage:
        X, y = load_data()
        for scale in [False, True]:
            model = train_model(X, y, scale=scale)
            acc = eval_model(model, X, y, scale=scale)
            print(f"- 使用标准化: {scale}, 准确率: {acc}")
    
    print("\n2. 检查版本信息:")
    versions = storage.versions(train_model)
    print("- train_model 的版本:")
    print(versions)
    
    print("\n3. 模拟代码变更:")
    # 修改全局变量（破坏性变更）
    N_CLASS = 5
    print("- 修改 N_CLASS 为", N_CLASS)
    
    # 修改 scale_data 函数（破坏性变更）
    @track
    def new_scale_data(X):
        """数据标准化 V2：进行中心化和标准化"""
        return StandardScaler(with_mean=True, with_std=True).fit_transform(X)
    scale_data = new_scale_data
    print("- 更新 scale_data 函数")
    
    # 修改 eval_model 函数（非破坏性变更）
    @op
    def new_eval_model(model, X, y, scale=False):
        """评估模型性能 V2：返回四舍五入后的准确率"""
        if scale:
            X = scale_data(X)
        return round(model.score(X, y), 2)
    eval_model = new_eval_model
    print("- 更新 eval_model 函数")
    
    print("\n4. 运行更新后的代码:")
    # 模拟用户输入：y（N_CLASS 变更）, n（eval_model 变更）, y（scale_data 变更）
    answers = ['y', 'n', 'y']
    with patch('builtins.input', mock_input(answers)):
        with storage:
            X, y = load_data()
            for scale in [False, True]:
                model = train_model(X, y, scale=scale)
                acc = eval_model(model, X, y, scale=scale)
                print(f"- 使用标准化: {scale}, 准确率: {acc}")
    
    print("\n5. 分析计算历史:")
    cf = storage.cf(eval_model).expand_all()
    print("- 计算框架结构:")
    print(cf)
    
    print("\n6. 检查更新后的版本:")
    versions = storage.versions(eval_model)
    print("- eval_model 的版本:")
    print(versions)

def main():
    print("演示版本管理功能...")
    demonstrate_version_management()

if __name__ == '__main__':
    main()

"""
文档来源：
- 文件：docs_source/topics/04_versions.ipynb
- 主题：更改 @op 和管理版本
- 描述：展示了如何处理代码变更和版本管理
- 关键概念：
  1. 自动依赖追踪：记录每个调用的依赖关系
  2. 变更分类：区分破坏性和非破坏性变更
  3. 基于内容的版本控制：代码状态决定版本
  4. 版本检查：检查和管理版本变化
- 相关文档：
  - docs/docs/topics/04_versions.md
  - docs/docs/blog/02_deps.md

本示例展示了版本管理的基本功能：
1. 启用和配置版本控制
2. 使用 @track 装饰器追踪依赖
3. 检查和管理版本变更
4. 处理破坏性和非破坏性变更
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
    """数据标准化
    
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
    """评估模型性能
    
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
    
    # 创建存储并启用版本控制
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
    # 修改全局变量
    N_CLASS = 5
    
    # 修改 scale_data 函数（破坏性变更）
    @track
    def new_scale_data(X):
        return StandardScaler(with_mean=True, with_std=True).fit_transform(X)
    scale_data = new_scale_data
    
    # 修改 eval_model 函数（非破坏性变更）
    @op
    def new_eval_model(model, X, y, scale=False):
        if scale:
            X = scale_data(X)
        return round(model.score(X, y), 2)
    eval_model = new_eval_model
    
    print("4. 运行更新后的代码:")
    # 模拟用户输入：y（N_CLASS 变更）, n（eval_model 变更）, y（scale_data 变更）
    answers = ['y', 'n', 'y']
    with patch('builtins.input', mock_input(answers)):
        with storage:
            X, y = load_data()
            for scale in [False, True]:
                model = train_model(X, y, scale=scale)
                acc = eval_model(model, X, y, scale=scale)
                print(f"- 使用标准化: {scale}, 准确率: {acc}")

def main():
    print("演示版本管理功能...")
    demonstrate_version_management()

if __name__ == '__main__':
    main() 
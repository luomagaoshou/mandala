"""
文档来源：
- 文件：docs_source/topics/04_versions.ipynb
- 主题：版本变更（Version Changes）
- 描述：展示了 mandala 中如何处理和管理代码版本变更
- 关键概念：
  1. 版本变更类型：破坏性vs非破坏性
  2. 版本检测：自动识别代码变更
  3. 版本迁移：处理不兼容的变更
  4. 版本历史：追踪和查询历史版本
- 相关文档：
  - docs/docs/topics/04_versions.md
  - docs/docs/blog/02_deps.md

本示例展示了如何处理 mandala 中的版本变更。
主要功能包括：
1. 识别不同类型的版本变更
2. 自动检测代码变更
3. 处理版本迁移
4. 管理版本历史
"""

import os
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from mandala.imports import Storage, op, track
from mandala.utils import mock_input
from unittest.mock import patch

# 配置存储路径
DB_PATH = 'mandala_storage/versions_demo.db'
os.makedirs('mandala_storage', exist_ok=True)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# 创建存储实例，启用版本管理
storage = Storage(
    db_path=DB_PATH,
    deps_path='__main__',  # 只追踪当前会话中定义的函数
)

# 设置随机种子以保证结果可重现
np.random.seed(0)

# 全局变量，用于演示全局依赖的变化
N_CLASS = 10

@track  # 追踪非记忆化函数
def scale_data_v1(X):
    """数据标准化函数 V1：只进行中心化。"""
    print("使用 scale_data V1")
    return StandardScaler(with_mean=True, with_std=False).fit_transform(X)

@track  # 追踪非记忆化函数
def scale_data_v2(X):
    """数据标准化函数 V2：进行中心化和标准化。"""
    print("使用 scale_data V2")
    return StandardScaler(with_mean=True, with_std=True).fit_transform(X)

# 当前使用的 scale_data 函数
scale_data = scale_data_v1

@op
def load_data():
    """加载数据集，依赖全局变量 N_CLASS。"""
    print(f"加载数据集 (N_CLASS={N_CLASS})")
    X, y = load_digits(n_class=N_CLASS, return_X_y=True)
    return X, y

@op
def train_model(X, y, scale=False):
    """
    训练模型，可选是否进行数据标准化。
    如果 scale=True，将依赖 scale_data 函数。
    """
    print(f"训练模型 (scale={scale})")
    if scale:
        X = scale_data(X)
    return LogisticRegression(max_iter=1000, solver='liblinear').fit(X, y)

@op
def eval_model_v1(model, X, y, scale=False):
    """
    评估模型 V1：返回原始准确率。
    如果 scale=True，将依赖 scale_data 函数。
    """
    print(f"评估模型 V1 (scale={scale})")
    if scale:
        X = scale_data(X)
    return model.score(X, y)

@op
def eval_model_v2(model, X, y, scale=False):
    """
    评估模型 V2：返回四舍五入后的准确率。
    如果 scale=True，将依赖 scale_data 函数。
    """
    print(f"评估模型 V2 (scale={scale})")
    if scale:
        X = scale_data(X)
    return round(model.score(X, y), 2)

# 当前使用的 eval_model 函数
eval_model = eval_model_v1

def run_experiment_v1():
    """运行第一版实验。"""
    print("1. 运行初始版本")
    print("-" * 50)
    
    with storage:
        # 加载数据
        X, y = load_data()
        
        # 使用不同的数据预处理方式训练和评估模型
        for scale in [False, True]:
            model = train_model(X, y, scale=scale)
            acc = eval_model(model, X, y, scale=scale)
            print(f"准确率 (scale={scale}): {acc}")
    
    # 展示版本信息
    print("\n函数版本信息:")
    print("train_model 的版本:")
    print(storage.versions(train_model))
    print("\neval_model 的版本:")
    print(storage.versions(eval_model))

def run_experiment_v2():
    """
    运行第二版实验，包含以下变更：
    1. 修改全局变量 N_CLASS（破坏性变更）
    2. 修改 scale_data 函数（破坏性变更）
    3. 修改 eval_model 函数（非破坏性变更）
    """
    print("\n2. 运行修改后的版本")
    print("-" * 50)
    
    # 修改全局变量
    global N_CLASS, scale_data, eval_model
    N_CLASS = 5
    print(f"修改 N_CLASS 为 {N_CLASS}")
    
    # 切换到新版本的函数
    scale_data = scale_data_v2
    print("切换到 scale_data V2")
    
    eval_model = eval_model_v2
    print("切换到 eval_model V2")
    
    # 模拟用户输入，处理变更提示
    # y: N_CLASS 的变更是破坏性的
    # n: eval_model 的变更是非破坏性的
    # y: scale_data 的变更是破坏性的
    answers = ['y', 'n', 'y']
    
    with patch('builtins.input', mock_input(answers)):
        with storage:
            # 加载数据
            X, y = load_data()
            
            # 使用不同的数据预处理方式训练和评估模型
            for scale in [False, True]:
                model = train_model(X, y, scale=scale)
                acc = eval_model(model, X, y, scale=scale)
                print(f"准确率 (scale={scale}): {acc}")
    
    # 展示版本信息
    print("\n更新后的函数版本信息:")
    print("train_model 的版本:")
    print(storage.versions(train_model))
    print("\neval_model 的版本:")
    print(storage.versions(eval_model))
    
    # 创建计算框架来分析版本关系
    print("\n创建计算框架分析版本关系:")
    cf = storage.cf(eval_model).expand_all()
    print(cf)

def main():
    """主函数，按顺序运行两个版本的实验。"""
    run_experiment_v1()
    run_experiment_v2()

if __name__ == "__main__":
    main() 
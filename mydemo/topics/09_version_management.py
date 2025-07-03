"""
文档来源：
- 文件：docs_source/topics/04_versions.ipynb
- 主题：版本管理（Version Management）
- 描述：展示了 mandala 的版本管理功能，包括依赖追踪和版本检测
- 关键概念：
  1. 版本配置：启用和管理版本
  2. 依赖追踪：检测代码变更影响
  3. 版本检测：识别破坏性和非破坏性变更
  4. 机器学习示例：数字识别模型版本管理
- 相关文档：
  - docs/docs/topics/04_versions.md
  - docs/docs/tutorials/02_ml.md

本示例展示了如何使用 mandala 的版本管理功能。
主要功能包括：
1. 版本管理的配置和启用
2. 依赖追踪和版本检测
3. 处理破坏性和非破坏性变更
4. 机器学习模型的版本管理
"""

import os
import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from mandala.imports import Storage, op, track, MList, MDict
from typing import Tuple, Any

# 配置存储路径
DB_PATH = "mandala_storage/version_demo.db"
os.makedirs("mandala_storage", exist_ok=True)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# 创建存储实例，启用版本管理
storage = Storage(
    db_path=DB_PATH,
    deps_path="__main__"  # 只追踪当前模块中定义的函数
)

# 设置随机种子以保证结果可重现
np.random.seed(0)

# 全局变量，用于演示版本变化
N_CLASS = 10

# 1. 基础数据处理函数
@track  # 追踪非记忆化函数
def scale_data(X):
    """标准化数据。"""
    print("标准化数据...")
    return StandardScaler(with_mean=True, with_std=False).fit_transform(X)

@op
def load_data() -> Tuple[Any, Any]:
    """加载数字数据集。"""
    print(f"加载{N_CLASS}个类别的数据...")
    X, y = load_digits(n_class=N_CLASS, return_X_y=True)
    print(f"数据形状: {X.shape}, 标签形状: {y.shape}")
    return X, y

@op
def train_model(X: Any, y: Any, scale: bool = False) -> Any:
    """训练逻辑回归模型。"""
    print("训练模型...")
    if scale:
        print("使用标准化数据")
        X = scale_data(X)
    model = LogisticRegression(max_iter=1000, solver="liblinear")
    model.fit(X, y)
    print("模型训练完成")
    return model

@op
def eval_model(model: Any, X: Any, y: Any, scale: bool = False) -> float:
    """评估模型性能。"""
    print("评估模型...")
    if scale:
        print("使用标准化数据")
        X = scale_data(X)
    score = model.score(X, y)
    print(f"模型准确率: {score:.4f}")
    return score

def demo_initial_version():
    """演示初始版本的功能。"""
    print("\n1. 初始版本测试")
    print("-" * 50)
    
    with storage:
        # 加载数据
        X, y = load_data()
        
        # 训练和评估两个模型（有无标准化）
        results = {}
        for scale in [False, True]:
            model = train_model(X, y, scale=scale)
            acc = eval_model(model, X, y, scale=scale)
            # 直接打印结果
            print(f"\n标准化={scale}的结果:")
            print(f"准确率: {acc}")
    
    # 查看版本信息
    print("\n函数版本信息:")
    print("\ntrain_model 的版本:")
    print(storage.versions(train_model))
    print("\neval_model 的版本:")
    print(storage.versions(eval_model))

def demo_version_changes():
    """演示版本变化的影响。"""
    print("\n2. 版本变化测试")
    print("-" * 50)
    
    # 修改全局变量
    global N_CLASS
    N_CLASS = 5
    print(f"修改类别数为: {N_CLASS}")
    
    # 修改 scale_data 函数（破坏性变更）
    @track
    def scale_data(X):
        """修改后的标准化函数。"""
        print("使用修改后的标准化方法...")
        return StandardScaler(with_mean=True, with_std=True).fit_transform(X)
    
    # 修改 eval_model 函数（非破坏性变更）
    @op
    def eval_model(model: Any, X: Any, y: Any, scale: bool = False) -> float:
        """修改后的评估函数（仅格式变化）。"""
        print("评估模型...")
        if scale:
            print("使用标准化数据")
            X = scale_data(X)
        score = round(model.score(X, y), 4)
        print(f"模型准确率: {score:.4f}")
        return score
    
    with storage:
        # 重新运行相同的实验
        X, y = load_data()
        for scale in [False, True]:
            model = train_model(X, y, scale=scale)
            acc = eval_model(model, X, y, scale=scale)
            # 直接打印结果
            print(f"\n标准化={scale}的结果:")
            print(f"准确率: {acc}")
    
    # 查看更新后的版本信息
    print("\n更新后的函数版本信息:")
    print("\ntrain_model 的版本:")
    print(storage.versions(train_model))
    print("\neval_model 的版本:")
    print(storage.versions(eval_model))

def main():
    """运行所有示例。"""
    print("开始运行版本管理示例...")
    demo_initial_version()
    demo_version_changes()
    print("\n示例运行完成。")

if __name__ == "__main__":
    main()

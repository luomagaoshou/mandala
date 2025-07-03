"""
文档来源：
- 文件：docs_source/tutorials/02_ml.ipynb
- 主题：机器学习流水线（Machine Learning Pipeline）
- 描述：展示了如何使用 mandala 构建和分析机器学习实验流水线
- 关键概念：
  1. 实验追踪：自动记录计算过程
  2. 条件执行：支持复杂的实验流程
  3. 计算图分析：评估模型依赖关系
  4. 性能对比：不同模型和预处理的比较
- 相关文档：
  - docs/docs/tutorials/02_ml.md
  - docs/docs/blog/01_cf.md

本示例展示了如何使用 mandala 构建机器学习流水线：
1. 自动记录所有操作和数据流
2. 支持条件执行和复杂模式
3. 提供简单的查询语法
4. 分析变量之间的关系
"""

# 导入必要的库
from mandala1.storage import Storage
from mandala1.model import op
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import numpy as np

# 设置随机种子以确保结果可重现
np.random.seed(42)

@op(output_names=["X", "y"])
def get_data():
    """生成月牙形状的二分类数据集
    
    返回:
        X: 特征矩阵，形状为 (n_samples, 2)
        y: 标签向量，形状为 (n_samples,)
    """
    return make_moons(n_samples=1000, noise=0.3, random_state=42)

@op(output_names=["X_train", "X_test", "y_train", "y_test"])
def get_train_test_split(X, y):
    """将数据集分割为训练集和测试集
    
    参数:
        X: 特征矩阵
        y: 标签向量
    返回:
        X_train, X_test: 训练集和测试集特征
        y_train, y_test: 训练集和测试集标签
    """
    return tuple(train_test_split(X, y, test_size=0.2, random_state=42))

@op(output_names=["X_scaled"])
def scale_data(X):
    """标准化特征
    
    参数:
        X: 输入特征矩阵
    返回:
        X_scaled: 标准化后的特征矩阵
    """
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    return X

@op(output_names=["svc_model"])
def train_svc(X_train, y_train, C: float = 1.0, kernel: str = "linear"):
    """训练支持向量机分类器
    
    参数:
        X_train: 训练特征
        y_train: 训练标签
        C: 正则化参数
        kernel: 核函数类型
    返回:
        svc_model: 训练好的SVC模型
    """
    model = SVC(C=C, kernel=kernel)
    model.fit(X_train, y_train)
    return model

@op(output_names=["rf_model"])
def train_random_forest(X_train, y_train, n_estimators: int = 5, max_depth: int = 5):
    """训练随机森林分类器
    
    参数:
        X_train: 训练特征
        y_train: 训练标签
        n_estimators: 树的数量
        max_depth: 树的最大深度
    返回:
        rf_model: 训练好的随机森林模型
    """
    model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
    model.fit(X_train, y_train)
    return model

@op(output_names=["accuracy"])
def eval_ensemble(model, X_test, y_test):
    """评估模型性能
    
    参数:
        model: 训练好的模型
        X_test: 测试特征
        y_test: 测试标签
    返回:
        accuracy: 测试集准确率
    """
    y_pred = model.predict(X_test)
    return accuracy_score(y_test, y_pred)

def main():
    # 初始化存储
    storage = Storage()
    
    print("开始机器学习实验...")
    
    with storage:
        # 1. 数据准备阶段
        print("\n1. 准备数据...")
        # 对于有无数据标准化的两种情况
        for scale in (True, False):
            X, y = get_data()
            if scale:
                print("   - 使用标准化数据")
                X = scale_data(X=X)
            else:
                print("   - 使用原始数据")
            X_train, X_test, y_train, y_test = get_train_test_split(X=X, y=y)
            
            # 2. 模型训练和评估阶段
            print(f"\n2. 训练和评估模型 (数据{'已' if scale else '未'}标准化)...")
            
            # 训练SVC
            print("   - 训练SVC模型...")
            svc = train_svc(X_train=X_train, y_train=y_train, C=1.0, kernel="rbf")
            svc_acc = eval_ensemble(model=svc, X_test=X_test, y_test=y_test)
            print(f"     SVC准确率: {storage.unwrap(svc_acc):.4f}")
            
            # 训练随机森林
            print("   - 训练随机森林模型...")
            rf = train_random_forest(
                X_train=X_train, 
                y_train=y_train,
                n_estimators=10,
                max_depth=5
            )
            rf_acc = eval_ensemble(model=rf, X_test=X_test, y_test=y_test)
            print(f"     随机森林准确率: {storage.unwrap(rf_acc):.4f}")
    
    # 3. 使用ComputationFrame分析计算图
    print("\n3. 分析计算图...")
    
    # 从eval_ensemble开始创建计算图
    cf = storage.cf(eval_ensemble)
    print("   - 创建了初始ComputationFrame")
    
    # 向后扩展以包含所有相关计算
    cf = cf.expand_back(recursive=True)
    print("   - 扩展了ComputationFrame以包含所有上游计算")
    
    # 将计算图转换为数据框
    df = cf.df()
    print("\n4. 计算图统计:")
    print(f"   - 总计算步骤数: {len(df)}")
    print(f"   - 计算图中的操作: {', '.join(col for col in df.columns if not col.startswith('_'))}")
    
    print("\n实验完成！")

if __name__ == "__main__":
    main() 
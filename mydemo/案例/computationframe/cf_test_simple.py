"""
简化版ComputationFrame测试脚本
验证基本功能是否正常工作
"""

import numpy as np
from mandala1.imports import Storage, op

@op
def 数据预处理(原始数据):
    """数据预处理：清洗和标准化"""
    return [x * 2 for x in 原始数据 if x > 0]

@op
def 特征提取(数据):
    """特征提取：计算统计特征"""
    return {
        '平均值': np.mean(数据),
        '标准差': np.std(数据),
        '最大值': np.max(数据),
        '最小值': np.min(数据)
    }

def main():
    """测试基本功能"""
    storage = Storage()
    
    with storage:
        原始数据 = [1, 2, 3, 4, 5, -1, 0, 6, 7, 8]
        清洗数据 = 数据预处理(原始数据)
        特征 = 特征提取(清洗数据)
        
        print(f"原始数据: {原始数据}")
        print(f"清洗后数据: {storage.unwrap(清洗数据)}")
        print(f"提取特征: {storage.unwrap(特征)}")
    
    # 创建 ComputationFrame
    cf = storage.cf(特征)
    print(f"\n创建ComputationFrame成功！")
    print(f"节点数: {len(cf.nodes)}")
    print(f"变量数: {len(cf.vnames)}")
    print(f"函数数: {len(cf.fnames)}")
    print(f"边数: {len(cf.edges())}")
    
    # 展示基本属性
    print(f"\n图描述:\n{cf.get_graph_desc()}")
    
    return cf

if __name__ == '__main__':
    try:
        final_cf = main()
        print("\n✅ 基本功能测试成功！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 
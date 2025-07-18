"""
文件: cf_simple_demo.py
位置: mydemo/案例/
目的: ComputationFrame 操作的简洁演示版本

这是 cf_node_manipulation_example.py 的简化版本，保留所有核心功能：
1. 计算历史创建和管理
2. ComputationFrame 遍历和分析
3. SVG 可视化生成
4. 节点更新和替换策略
5. 综合分析工作流

特点：更简洁的API，更清晰的输出，更易于理解和使用。
"""

from mandala1.imports import Storage, op, track
import time
import pandas as pd
import hashlib
from pathlib import Path

class CFDemo:
    """ComputationFrame 演示类 - 简洁版本"""
    
    def __init__(self):
        self.storage = Storage()
        self.svg_dir = Path("mydemo/svg")
        self.svg_dir.mkdir(exist_ok=True)
        self._setup_functions()
    
    def _setup_functions(self):
        """设置演示用的函数"""
        @track
        def config_value() -> int:
            return 15
        
        @op
        def compute(data: list, mode: str = "basic") -> list:
            multiplier = config_value()
            if mode == "basic":
                return [x * multiplier for x in data]
            elif mode == "advanced":
                return [x * multiplier + x for x in data]
            else:
                return [x ** 2 + multiplier for x in data]
        
        @op
        def summarize(data: list) -> dict:
            return {"sum": sum(data), "count": len(data), "avg": sum(data)/len(data)}
        
        self.config_value = config_value
        self.compute = compute
        self.summarize = summarize
    
    def create_history(self):
        """创建计算历史"""
        print("📊 创建计算历史...")
        
        with self.storage:
            # 基础计算
            result1 = self.compute([1, 2, 3], mode="basic")
            summary1 = self.summarize(result1)
            
            # 高级计算
            result2 = self.compute([4, 5, 6], mode="advanced")
            summary2 = self.summarize(result2)
            
            # 实验性计算
            result3 = self.compute([7, 8, 9], mode="experimental")
            summary3 = self.summarize(result3)
        
        print(f"✅ 创建了 3 个计算分支")
        return [summary1, summary2, summary3]
    
    def analyze_cf(self, cf, name="ComputationFrame"):
        """分析 ComputationFrame"""
        print(f"\n🔍 分析 {name}:")
        print(f"  函数节点: {len(cf.fnames)} 个")
        print(f"  变量节点: {len(cf.vnames)} 个")
        print(f"  总节点数: {len(cf.fnames | cf.vnames)} 个")
        
        # 显示函数调用统计
        for fname in cf.fnames:
            try:
                table = cf.get_func_table(fname)
                print(f"  📋 {fname}: {len(table)} 次调用")
            except:
                print(f"  ❌ {fname}: 无法获取调用信息")
        
        return {
            "functions": len(cf.fnames),
            "variables": len(cf.vnames),
            "total": len(cf.fnames | cf.vnames)
        }
    
    def generate_svg(self, cf, filename):
        """生成 SVG 可视化"""
        svg_path = self.svg_dir / filename
        try:
            cf.draw(verbose=True, path=str(svg_path))
            print(f"🎨 SVG 已保存: {svg_path.name}")
            return svg_path
        except Exception as e:
            print(f"❌ SVG 生成失败: {e}")
            return None
    
    def update_strategy_1_version(self):
        """策略1: 版本控制更新"""
        print("\n🔄 策略1: 版本控制")
        
        @op
        def compute_v2(data: list, mode: str = "basic", version: str = "v2") -> list:
            multiplier = self.config_value()
            # 增强逻辑: 所有结果都乘以2
            base_result = [x * multiplier for x in data]
            return [x * 2 for x in base_result]
        
        with self.storage:
            new_result = compute_v2([1, 2, 3], version="v2.0")
            new_summary = self.summarize(new_result)
        
        cf = self.storage.cf(compute_v2).expand_all()
        return cf, new_summary
    
    def update_strategy_2_hash(self):
        """策略2: 参数哈希更新"""
        print("\n🔄 策略2: 参数哈希")
        
        @op
        def hash_compute(data: list, hash_id: str = None) -> dict:
            if hash_id is None:
                hash_id = hashlib.md5(str(data).encode()).hexdigest()[:6]
            
            multiplier = self.config_value()
            result = [x * multiplier for x in data]
            
            return {
                "data": result,
                "hash": hash_id,
                "sum": sum(result)
            }
        
        with self.storage:
            # 原始计算
            original = hash_compute([1, 2, 3])
            # 强制更新
            updated = hash_compute([1, 2, 3], hash_id="forced_update")
        
        cf = self.storage.cf(hash_compute).expand_all()
        return cf, [original, updated]
    
    def update_strategy_3_branch(self):
        """策略3: 逻辑分支更新"""
        print("\n🔄 策略3: 逻辑分支")
        
        @op
        def branch_compute(data: list, branch: str = "A") -> dict:
            multiplier = self.config_value()
            
            if branch == "A":
                result = [x * multiplier for x in data]
            elif branch == "B":
                result = [x * multiplier + 10 for x in data]
            else:  # branch == "C"
                result = [x ** 2 + multiplier for x in data]
            
            return {"result": result, "branch": branch, "total": sum(result)}
        
        with self.storage:
            results = []
            for branch in ["A", "B", "C"]:
                result = branch_compute([1, 2, 3], branch=branch)
                results.append(result)
        
        cf = self.storage.cf(branch_compute).expand_all()
        return cf, results
    
    def run_demo(self):
        """运行完整演示"""
        print("🚀 ComputationFrame 简洁演示")
        print("=" * 40)
        
        # 1. 创建基础计算历史
        summaries = self.create_history()
        
        # 2. 分析原始计算框架
        original_cf = self.storage.cf(self.summarize).expand_all()
        self.analyze_cf(original_cf, "原始计算框架")
        self.generate_svg(original_cf, "demo_original.svg")
        
        # 3. 测试三种更新策略
        strategies = [
            ("版本控制", self.update_strategy_1_version),
            ("参数哈希", self.update_strategy_2_hash),
            ("逻辑分支", self.update_strategy_3_branch)
        ]
        
        for name, strategy_func in strategies:
            try:
                cf, results = strategy_func()
                info = self.analyze_cf(cf, f"{name}策略")
                self.generate_svg(cf, f"demo_{name.lower()}.svg")
                print(f"✅ {name}策略成功，生成 {len(results) if isinstance(results, list) else 1} 个结果")
            except Exception as e:
                print(f"❌ {name}策略失败: {e}")
        
        # 4. 创建组合视图
        print("\n🔗 创建组合计算框架:")
        try:
            combined_cf = (self.storage.cf(self.compute) | 
                          self.storage.cf(self.summarize)).expand_all()
            self.analyze_cf(combined_cf, "组合计算框架")
            self.generate_svg(combined_cf, "demo_combined.svg")
        except Exception as e:
            print(f"❌ 组合框架创建失败: {e}")
        
        print("\n🎉 演示完成！")
        print(f"📁 查看 SVG 文件: {self.svg_dir}")

def quick_demo():
    """快速演示函数"""
    demo = CFDemo()
    demo.run_demo()

def advanced_usage():
    """高级用法示例"""
    print("\n🔧 高级用法演示:")
    demo = CFDemo()
    
    # 创建计算历史
    demo.create_history()
    
    # 单独分析某个函数
    cf = demo.storage.cf(demo.compute)
    info = demo.analyze_cf(cf, "compute 函数")
    
    # 获取详细的函数调用表
    if cf.fnames:
        fname = next(iter(cf.fnames))
        table = cf.get_func_table(fname)
        print(f"\n📊 {fname} 详细调用表:")
        print(table)
    
    # 获取变量引用
    try:
        refs = cf.refs_by_var()
        print(f"\n📝 变量引用: {list(refs.keys())}")
        for var, ref_list in refs.items():
            if isinstance(ref_list, list):
                values = [demo.storage.unwrap(ref) for ref in ref_list[:3]]
                print(f"  {var}: {values}")
    except Exception as e:
        print(f"获取变量引用失败: {e}")

def main():
    """主函数 - 提供多种使用方式"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "advanced":
        advanced_usage()
    else:
        quick_demo()

if __name__ == "__main__":
    main() 
import os
from flow import create_flow

def main():
    """运行批处理示例。"""
    # 如果数据目录不存在，则创建它
    os.makedirs("data", exist_ok=True)
    
    # 如果示例 CSV 文件不存在，则创建它
    if not os.path.exists("data/sales.csv"):
        print("正在创建示例 sales.csv...")
        import pandas as pd
        import numpy as np
        
        # 生成示例数据
        np.random.seed(42)
        n_rows = 10000
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=n_rows),
            "amount": np.random.normal(100, 30, n_rows).round(2),
            "product": np.random.choice(["A", "B", "C"], n_rows)
        })
        df.to_csv("data/sales.csv", index=False)
    
    # 初始化共享存储
    shared = {
        "input_file": "data/sales.csv"
    }
    
    # 创建并运行流程
    print(f"正在分块处理 sales.csv...")
    flow = create_flow()
    flow.run(shared)

if __name__ == "__main__":
    main() 
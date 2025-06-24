import pandas as pd
from pocketflow import BatchNode

class CSVProcessor(BatchNode):
    """BatchNode，用于分块处理大型 CSV 文件。"""
    
    def __init__(self, chunk_size=1000):
        """使用分块大小进行初始化。"""
        super().__init__()
        self.chunk_size = chunk_size
    
    def prep(self, shared):
        """将 CSV 文件分割成块。
        
        返回一个 DataFrame 迭代器，每个 DataFrame 包含 chunk_size 行。
        """
        # 分块读取 CSV
        chunks = pd.read_csv(
            shared["input_file"],
            chunksize=self.chunk_size
        )
        return chunks
    
    def exec(self, chunk):
        """处理 CSV 的单个块。
        
        Args:
            chunk: 包含 chunk_size 行的 pandas DataFrame
            
        Returns:
            dict: 此块的统计信息
        """
        return {
            "total_sales": chunk["amount"].sum(),
            "num_transactions": len(chunk),
            "total_amount": chunk["amount"].sum()
        }
    
    def post(self, shared, prep_res, exec_res_list):
        """合并所有块的结果。
        
        Args:
            prep_res: 原始块迭代器
            exec_res_list: 每个块的结果列表
            
        Returns:
            str: 下一步要执行的操作
        """
        # 合并所有块的统计信息
        total_sales = sum(res["total_sales"] for res in exec_res_list)
        total_transactions = sum(res["num_transactions"] for res in exec_res_list)
        total_amount = sum(res["total_amount"] for res in exec_res_list)
        
        # 计算最终统计信息
        shared["statistics"] = {
            "total_sales": total_sales,
            "average_sale": total_amount / total_transactions,
            "total_transactions": total_transactions
        }
        
        return "show_stats" 
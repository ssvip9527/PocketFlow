from pocketflow import Flow, Node
from nodes import CSVProcessor

class ShowStats(Node):
    """用于显示最终统计信息的节点。"""
    
    def prep(self, shared):
        """从共享存储中获取统计信息。"""
        return shared["statistics"]
    
    def post(self, shared, prep_res, exec_res):
        """显示统计信息。"""
        stats = prep_res
        print("\n最终统计数据:")
        print(f"- 总销售额: ${stats['total_sales']:,.2f}")
        print(f"- 平均销售额: ${stats['average_sale']:,.2f}")
        print(f"- 总交易量: {stats['total_transactions']:,}\n")
        return "end"

def create_flow():
    """创建并返回处理流程。"""
    # 创建节点
    processor = CSVProcessor(chunk_size=1000)
    show_stats = ShowStats()
    
    # 连接节点
    processor - "show_stats" >> show_stats
    
    # 创建并返回流程
    return Flow(start=processor)
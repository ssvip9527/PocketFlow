"""通信示例的节点实现。"""

from pocketflow import Node

class EndNode(Node):
    """处理流程终止的节点。"""
    pass

class TextInput(Node):
    """读取文本输入并初始化共享存储的节点。"""
    
    def prep(self, shared):
        """从共享存储中获取统计信息。"""
        """获取用户输入并确保共享存储已初始化。"""
        return input("输入文本（或输入 'q' 退出）：")
    
    def post(self, shared, prep_res, exec_res):
        """显示统计信息并继续流程。"""
        """存储文本并初始化/更新统计信息。"""
        if prep_res == 'q':
            return "exit"
        
        # 存储文本
        shared["text"] = prep_res
        
        # 如果统计信息不存在，则初始化
        if "stats" not in shared:
            shared["stats"] = {
                "total_texts": 0,
                "total_words": 0
            }
        shared["stats"]["total_texts"] += 1
        
        return "count"

class WordCounter(Node):
    """计算文本中单词数量的节点。"""
    
    def prep(self, shared):
        """从共享存储中获取文本。"""
        return shared["text"]
    
    def exec(self, text):
        """计算文本中的单词数量。"""
        return len(text.split())
    
    def post(self, shared, prep_res, exec_res):
        """更新单词计数统计信息。"""
        shared["stats"]["total_words"] += exec_res
        return "show"

class ShowStats(Node):
    """显示共享存储中统计信息的节点。"""
    
    def prep(self, shared):
        """Get statistics from shared store."""
        return shared["stats"]
    
    def post(self, shared, prep_res, exec_res):
        """Display statistics and continue the flow."""
        stats = prep_res
        print(f"\n统计信息:")
        print(f"- 已处理文本数: {stats['total_texts']}")
        print(f"- 总词数: {stats['total_words']}")
        print(f"- 平均每文本词数: {stats['total_words'] / stats['total_texts']:.1f}\n")
        return "continue"
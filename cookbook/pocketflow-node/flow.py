from pocketflow import Node, Flow
from utils.call_llm import call_llm

class Summarize(Node):
    def prep(self, shared):
        """从共享存储中读取和预处理数据。"""
        return shared["data"]

    def exec(self, prep_res):
        """使用LLM执行摘要。"""
        if not prep_res:
            return "空文本"
        prompt = f"用10个词总结这段文本: {prep_res}"
        summary = call_llm(prompt)  # 可能会失败
        return summary

    def exec_fallback(self, shared, prep_res, exc):
        """提供一个简单的备用方案，而不是崩溃。"""
        return "处理您的请求时发生错误。"

    def post(self, shared, prep_res, exec_res):
        """将摘要存储在共享存储中。"""
        shared["summary"] = exec_res
        # 不返回任何内容则返回“default”

# 创建流程
summarize_node = Summarize(max_retries=3)
flow = Flow(start=summarize_node)
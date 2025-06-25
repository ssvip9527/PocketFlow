from pocketflow import Node, Flow
from utils.call_llm import call_llm

# 这是一个示例节点和流程
# 请将其替换为您自己的节点和流程
class AnswerNode(Node):
    def prep(self, shared):
        # 从共享中读取问题
        return shared["question"]
    
    def exec(self, question):
        return call_llm(question)
    
    def post(self, shared, prep_res, exec_res):
        # 将答案存储在共享中
        shared["answer"] = exec_res

answer_node = AnswerNode()
qa_flow = Flow(start=answer_node)
from pocketflow import Flow
from nodes import ReadResumesNode, EvaluateResumesNode, ReduceResultsNode

def create_resume_processing_flow():
    """创建一个用于处理简历的 Map-Reduce 流程。"""
    # 创建节点
    read_resumes_node = ReadResumesNode()
    evaluate_resumes_node = EvaluateResumesNode()
    reduce_results_node = ReduceResultsNode()
    
    # 连接节点
    read_resumes_node >> evaluate_resumes_node >> reduce_results_node
    
    # 创建流程
    return Flow(start=read_resumes_node)
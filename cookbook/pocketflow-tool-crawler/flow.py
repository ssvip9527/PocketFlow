from pocketflow import Flow
from nodes import CrawlWebsiteNode, AnalyzeContentBatchNode, GenerateReportNode

def create_flow() -> Flow:
    """创建并配置爬取流程
    
    返回:
        Flow: 配置好的可运行流程
    """
    # 创建节点
    crawl = CrawlWebsiteNode()
    analyze = AnalyzeContentBatchNode()
    report = GenerateReportNode()
    
    # 连接节点
    crawl >> analyze >> report
    
    # 创建从爬取开始的流程
    return Flow(start=crawl)

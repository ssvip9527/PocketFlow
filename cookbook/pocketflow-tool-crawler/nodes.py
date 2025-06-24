from pocketflow import Node, BatchNode
from tools.crawler import WebCrawler
from tools.parser import analyze_site
from typing import List, Dict

class CrawlWebsiteNode(Node):
    """用于抓取网站并提取内容的节点"""
    
    def prep(self, shared):
        return shared.get("base_url"), shared.get("max_pages", 10) # 默认最大页面数为10
        
    def exec(self, inputs):
        base_url, max_pages = inputs
        if not base_url:
            return []
            
        crawler = WebCrawler(base_url, max_pages)
        return crawler.crawl()
        
    def post(self, shared, prep_res, exec_res):
        shared["crawl_results"] = exec_res
        return "default"

class AnalyzeContentBatchNode(BatchNode):
    """用于批量分析爬取内容的节点"""
    
    def prep(self, shared):
        results = shared.get("crawl_results", [])
        # 以5页为一批次处理
        batch_size = 5
        return [results[i:i+batch_size] for i in range(0, len(results), batch_size)]
        
    def exec(self, batch):
        return analyze_site(batch)
        
    def post(self, shared, prep_res, exec_res_list):
        # 合并所有批次的结果
        all_results = []
        for batch_results in exec_res_list:
            all_results.extend(batch_results)
            
        shared["analyzed_results"] = all_results
        return "default"

class GenerateReportNode(Node):
    """用于生成分析摘要报告的节点"""
    
    def prep(self, shared):
        return shared.get("analyzed_results", [])
        
    def exec(self, results):
        if not results:
            return "没有可报告的结果"
            
        report = []
        report.append(f"分析报告\n")
        report.append(f"分析页面总数: {len(results)}\n")
        
        for page in results:
            report.append(f"\n页面: {page['url']}")
            report.append(f"标题: {page['title']}")
            
            analysis = page.get("analysis", {})
            report.append(f"摘要: {analysis.get('summary', 'N/A')}")
            report.append(f"主题: {', '.join(analysis.get('topics', []))}")
            report.append(f"内容类型: {analysis.get('content_type', 'unknown')}")
            report.append("-" * 80)
            
        return "\n".join(report)
        
    def post(self, shared, prep_res, exec_res):
        shared["report"] = exec_res
        print("\n报告已生成:")
        print(exec_res)
        return "default"

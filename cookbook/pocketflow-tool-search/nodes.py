from pocketflow import Node
from tools.search import SearchTool
from tools.parser import analyze_results
from typing import List, Dict

class SearchNode(Node):
    """使用SerpAPI执行网络搜索的节点"""
    
    def prep(self, shared):
        return shared.get("query"), shared.get("num_results", 5)
        
    def exec(self, inputs):
        query, num_results = inputs
        if not query:
            return []
            
        searcher = SearchTool()
        return searcher.search(query, num_results)
        
    def post(self, shared, prep_res, exec_res):
        shared["search_results"] = exec_res
        return "default"

class AnalyzeResultsNode(Node):
    """使用LLM分析搜索结果的节点"""
    
    def prep(self, shared):
        return shared.get("query"), shared.get("search_results", [])
        
    def exec(self, inputs):
        query, results = inputs
        if not results:
            return {
                "summary": "没有可分析的搜索结果",
                "key_points": [],
                "follow_up_queries": []
            }
            
        return analyze_results(query, results)
        
    def post(self, shared, prep_res, exec_res):
        shared["analysis"] = exec_res
        
        # 打印分析结果
        print("\n搜索分析:")
        print("\n摘要:", exec_res["summary"])
        
        print("\n关键点:")
        for point in exec_res["key_points"]:
            print(f"- {point}")
            
        print("\n建议的后续查询:")
        for query in exec_res["follow_up_queries"]:
            print(f"- {query}")
            
        return "default"

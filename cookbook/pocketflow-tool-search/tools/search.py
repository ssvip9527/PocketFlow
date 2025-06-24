import os
from serpapi import GoogleSearch
from typing import Dict, List, Optional

class SearchTool:
    """使用SerpAPI执行网络搜索的工具"""
    
    def __init__(self, api_key: Optional[str] = None):
        """使用API密钥初始化搜索工具
        
        参数:
            api_key (str, optional): SerpAPI密钥。默认为环境变量SERPAPI_API_KEY。
        """
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("未找到SerpAPI密钥。请设置环境变量SERPAPI_API_KEY。")
            
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """通过SerpAPI执行Google搜索
        
        参数:
            query (str): 搜索查询
            num_results (int, optional): 返回结果的数量。默认为5。
            
        返回:
            List[Dict]: 包含标题、摘要和链接的搜索结果
        """
        # 配置搜索参数
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": num_results
        }
        
        try:
            # 执行搜索
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # 提取自然搜索结果
            if "organic_results" not in results:
                return []
                
            processed_results = []
            for result in results["organic_results"][:num_results]:
                processed_results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "link": result.get("link", "")
                })
                
            return processed_results
            
        except Exception as e:
            print(f"搜索错误: {str(e)}")
            return []

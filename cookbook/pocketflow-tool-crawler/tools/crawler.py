import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set

class WebCrawler:
    """一个简单的网络爬虫，用于提取内容并跟踪链接"""
    
    def __init__(self, base_url: str, max_pages: int = 10):
        self.base_url = base_url
        self.max_pages = max_pages
        self.visited: Set[str] = set()
        
    def is_valid_url(self, url: str) -> bool:
        """检查 URL 是否属于同一域名"""
        base_domain = urlparse(self.base_url).netloc
        url_domain = urlparse(url).netloc
        return base_domain == url_domain
        
    def extract_page_content(self, url: str) -> Dict:
        """从单个页面提取内容"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 提取主要内容
            content = {
                "url": url,
                "title": soup.title.string if soup.title else "",
                "text": soup.get_text(separator="\n", strip=True),
                "links": []
            }
            
            # 提取链接
            for link in soup.find_all("a"):
                href = link.get("href")
                if href:
                    absolute_url = urljoin(url, href)
                    if self.is_valid_url(absolute_url):
                        content["links"].append(absolute_url)
            
            return content
            
        except Exception as e:
            print(f"抓取 {url} 时出错: {str(e)}")
            return None
    
    def crawl(self) -> List[Dict]:
        """从 base_url 开始抓取网站"""
        to_visit = [self.base_url]
        results = []
        
        while to_visit and len(self.visited) < self.max_pages:
            url = to_visit.pop(0)
            
            if url in self.visited:
                continue
                
            print(f"正在抓取: {url}")
            content = self.extract_page_content(url)
            
            if content:
                self.visited.add(url)
                results.append(content)
                
                # 添加新的待访问 URL
                new_urls = [url for url in content["links"] 
                          if url not in self.visited 
                          and url not in to_visit]
                to_visit.extend(new_urls)
        
        return results

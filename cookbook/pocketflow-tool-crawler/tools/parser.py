from typing import Dict, List
from utils.call_llm import call_llm

def analyze_content(content: Dict) -> Dict:
    """使用 LLM 分析网页内容
    
    Args:
        content (Dict): 包含 url、title 和 text 的网页内容
        
    Returns:
        Dict: 分析结果，包括摘要和主题
    """
    prompt = f"""
分析此网页内容：

标题: {content['title']}
URL: {content['url']}
内容: {content['text'][:2000]}  # 限制内容长度

请提供：
1. 简要摘要（2-3 句话）
2. 主要主题/关键词（最多 5 个）
3. 内容类型（文章、产品页面等）

以 YAML 格式输出：
```yaml
summary: >
    此处填写简要摘要
topics:
    - 主题 1
    - 主题 2
content_type: 此处填写类型
```
"""
    
    try:
        response = call_llm(prompt)
        # 提取代码块之间的 YAML
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        
        import yaml
        analysis = yaml.safe_load(yaml_str)
        
        # 验证必填字段
        assert "summary" in analysis
        assert "topics" in analysis
        assert "content_type" in analysis
        assert isinstance(analysis["topics"], list)
        
        return analysis
        
    except Exception as e:
        print(f"分析内容时出错: {str(e)}")
        return {
            "summary": "分析内容时出错",
            "topics": [],
            "content_type": "未知"
        }

def analyze_site(crawl_results: List[Dict]) -> List[Dict]:
    """分析所有抓取的页面
    
    Args:
        crawl_results (List[Dict]): 抓取到的页面内容列表
        
    Returns:
        List[Dict]: 包含分析结果的原始内容
    """
    analyzed_results = []
    
    for content in crawl_results:
        if content and content.get("text"):
            analysis = analyze_content(content)
            content["analysis"] = analysis
            analyzed_results.append(content)
            
    return analyzed_results

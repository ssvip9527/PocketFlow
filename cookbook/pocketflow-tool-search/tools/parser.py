from typing import Dict, List
from utils.call_llm import call_llm

def analyze_results(query: str, results: List[Dict]) -> Dict:
    """使用LLM分析搜索结果
    
    参数:
        query (str): 原始搜索查询
        results (List[Dict]): 要分析的搜索结果
        
    返回:
        Dict: 包含摘要和关键点的分析结果
    """
    # 格式化结果用于提示词
    formatted_results = []
    for i, result in enumerate(results, 1):
        formatted_results.append(f"""
Result {i}:
Title: {result['title']}
Snippet: {result['snippet']}
URL: {result['link']}
""")
    
    prompt = f"""
Analyze these search results for the query: "{query}"

{'\n'.join(formatted_results)}

Please provide:
1. A concise summary of the findings (2-3 sentences)
2. Key points or facts (up to 5 bullet points)
3. Suggested follow-up queries (2-3)

Output in YAML format:
```yaml
summary: >
    brief summary here
key_points:
    - point 1
    - point 2
follow_up_queries:
    - query 1
    - query 2
```
"""
    
    try:
        response = call_llm(prompt)
        # 从代码块中提取YAML
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        
        import yaml
        analysis = yaml.safe_load(yaml_str)
        
        # 验证必填字段
        assert "summary" in analysis
        assert "key_points" in analysis
        assert "follow_up_queries" in analysis
        assert isinstance(analysis["key_points"], list)
        assert isinstance(analysis["follow_up_queries"], list)
        
        return analysis
        
    except Exception as e:
        print(f"Error analyzing results: {str(e)}")
        return {
            "summary": "Error analyzing results",
            "key_points": [],
            "follow_up_queries": []
        }
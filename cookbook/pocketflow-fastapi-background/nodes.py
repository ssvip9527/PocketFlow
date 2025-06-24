import yaml
from pocketflow import Node, BatchNode
from utils.call_llm import call_llm

class GenerateOutline(Node):
    def prep(self, shared):
        return shared["topic"]
    
    def exec(self, topic):
        prompt = f"""
Create a simple outline for an article about {topic}.
Include at most 3 main sections (no subsections).

Output the sections in YAML format as shown below:

```yaml
sections:
    - First section title
    - Second section title  
    - Third section title
```"""
        response = call_llm(prompt)
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        structured_result = yaml.safe_load(yaml_str)
        return structured_result
    
    def post(self, shared, prep_res, exec_res):
        sections = exec_res["sections"]
        shared["sections"] = sections
        
        # 通过 SSE 队列发送进度更新
        progress_msg = {"step": "outline", "progress": 33, "data": {"sections": sections}}
        shared["sse_queue"].put_nowait(progress_msg)
        
        return "default"

class WriteContent(BatchNode):
    def prep(self, shared):
        # 存储 sections 和 sse_queue 以供 exec 使用
        self.sections = shared.get("sections", [])
        self.sse_queue = shared["sse_queue"]
        return self.sections
    
    def exec(self, section):
        prompt = f"""
Write a short paragraph (MAXIMUM 100 WORDS) about this section:

{section}

Requirements:
- Explain the idea in simple, easy-to-understand terms
- Use everyday language, avoiding jargon
- Keep it very concise (no more than 100 words)
- Include one brief example or analogy
"""
        content = call_llm(prompt)
        
        # 为此部分发送进度更新
        current_section_index = self.sections.index(section) if section in self.sections else 0
        total_sections = len(self.sections)
        
        # 进度从 33%（大纲后）到 66%（样式前）
        # 每个部分贡献 (66-33)/total_sections = 33/total_sections 百分比
        section_progress = 33 + ((current_section_index + 1) * 33 // total_sections)
        
        progress_msg = {
            "step": "content", 
            "progress": section_progress, 
            "data": {
                "section": section,
                "completed_sections": current_section_index + 1,
                "total_sections": total_sections
            }
        }
        self.sse_queue.put_nowait(progress_msg)
        
        return f"## {section}\n\n{content}\n"
    
    def post(self, shared, prep_res, exec_res_list):
        draft = "\n".join(exec_res_list)
        shared["draft"] = draft
        return "default"

class ApplyStyle(Node):
    def prep(self, shared):
        return shared["draft"]
    
    def exec(self, draft):
        prompt = f"""
Rewrite the following draft in a conversational, engaging style:

{draft}

Make it:
- Conversational and warm in tone
- Include rhetorical questions that engage the reader
- Add analogies and metaphors where appropriate
- Include a strong opening and conclusion
"""
        return call_llm(prompt)
    
    def post(self, shared, prep_res, exec_res):
        shared["final_article"] = exec_res
        
        # 通过 SSE 队列发送完成更新
        progress_msg = {"step": "complete", "progress": 100, "data": {"final_article": exec_res}}
        shared["sse_queue"].put_nowait(progress_msg)
        
        return "default" 
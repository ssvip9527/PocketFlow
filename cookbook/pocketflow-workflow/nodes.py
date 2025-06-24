import re
from pocketflow import Node, BatchNode
from utils.call_llm import call_llm
import yaml

class GenerateOutline(Node):
    def prep(self, shared):
        return shared["topic"]
    
    def exec(self, topic):
        prompt = f"""
为关于 {topic} 的文章创建一个简单大纲。
最多包含 3 个主要部分（无子部分）。

以 YAML 格式输出部分，如下所示：

```yaml
sections:
    - |
        第一部分
    - |
        第二部分
    - |
        第三部分
```"""
        response = call_llm(prompt)
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        structured_result = yaml.safe_load(yaml_str)
        return structured_result
    
    def post(self, shared, prep_res, exec_res):
        # 存储结构化数据
        shared["outline_yaml"] = exec_res
        
        # 提取部分
        sections = exec_res["sections"]
        shared["sections"] = sections
        
        # 格式化显示
        formatted_outline = "\n".join([f"{i+1}. {section}" for i, section in enumerate(sections)])
        shared["outline"] = formatted_outline
        
        # 显示结果
        print("\n===== 大纲 (YAML) =====\n")
        print(yaml.dump(exec_res, default_flow_style=False))
        print("\n===== 解析后的大纲 =====\n")
        print(formatted_outline)
        print("\n=========================\n")
        
        return "default"

class WriteSimpleContent(BatchNode):
    def prep(self, shared):
        # 获取要处理的部分列表并存储以进行进度跟踪
        self.sections = shared.get("sections", [])
        return self.sections
    
    def exec(self, section):
        prompt = f"""
撰写关于此部分的短段落（最多 100 字）：

{section}

要求：
- 用简单易懂的术语解释想法
- 使用日常语言，避免行话
- 保持非常简洁（不超过 100 字）
- 包含一个简短的示例或类比
"""
        content = call_llm(prompt)
        
        # 显示此部分的进度
        current_section_index = self.sections.index(section) if section in self.sections else 0
        total_sections = len(self.sections)
        print(f"✓ Completed section {current_section_index + 1}/{total_sections}: {section}")
        
        return section, content
    
    def post(self, shared, prep_res, exec_res_list):
        # exec_res_list 包含 [(部分, 内容), (部分, 内容), ...]
        section_contents = {}
        all_sections_content = []
        
        for section, content in exec_res_list:
            section_contents[section] = content
            all_sections_content.append(f"## {section}\n\n{content}\n")
        
        draft = "\n".join(all_sections_content)
        
        # 存储部分内容和草稿
        shared["section_contents"] = section_contents
        shared["draft"] = draft
        
        print("\n===== 部分内容 =====\n")
        for section, content in section_contents.items():
            print(f"--- {section} ---")
            print(content)
            print()
        print("===========================\n")
        
        return "default"

class ApplyStyle(Node):
    def prep(self, shared):
        """
        从共享数据中获取草稿
        """
        return shared["draft"]
    
    def exec(self, draft):
        """
        将特定样式应用于文章
        """
        prompt = f"""
        以对话式、引人入胜的风格重写以下草稿：
        
        {draft}
        
        使其：
        - 语气对话化和热情
        - 包含引人入胜的反问句
        - 适当地添加类比和隐喻
        - 包含强有力的开头和结尾
        """
        return call_llm(prompt)
    
    def post(self, shared, prep_res, exec_res):
        """
        将最终文章存储在共享数据中
        """
        shared["final_article"] = exec_res
        print("\n===== 最终文章 =====\n")
        print(exec_res)
        print("\n========================\n")
        return "default"
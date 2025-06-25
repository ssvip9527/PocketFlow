import yaml
import os  # Needed for the utils import below
from pocketflow import Node, Flow
from utils import call_llm # Assumes utils.py with call_llm exists

class ResumeParserNode(Node):
    def prep(self, shared):
        """返回共享状态中的简历文本和目标技能。"""
        return {
            "resume_text": shared["resume_text"],
            "target_skills": shared.get("target_skills", [])
        }

    def exec(self, prep_res):
        """使用提示工程从简历中提取结构化数据。
        请求 YAML 输出，包含注释和技能索引列表。
        """
        resume_text = prep_res["resume_text"]
        target_skills = prep_res["target_skills"]

        # 为提示格式化技能，包含索引
        skill_list_for_prompt = "\n".join([f"{i}: {skill}" for i, skill in enumerate(target_skills)])

        # 简化提示，专注于关键指令和格式
        prompt = f"""
分析以下简历。仅以 YAML 格式输出所需信息。

**简历:**
```
{resume_text}
```

**目标技能 (使用这些索引):**
```
{skill_list_for_prompt}
```

**YAML 输出要求:**
- 提取 `name` (字符串)。
- 提取 `email` (字符串)。
- 提取 `experience` (对象列表，包含 `title` 和 `company`)。
- 提取 `skill_indexes` (从目标技能列表中找到的整数列表)。
- **在 `name`、`email`、`experience`、`experience` 中的每个项目以及 `skill_indexes` 之前添加 YAML 注释 (`#`) 解释来源。**

**示例格式:**
```yaml
# 在顶部找到姓名
name: Jane Doe
# 在联系信息中找到电子邮件
email: jane@example.com
# 经验部分分析
experience:
  # 列出的第一份工作
  - title: Manager
    company: Corp A
  # 列出的第二份工作
  - title: Assistant
    company: Corp B
# 根据简历内容从目标列表中识别出的技能
skill_indexes:
  # 在顶部找到 0
  - 0
  # 在经验中找到 2
  - 2
```

现在生成 YAML 输出:
"""
        response = call_llm(prompt)

        # --- 最小 YAML 提取 ---
        # 假设 LLM 正确使用 ```yaml 块
        yaml_str = response.split("```yaml")[1].split("```")[0].strip()
        structured_result = yaml.safe_load(yaml_str)
        # --- 结束最小提取 ---

        # --- 基本验证 ---
        assert structured_result is not None, "验证失败: 解析的 YAML 为 None"
        assert "name" in structured_result, "验证失败: 缺少 'name'"
        assert "email" in structured_result, "验证失败: 缺少 'email'"
        assert "experience" in structured_result, "验证失败: 缺少 'experience'"
        assert isinstance(structured_result.get("experience"), list), "验证失败: 'experience' 不是列表"
        assert "skill_indexes" in structured_result, "验证失败: 缺少 'skill_indexes'"
        skill_indexes_val = structured_result.get("skill_indexes")
        assert skill_indexes_val is None or isinstance(skill_indexes_val, list), "验证失败: 'skill_indexes' 不是列表或 None"
        if isinstance(skill_indexes_val, list):
             for index in skill_indexes_val:
                 assert isinstance(index, int), f"验证失败: 技能索引 '{index}' 不是整数"
        # --- 结束基本验证 ---

        return structured_result

    def post(self, shared, prep_res, exec_res):
        """存储结构化数据并打印。"""
        shared["structured_data"] = exec_res

        print("\n=== 结构化简历数据 (注释和技能索引列表) ===\n")
        # 导出 YAML，确保块样式以便阅读
        print(yaml.dump(exec_res, sort_keys=False, allow_unicode=True, default_flow_style=None))
        print("\n============================================================\n")
        print("✅ 简历信息提取成功。")


# === 主执行逻辑 ===
if __name__ == "__main__":
    print("=== 简历解析器 - 带有索引和注释的结构化输出 ===\n")

    # --- 配置 ---
    target_skills_to_find = [
        "团队领导与管理", # 0
        "CRM 软件",                 # 1
        "项目管理",           # 2
        "公众演讲",              # 3
        "Microsoft Office",             # 4
        "Python",                       # 5
        "数据分析"                 # 6
    ]
    resume_file = 'data.txt' # 假设 data.txt 包含简历

    # --- 准备共享状态 ---
    shared = {}
    try:
        with open(resume_file, 'r') as file:
            shared["resume_text"] = file.read()
    except FileNotFoundError:
        print(f"错误: 简历文件 '{resume_file}' 未找到。")
        exit(1) # 如果简历文件缺失则退出

    shared["target_skills"] = target_skills_to_find

    # --- 定义并运行流程 ---
    parser_node = ResumeParserNode(max_retries=3, wait=10)
    flow = Flow(start=parser_node)
    flow.run(shared) # 执行解析节点

    # --- 显示找到的技能 ---
    if "structured_data" in shared and "skill_indexes" in shared["structured_data"]:
         print("\n--- 找到的目标技能 (来自索引) ---")
         found_indexes = shared["structured_data"]["skill_indexes"]
         if found_indexes: # 检查列表是否不为空或 None
             for index in found_indexes:
                 if 0 <= index < len(target_skills_to_find):
                     print(f"- {target_skills_to_find[index]} (索引: {index})")
                 else:
                     print(f"- 警告: 找到无效的技能索引 {index}")
         else:
             print("未从列表中识别出目标技能。")
         print("----------------------------------------\n")
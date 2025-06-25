from pocketflow import Node, BatchNode
from utils import call_llm
import yaml
import os

class ReadResumesNode(Node):
    """Map 阶段：将数据目录中的所有简历读入共享存储。"""
    
    def exec(self, _):
        resume_files = {}
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        
        for filename in os.listdir(data_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(data_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    resume_files[filename] = file.read()
        
        return resume_files
    
    def post(self, shared, prep_res, exec_res):
        shared["resumes"] = exec_res
        return "default"


class EvaluateResumesNode(BatchNode):
    """批处理：评估每份简历以确定候选人是否合格。"""
    
    def prep(self, shared):
        return list(shared["resumes"].items())
    
    def exec(self, resume_item):
        """评估一份简历。"""
        filename, content = resume_item
        
        prompt = f"""
评估以下简历，并确定候选人是否符合高级技术职位的要求。
资格标准：
- 至少拥有相关领域的学士学位
- 至少 3 年相关工作经验
- 具备与职位相关的强大技术技能

简历：
{content}

以 YAML 格式返回您的评估：
```yaml
candidate_name: [候选人姓名]
qualifies: [true/false]
reasons:
  - [合格/不合格的第一个原因]
  - [第二个原因，如果适用]
```
"""
        response = call_llm(prompt)
        
        # 提取 YAML 内容
        yaml_content = response.split("```yaml")[1].split("```")[0].strip() if "```yaml" in response else response
        result = yaml.safe_load(yaml_content)
        
        return (filename, result)

    def post(self, shared, prep_res, exec_res_list):
        shared["evaluations"] = {filename: result for filename, result in exec_res_list}
        return "default"


class ReduceResultsNode(Node):
    """Reduce 节点：统计并打印有多少候选人合格。"""
    
    def prep(self, shared):
        return shared["evaluations"]
    
    def exec(self, evaluations):
        qualified_count = 0
        total_count = len(evaluations)
        qualified_candidates = []
        
        for filename, evaluation in evaluations.items():
            if evaluation.get("qualifies", False):
                qualified_count += 1
                qualified_candidates.append(evaluation.get("candidate_name", "未知"))
        
        summary = {
            "total_candidates": total_count,
            "qualified_count": qualified_count,
            "qualified_percentage": round(qualified_count / total_count * 100, 1) if total_count > 0 else 0,
            "qualified_names": qualified_candidates
        }
        
        return summary
    
    def post(self, shared, prep_res, exec_res):
        shared["summary"] = exec_res
        
        print("\n===== 简历资格评估摘要 =====")
        print(f"评估候选人总数: {exec_res['total_candidates']}")
        print(f"合格候选人: {exec_res['qualified_count']} ({exec_res['qualified_percentage']}%) 张")
        
        if exec_res['qualified_names']:
            print("\n合格候选人:")
            for name in exec_res['qualified_names']:
                print(f"- {name}")
        
        return "default"
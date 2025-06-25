from pocketflow import Node, Flow
from utils import call_llm, get_tools, call_tool
import yaml
import sys

class GetToolsNode(Node):
    def prep(self, shared):
        """初始化并获取工具"""
        # 问题现在通过 shared 从 main 传递
        print("🔍 正在获取可用工具...")
        return "simple_server.py"

    def exec(self, server_path):
        """从 MCP 服务器检索工具"""
        tools = get_tools(server_path)
        return tools

    def post(self, shared, prep_res, exec_res):
        """存储工具并处理到决策节点"""
        tools = exec_res
        shared["tools"] = tools
        
        # 格式化工具信息以备后用
        tool_info = []
        for i, tool in enumerate(tools, 1):
            properties = tool.inputSchema.get('properties', {})
            required = tool.inputSchema.get('required', [])
            
            params = []
            for param_name, param_info in properties.items():
                param_type = param_info.get('type', 'unknown')
                req_status = "(必填)" if param_name in required else "(可选)"
                params.append(f"    - {param_name} ({param_type}): {req_status}")
            
            tool_info.append(f"[{i}] {tool.name}\n  描述: {tool.description}\n  参数:\n" + "\n".join(params))
        
        shared["tool_info"] = "\n".join(tool_info)
        return "decide"

class DecideToolNode(Node):
    def prep(self, shared):
        """准备提示，供 LLM 处理问题"""
        tool_info = shared["tool_info"]
        question = shared["question"]
        
        prompt = f"""
### 上下文
您是一个可以通过模型上下文协议 (MCP) 使用工具的助手。

### 行动空间
{tool_info}

### 任务
回答这个问题: "{question}"

## 下一步行动
分析问题，提取任何数字或参数，并决定使用哪个工具。
以以下格式返回您的响应:

```yaml
thinking: |
    <您关于问题在问什么以及要提取哪些数字的逐步推理>
tool: <要使用的工具名称>
reason: <您选择此工具的原因>
parameters:
    <参数名称>: <参数值>
    <参数名称>: <参数值>
```
重要提示:
1. 正确从问题中提取数字
2. 多行字段使用正确的缩进 (4 个空格)
3. 多行文本字段使用 | 字符
"""
        return prompt

    def exec(self, prompt):
        """调用 LLM 处理问题并决定使用哪个工具"""
        print("🤔 正在分析问题并决定使用哪个工具...")
        response = call_llm(prompt)
        return response

    def post(self, shared, prep_res, exec_res):
        """从 YAML 中提取决策并保存到共享上下文"""
        try:
            yaml_str = exec_res.split("```yaml")[1].split("```")[0].strip()
            decision = yaml.safe_load(yaml_str)
            
            shared["tool_name"] = decision["tool"]
            shared["parameters"] = decision["parameters"]
            shared["thinking"] = decision.get("thinking", "")
            
            print(f"💡 选定的工具: {decision['tool']}")
            print(f"🔢 提取的参数: {decision['parameters']}")
            
            return "execute"
        except Exception as e:
            print(f"❌ 解析 LLM 响应时出错: {e}")
            print("原始响应:", exec_res)
            return None

class ExecuteToolNode(Node):
    def prep(self, shared):
        """准备工具执行参数"""
        return shared["tool_name"], shared["parameters"]

    def exec(self, inputs):
        """执行所选工具"""
        tool_name, parameters = inputs
        print(f"🔧 正在执行工具 '{tool_name}'，参数: {parameters}")
        result = call_tool("simple_server.py", tool_name, parameters)
        return result

    def post(self, shared, prep_res, exec_res):
        print(f"\n✅ 最终答案: {exec_res}")
        return "done"


if __name__ == "__main__":
    # 默认问题
    default_question = "982713504867129384651 加 73916582047365810293746529 是多少？"
    
    # 如果提供了 --，则从命令行获取问题
    question = default_question
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            question = arg[2:]
            break
    
    print(f"🤔 正在处理问题: {question}")
    
    # 创建节点
    get_tools_node = GetToolsNode()
    decide_node = DecideToolNode()
    execute_node = ExecuteToolNode()
    
    # 连接节点
    get_tools_node - "decide" >> decide_node
    decide_node - "execute" >> execute_node
    
    # 创建并运行流程
    flow = Flow(start=get_tools_node)
    shared = {"question": question}
    flow.run(shared)
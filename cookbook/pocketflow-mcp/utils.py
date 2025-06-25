from openai import OpenAI
import os
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 全局标志，控制是使用 MCP 还是本地实现
MCP = False

def call_llm(prompt):    
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

def get_tools(server_script_path=None):
    """获取可用工具，根据 MCP 全局设置从 MCP 服务器或本地获取。"""
    if MCP:
        return mcp_get_tools(server_script_path)
    else:
        return local_get_tools(server_script_path)
    
def mcp_get_tools(server_script_path):
    """从 MCP 服务器获取可用工具。"""
    async def _get_tools():
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_response = await session.list_tools()
                return tools_response.tools
    
    return asyncio.run(_get_tools())

def local_get_tools(server_script_path=None):
    """一个简单的 get_tools 模拟实现，不使用 MCP。"""
    tools = [
        {
            "name": "add",
            "description": "将两个数字相加",
            "inputSchema": {
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"}
                },
                "required": ["a", "b"]
            }
        },
        {
            "name": "subtract",
            "description": "从 b 中减去 a",
            "inputSchema": {
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"}
                },
                "required": ["a", "b"]
            }
        },
        {
            "name": "multiply",
            "description": "将两个数字相乘",
            "inputSchema": {
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"}
                },
                "required": ["a", "b"]
            }
        },
        {
            "name": "divide",
            "description": "将 a 除以 b",
            "inputSchema": {
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"}
                },
                "required": ["a", "b"]
            }
        }
    ]

    class DictObject(dict):
        """一个简单的类，既可以作为字典，也可以作为具有属性的对象。"""
        def __init__(self, data):
            super().__init__(data)
            for key, value in data.items():
                if isinstance(value, dict):
                    self[key] = DictObject(value)
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    self[key] = [DictObject(item) for item in value]
        
        def __getattr__(self, key):
            try:
                return self[key]
            except KeyError:
                raise AttributeError(f"'DictObject' 对象没有属性 '{key}'")

    return [DictObject(tool) for tool in tools]

def call_tool(server_script_path=None, tool_name=None, arguments=None):
    """调用工具，根据 MCP 全局设置从 MCP 服务器或本地调用。"""
    if MCP:
        return mcp_call_tool(server_script_path, tool_name, arguments)
    else:
        return local_call_tool(server_script_path, tool_name, arguments)
    
def mcp_call_tool(server_script_path=None, tool_name=None, arguments=None):
    """在 MCP 服务器上调用工具。"""
    async def _call_tool():
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path]
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result.content[0].text
    
    return asyncio.run(_call_tool())

def local_call_tool(server_script_path=None, tool_name=None, arguments=None):
    """一个简单的 call_tool 模拟实现，不使用 MCP。"""
    # 工具的简单实现
    if tool_name == "add":
        if "a" in arguments and "b" in arguments:
            return arguments["a"] + arguments["b"]
        else:
            return "错误: 缺少必需参数 'a' 或 'b'"
    elif tool_name == "subtract":
        if "a" in arguments and "b" in arguments:
            return arguments["a"] - arguments["b"]
        else:
            return "错误: 缺少必需参数 'a' 或 'b'"
    elif tool_name == "multiply":
        if "a" in arguments and "b" in arguments:
            return arguments["a"] * arguments["b"]
        else:
            return "错误: 缺少必需参数 'a' 或 'b'"
    elif tool_name == "divide":
        if "a" in arguments and "b" in arguments:
            if arguments["b"] == 0:
                return "错误: 不允许除以零"
            return arguments["a"] / arguments["b"]
        else:
            return "错误: 缺少必需参数 'a' 或 'b'"
    else:
        return f"错误: 未知工具 '{tool_name}'"

if __name__ == "__main__":
    print("=== 正在测试 call_llm ===")
    prompt = "用几句话概括生命的意义是什么？"
    print(f"提示: {prompt}")
    response = call_llm(prompt)
    print(f"响应: {response}")

        # 查找可用工具
    print("=== 正在查找可用工具 ===")
    tools = get_tools("simple_server.py")
    
    # 漂亮地打印工具信息
    for i, tool in enumerate(tools, 1):
        print(f"\n工具 {i}: {tool.name}")
        print("=" * (len(tool.name) + 8))
        print(f"描述: {tool.description}")
        
        # 参数部分
        print("参数:")
        properties = tool.inputSchema.get('properties', {})
        required = tool.inputSchema.get('required', [])
        
        # 没有参数的情况
        if not properties:
            print("  无")
        
        # 打印每个参数及其详细信息
        for param_name, param_info in properties.items():
            param_type = param_info.get('type', 'unknown')
            req_status = "(必填)" if param_name in required else "(可选)"
            print(f"  • {param_name}: {param_type} {req_status}")
    
    # 调用工具
    print("\n=== 正在调用 add 工具 ===")
    a, b = 5, 3
    result = call_tool("simple_server.py", "add", {"a": a, "b": b})
    print(f"{a} + {b} 的结果 = {result}")
    
    # 您可以轻松地使用不同的参数调用
    a, b = 10, 20
    result = call_tool("simple_server.py", "add", {"a": a, "b": b})
    print(f"{a} + {b} 的结果 = {result}")


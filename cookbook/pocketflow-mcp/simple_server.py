from fastmcp import FastMCP

# 创建一个命名服务器
mcp = FastMCP("数学运算服务器")

# 定义数学运算工具
@mcp.tool()
def add(a: int, b: int) -> int:
    """将两个数字相加"""
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """从 a 中减去 b"""
    return a - b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """将两个数字相乘"""
    return a * b

@mcp.tool()
def divide(a: int, b: int) -> float:
    """将 a 除以 b"""
    if b == 0:
        raise ValueError("不允许除以零")
    return a / b

# 启动服务器
if __name__ == "__main__":
    mcp.run()
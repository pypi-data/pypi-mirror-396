from mcp.server.fastmcp import FastMCP

# 创建 FastMCP 实例，使用 streamable-http 传输
mcp = FastMCP(
    "Demo",
    host="127.0.0.1",  # 或 "0.0.0.0" 允许外部访问
    port=8000,         # 根据需要调整端口
)


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"



def main() -> None:
    mcp.run(transport="stdio")

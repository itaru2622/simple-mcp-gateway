"""
FastMCP Echo Server
cf. https://github.com/jlowin/fastmcp/blob/main/examples/echo.py
fastmcp run --server-spec thisfile.py --transport http --host 0.0.0.0 --port 8890
"""

from fastmcp import FastMCP

# Create server
mcp = FastMCP("Echo Server")


@mcp.tool
def echo_tool(text: str) -> str:
    """Echo the input text"""
    return text


@mcp.resource("echo://static")
def echo_resource() -> str:
    return "Echo!"


@mcp.resource("echo://{text}")
def echo_template(text: str) -> str:
    """Echo the input text"""
    return f"Echo: {text}"


@mcp.prompt("echo")
def echo_prompt(text: str) -> str:
    return text

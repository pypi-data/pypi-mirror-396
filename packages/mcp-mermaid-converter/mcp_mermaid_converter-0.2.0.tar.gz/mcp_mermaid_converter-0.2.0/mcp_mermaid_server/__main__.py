"""MCP Mermaid Converter - 主入口点

当包作为模块运行时使用：python -m mcp_mermaid_server
"""

from .server import mcp

if __name__ == "__main__":
    mcp.run()


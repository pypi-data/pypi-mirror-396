"""MCP Mermaid Converter - 主入口点

当包作为模块运行时使用：python -m mcp_mermaid_server
"""

import asyncio
from .server import main

if __name__ == "__main__":
    asyncio.run(main())


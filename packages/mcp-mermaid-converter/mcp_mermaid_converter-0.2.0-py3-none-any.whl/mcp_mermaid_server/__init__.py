"""MCP Mermaid转换服务器包

这个包提供了基于MCP协议的Mermaid图表转换服务。

主要功能：
- 将Mermaid文本转换为PNG或SVG图片
- 支持从文件读取Mermaid图表
- 基于Kroki.io API进行高质量渲染
- 提供MCP工具接口供AI助手调用

模块：
- server: MCP服务器实现
- converter: Mermaid转换核心逻辑
- exceptions: 自定义异常类
- logger: 日志配置
"""

__version__ = "0.2.0"
__author__ = "MCP Mermaid Converter Team"
__license__ = "MIT"

__all__ = ["server", "converter", "exceptions", "logger", "__version__"]


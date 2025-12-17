"""MCP Mermaid转换服务器

提供MCP工具来转换Mermaid图表为图片。
"""

import asyncio
import json
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import BaseModel, Field

from .converter import convert_mermaid_async


# 定义工具的输入参数模型
class ConvertMermaidFileParams(BaseModel):
    """转换Mermaid文件参数"""
    input_file: str = Field(description="Mermaid文件的路径（.mmd文件）")
    output_file: str = Field(description="输出图片文件的路径")
    format: str = Field(
        default="png",
        description="输出格式：png、svg或pdf"
    )


class ConvertMermaidTextParams(BaseModel):
    """转换Mermaid文本参数"""
    mermaid_text: str = Field(description="Mermaid图表的文本内容")
    output_file: str = Field(description="输出图片文件的路径")
    format: str = Field(
        default="png",
        description="输出格式：png、svg或pdf"
    )


# 创建MCP服务器实例
app = Server("mcp-mermaid-converter")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="convert_mermaid_file",
            description=(
                "将Mermaid图表文件（.mmd）转换为图片格式。"
                "支持PNG和SVG格式输出。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "Mermaid文件的路径（.mmd文件）"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "输出图片文件的路径"
                    },
                    "format": {
                        "type": "string",
                        "description": "输出格式：png或svg",
                        "enum": ["png", "svg"],
                        "default": "png"
                    }
                },
                "required": ["input_file", "output_file"]
            }
        ),
        Tool(
            name="convert_mermaid_text",
            description=(
                "将Mermaid图表文本直接转换为图片格式。"
                "支持PNG和SVG格式输出。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "mermaid_text": {
                        "type": "string",
                        "description": "Mermaid图表的文本内容"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "输出图片文件的路径"
                    },
                    "format": {
                        "type": "string",
                        "description": "输出格式：png或svg",
                        "enum": ["png", "svg"],
                        "default": "png"
                    }
                },
                "required": ["mermaid_text", "output_file"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """处理工具调用"""
    
    if name == "convert_mermaid_file":
        # 验证参数
        params = ConvertMermaidFileParams(**arguments)
        
        try:
            # 读取Mermaid文件
            input_path = Path(params.input_file)
            if not input_path.exists():
                return [TextContent(
                    type="text",
                    text=f"错误：输入文件不存在: {params.input_file}"
                )]
            
            mermaid_text = input_path.read_text(encoding='utf-8')
            
            # 转换为图片
            image_data = await convert_mermaid_async(
                mermaid_text,
                params.format,  # type: ignore
                timeout=60
            )
            
            # 保存文件
            output_path = Path(params.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(image_data)
            
            return [TextContent(
                type="text",
                text=(
                    f"成功将 {params.input_file} 转换为 {params.format.upper()} 格式！\n"
                    f"输出文件: {params.output_file}\n"
                    f"文件大小: {len(image_data)} 字节"
                )
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"转换失败: {str(e)}"
            )]
    
    elif name == "convert_mermaid_text":
        # 验证参数
        params = ConvertMermaidTextParams(**arguments)
        
        try:
            # 转换为图片
            image_data = await convert_mermaid_async(
                params.mermaid_text,
                params.format,  # type: ignore
                timeout=60
            )
            
            # 保存文件
            output_path = Path(params.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(image_data)
            
            return [TextContent(
                type="text",
                text=(
                    f"成功将Mermaid文本转换为 {params.format.upper()} 格式！\n"
                    f"输出文件: {params.output_file}\n"
                    f"文件大小: {len(image_data)} 字节"
                )
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"转换失败: {str(e)}"
            )]
    
    else:
        return [TextContent(
            type="text",
            text=f"未知工具: {name}"
        )]


async def main():
    """主函数：启动MCP服务器"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())


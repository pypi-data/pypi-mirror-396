"""MCP Mermaid转换服务器

提供MCP工具来转换Mermaid图表为图片。

这个模块使用FastMCP实现MCP服务器，提供两个工具：
1. convert_mermaid_file - 从文件转换
2. convert_mermaid_text - 从文本转换
"""

from pathlib import Path
from typing import Literal

from fastmcp import FastMCP

from .converter import convert_mermaid_async
from .exceptions import MermaidConverterError
from .logger import get_logger

logger = get_logger(__name__)

# 创建FastMCP应用实例
mcp = FastMCP("mcp-mermaid-converter")


@mcp.tool()
async def convert_mermaid_file(
    input_file: str,
    output_file: str,
    format: Literal["png", "svg"] = "png"
) -> str:
    """将Mermaid图表文件（.mmd）转换为图片格式。支持PNG和SVG格式输出。
    
    Args:
        input_file: Mermaid文件的路径（.mmd文件）
        output_file: 输出图片文件的路径
        format: 输出格式：png或svg，默认为png
        
    Returns:
        转换成功的消息，包含输出文件路径和文件大小
        
    Raises:
        MermaidConverterError: 转换失败时抛出
    """
    logger.info(f"Tool called: convert_mermaid_file")
    logger.debug(f"Arguments: input_file={input_file}, output_file={output_file}, format={format}")
    
    try:
        # 读取Mermaid文件
        input_path = Path(input_file)
        if not input_path.exists():
            error_msg = f"错误：输入文件不存在: {input_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        mermaid_text = input_path.read_text(encoding='utf-8')
        logger.debug(f"Read {len(mermaid_text)} characters from {input_path}")
        
        # 转换为图片
        image_data = await convert_mermaid_async(
            mermaid_text,
            format,
            timeout=60
        )
        
        # 保存文件
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(image_data)
        
        success_msg = (
            f"✓ 成功将 {input_file} 转换为 {format.upper()} 格式！\n"
            f"输出文件: {output_file}\n"
            f"文件大小: {len(image_data):,} 字节"
        )
        logger.info(success_msg)
        
        return success_msg
        
    except MermaidConverterError as e:
        error_msg = f"转换失败: {str(e)}"
        logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"未预期的错误: {str(e)}"
        logger.exception(error_msg)
        raise


@mcp.tool()
async def convert_mermaid_text(
    mermaid_text: str,
    output_file: str,
    format: Literal["png", "svg"] = "png"
) -> str:
    """将Mermaid图表文本直接转换为图片格式。支持PNG和SVG格式输出。
    
    Args:
        mermaid_text: Mermaid图表的文本内容
        output_file: 输出图片文件的路径
        format: 输出格式：png或svg，默认为png
        
    Returns:
        转换成功的消息，包含输出文件路径和文件大小
        
    Raises:
        MermaidConverterError: 转换失败时抛出
    """
    logger.info(f"Tool called: convert_mermaid_text")
    logger.debug(f"Arguments: output_file={output_file}, format={format}")
    
    try:
        # 转换为图片
        image_data = await convert_mermaid_async(
            mermaid_text,
            format,
            timeout=60
        )
        
        # 保存文件
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(image_data)
        
        success_msg = (
            f"✓ 成功将Mermaid文本转换为 {format.upper()} 格式！\n"
            f"输出文件: {output_file}\n"
            f"文件大小: {len(image_data):,} 字节"
        )
        logger.info(success_msg)
        
        return success_msg
        
    except MermaidConverterError as e:
        error_msg = f"转换失败: {str(e)}"
        logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"未预期的错误: {str(e)}"
        logger.exception(error_msg)
        raise


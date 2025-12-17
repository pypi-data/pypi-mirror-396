"""Mermaid图表转换器

使用Kroki.io API将Mermaid图表转换为图片格式。

主要类：
- MermaidConverter: 同步转换器类

主要函数：
- convert_mermaid_async: 异步转换函数
"""

from __future__ import annotations

import base64
import httpx
from pathlib import Path
from typing import Literal, Optional, Union
import zlib

from .exceptions import (
    InvalidFormatError,
    NetworkError,
    APIError,
    ConversionError,
    FileNotFoundError as MermaidFileNotFoundError
)
from .logger import get_logger

logger = get_logger(__name__)


class MermaidConverter:
    """Mermaid到图片的转换器"""

    KROKI_BASE_URL = "https://kroki.io"
    SUPPORTED_FORMATS = ["png", "svg"]  # Kroki的Mermaid仅支持PNG和SVG

    def __init__(self, timeout: int = 30):
        """初始化转换器
        
        Args:
            timeout: HTTP请求超时时间（秒）
        """
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        logger.debug(f"MermaidConverter initialized with timeout={timeout}s")

    def __del__(self):
        """清理HTTP客户端"""
        if hasattr(self, 'client'):
            self.client.close()

    def encode_diagram(self, diagram_text: str) -> str:
        """将Mermaid文本编码为Kroki所需的格式
        
        Args:
            diagram_text: Mermaid图表文本
            
        Returns:
            编码后的字符串
            
        Raises:
            ConversionError: 编码失败
        """
        try:
            # Kroki使用deflate压缩 + base64编码
            compressed = zlib.compress(diagram_text.encode('utf-8'), level=9)
            # 使用URL安全的base64编码
            encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')
            logger.debug(f"Diagram encoded, original length: {len(diagram_text)}, "
                        f"encoded length: {len(encoded)}")
            return encoded
        except Exception as e:
            logger.error(f"Failed to encode diagram: {e}")
            raise ConversionError(f"图表编码失败: {str(e)}") from e

    def convert_text(
        self,
        mermaid_text: str,
        output_format: Literal["png", "svg"] = "png"
    ) -> bytes:
        """将Mermaid文本转换为图片
        
        Args:
            mermaid_text: Mermaid图表文本
            output_format: 输出格式（png或svg）
            
        Returns:
            图片的二进制数据
            
        Raises:
            InvalidFormatError: 不支持的输出格式
            NetworkError: 网络请求失败
            APIError: Kroki API返回错误
        """
        if output_format not in self.SUPPORTED_FORMATS:
            raise InvalidFormatError(
                f"不支持的格式: {output_format}。"
                f"支持的格式: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        logger.info(f"Converting Mermaid diagram to {output_format}")
        
        # 编码Mermaid文本
        encoded = self.encode_diagram(mermaid_text)

        # 构建Kroki API URL
        url = f"{self.KROKI_BASE_URL}/mermaid/{output_format}/{encoded}"
        logger.debug(f"Requesting URL: {url[:100]}...")

        # 发送请求
        try:
            response = self.client.get(url)
            response.raise_for_status()
            logger.info(f"Successfully converted diagram, size: {len(response.content)} bytes")
            return response.content
        except httpx.HTTPStatusError as e:
            error_msg = f"Kroki API返回错误: {e.response.status_code}"
            if e.response.text:
                error_msg += f" - {e.response.text}"
            logger.error(error_msg)
            raise APIError(error_msg, e.response.status_code, e.response.text) from e
        except httpx.RequestError as e:
            error_msg = f"网络请求失败: {str(e)}"
            logger.error(error_msg)
            raise NetworkError(error_msg) from e

    def convert_file(
        self,
        input_file: str | Path,
        output_file: str | Path,
        output_format: Optional[Literal["png", "svg"]] = None
    ) -> Path:
        """将Mermaid文件转换为图片文件
        
        Args:
            input_file: 输入的.mmd文件路径
            output_file: 输出的图片文件路径
            output_format: 输出格式，如果为None则从output_file扩展名推断
            
        Returns:
            输出文件的路径
            
        Raises:
            MermaidFileNotFoundError: 输入文件不存在
            InvalidFormatError: 无法确定输出格式
        """
        input_path = Path(input_file)
        output_path = Path(output_file)

        logger.info(f"Converting file: {input_path} -> {output_path}")

        # 检查输入文件是否存在
        if not input_path.exists():
            error_msg = f"输入文件不存在: {input_path}"
            logger.error(error_msg)
            raise MermaidFileNotFoundError(error_msg)

        # 读取Mermaid文件内容
        try:
            mermaid_text = input_path.read_text(encoding='utf-8')
            logger.debug(f"Read {len(mermaid_text)} characters from {input_path}")
        except Exception as e:
            error_msg = f"读取文件失败: {str(e)}"
            logger.error(error_msg)
            raise ConversionError(error_msg) from e

        # 确定输出格式
        if output_format is None:
            # 从输出文件扩展名推断格式
            ext = output_path.suffix.lower().lstrip('.')
            if ext not in self.SUPPORTED_FORMATS:
                raise InvalidFormatError(
                    f"无法从文件扩展名 '.{ext}' 推断输出格式。"
                    f"请明确指定format参数或使用以下扩展名: "
                    f"{', '.join('.' + f for f in self.SUPPORTED_FORMATS)}"
                )
            output_format = ext  # type: ignore
            logger.debug(f"Inferred output format from extension: {output_format}")

        # 转换
        image_data = self.convert_text(mermaid_text, output_format)

        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        try:
            output_path.write_bytes(image_data)
            logger.info(f"Successfully wrote {len(image_data)} bytes to {output_path}")
        except Exception as e:
            error_msg = f"写入文件失败: {str(e)}"
            logger.error(error_msg)
            raise ConversionError(error_msg) from e

        return output_path


async def convert_mermaid_async(
    mermaid_text: str,
    output_format: Literal["png", "svg"] = "png",
    timeout: int = 30
) -> bytes:
    """异步版本：将Mermaid文本转换为图片
    
    Args:
        mermaid_text: Mermaid图表文本
        output_format: 输出格式
        timeout: 超时时间
        
    Returns:
        图片的二进制数据
        
    Raises:
        InvalidFormatError: 不支持的输出格式
        NetworkError: 网络请求失败
        APIError: Kroki API返回错误
    """
    if output_format not in MermaidConverter.SUPPORTED_FORMATS:
        raise InvalidFormatError(f"不支持的格式: {output_format}")

    logger.info(f"Converting Mermaid diagram to {output_format} (async)")
    
    converter = MermaidConverter(timeout=timeout)
    encoded = converter.encode_diagram(mermaid_text)
    url = f"{converter.KROKI_BASE_URL}/mermaid/{output_format}/{encoded}"
    
    logger.debug(f"Requesting URL (async): {url[:100]}...")

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            logger.info(f"Successfully converted diagram (async), size: {len(response.content)} bytes")
            return response.content
        except httpx.HTTPStatusError as e:
            error_msg = f"Kroki API返回错误: {e.response.status_code}"
            if e.response.text:
                error_msg += f" - {e.response.text}"
            logger.error(error_msg)
            raise APIError(error_msg, e.response.status_code, e.response.text) from e
        except httpx.RequestError as e:
            error_msg = f"网络请求失败: {str(e)}"
            logger.error(error_msg)
            raise NetworkError(error_msg) from e


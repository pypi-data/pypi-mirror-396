"""Mermaid转换器测试"""

import pytest
from pathlib import Path
from mcp_mermaid_server.converter import MermaidConverter, convert_mermaid_async


class TestMermaidConverter:
    """MermaidConverter测试类"""
    
    @pytest.fixture
    def converter(self):
        """创建转换器实例"""
        return MermaidConverter(timeout=30)
    
    @pytest.fixture
    def sample_mermaid(self):
        """示例Mermaid文本"""
        return """
graph TD
    A[开始] --> B[处理]
    B --> C[结束]
"""
    
    def test_encode_diagram(self, converter, sample_mermaid):
        """测试图表编码"""
        encoded = converter.encode_diagram(sample_mermaid)
        assert isinstance(encoded, str)
        assert len(encoded) > 0
    
    @pytest.mark.asyncio
    async def test_convert_text_png(self, sample_mermaid):
        """测试转换为PNG"""
        result = await convert_mermaid_async(sample_mermaid, "png")
        assert isinstance(result, bytes)
        assert len(result) > 0
        # PNG文件应该以特定的魔术数字开头
        assert result[:8] == b'\x89PNG\r\n\x1a\n'
    
    @pytest.mark.asyncio
    async def test_convert_text_svg(self, sample_mermaid):
        """测试转换为SVG"""
        result = await convert_mermaid_async(sample_mermaid, "svg")
        assert isinstance(result, bytes)
        assert len(result) > 0
        # SVG应该包含XML标记
        assert b'<svg' in result or b'<?xml' in result
    
    @pytest.mark.asyncio
    async def test_invalid_format(self, sample_mermaid):
        """测试无效格式"""
        with pytest.raises(ValueError, match="不支持的格式"):
            await convert_mermaid_async(sample_mermaid, "pdf")  # type: ignore
    
    def test_supported_formats(self, converter):
        """测试支持的格式列表"""
        assert "png" in converter.SUPPORTED_FORMATS
        assert "svg" in converter.SUPPORTED_FORMATS


class TestEdgeCases:
    """边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_empty_diagram(self):
        """测试空图表"""
        with pytest.raises(Exception):
            await convert_mermaid_async("", "png")
    
    @pytest.mark.asyncio
    async def test_complex_diagram(self):
        """测试复杂图表"""
        complex_mermaid = """
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: 你好，Bob！
    Bob-->>Alice: 你好，Alice！
    Alice->>Bob: 最近怎么样？
    Bob-->>Alice: 很好，谢谢！
"""
        result = await convert_mermaid_async(complex_mermaid, "svg")
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_chinese_content(self):
        """测试中文内容"""
        chinese_mermaid = """
graph LR
    开始 --> 处理数据
    处理数据 --> 结束
"""
        result = await convert_mermaid_async(chinese_mermaid, "png")
        assert isinstance(result, bytes)
        assert len(result) > 0


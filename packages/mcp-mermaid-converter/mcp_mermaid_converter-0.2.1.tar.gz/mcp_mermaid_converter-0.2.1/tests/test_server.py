"""MCP服务器测试"""

import pytest
from mcp_mermaid_server.server import ConvertMermaidTextParams, ConvertMermaidFileParams


class TestParamModels:
    """参数模型测试"""
    
    def test_convert_text_params_valid(self):
        """测试有效的文本转换参数"""
        params = ConvertMermaidTextParams(
            mermaid_text="graph TD\nA-->B",
            output_file="output.png",
            format="png"
        )
        assert params.mermaid_text == "graph TD\nA-->B"
        assert params.output_file == "output.png"
        assert params.format == "png"
    
    def test_convert_text_params_default_format(self):
        """测试默认格式"""
        params = ConvertMermaidTextParams(
            mermaid_text="graph TD\nA-->B",
            output_file="output.png"
        )
        assert params.format == "png"
    
    def test_convert_file_params_valid(self):
        """测试有效的文件转换参数"""
        params = ConvertMermaidFileParams(
            input_file="input.mmd",
            output_file="output.svg",
            format="svg"
        )
        assert params.input_file == "input.mmd"
        assert params.output_file == "output.svg"
        assert params.format == "svg"
    
    def test_missing_required_field(self):
        """测试缺少必需字段"""
        with pytest.raises(Exception):
            ConvertMermaidTextParams(output_file="output.png")  # type: ignore


class TestToolDefinitions:
    """工具定义测试"""
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """测试列出工具"""
        from mcp_mermaid_server.server import list_tools
        
        tools = await list_tools()
        assert len(tools) == 2
        
        tool_names = [tool.name for tool in tools]
        assert "convert_mermaid_file" in tool_names
        assert "convert_mermaid_text" in tool_names
        
        # 验证工具schema
        for tool in tools:
            assert "inputSchema" in tool.model_dump()
            assert tool.description is not None


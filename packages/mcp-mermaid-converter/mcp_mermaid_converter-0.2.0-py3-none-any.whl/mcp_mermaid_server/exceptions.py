"""自定义异常类

定义了MCP Mermaid Converter的自定义异常类型。
"""


class MermaidConverterError(Exception):
    """Mermaid转换器基础异常类"""
    pass


class InvalidFormatError(MermaidConverterError):
    """无效的输出格式异常"""
    pass


class FileNotFoundError(MermaidConverterError):
    """文件不存在异常"""
    pass


class NetworkError(MermaidConverterError):
    """网络请求异常"""
    pass


class APIError(MermaidConverterError):
    """API调用异常"""
    
    def __init__(self, message: str, status_code: int = None, response_text: str = None):
        """初始化API异常
        
        Args:
            message: 错误消息
            status_code: HTTP状态码
            response_text: API响应文本
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class ConversionError(MermaidConverterError):
    """转换过程异常"""
    pass


class InvalidDiagramError(MermaidConverterError):
    """无效的Mermaid图表异常"""
    pass


# MCP Mermaid Converter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

一个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io) 的 Mermaid 图表转换服务，可以将 Mermaid 图表文本转换为 PNG 或 SVG 格式的图片。

## ✨ 特性

- 🎨 支持将 Mermaid 文本直接转换为图片
- 📁 支持从 .mmd 文件读取并转换
- 🖼️ 支持 PNG 和 SVG 两种输出格式
- ⚡ 基于 MCP 协议，可与支持 MCP 的 AI 助手集成
- 🌐 使用 [Kroki.io](https://kroki.io) API 进行高质量图表渲染
- 🔧 简单易用，零配置即可开始使用

## 📦 安装

### 使用 uvx（推荐）

```bash
uvx mcp-mermaid-converter
```

### 使用 pip

```bash
pip install mcp-mermaid-converter
```

### 从源码安装

```bash
git clone https://github.com/yourusername/mcp-mermaid-converter.git
cd mcp-mermaid-converter
pip install -e .
```

## 🚀 快速开始

### 作为 MCP 服务器运行

将以下配置添加到你的 MCP 客户端配置文件中（如 Cursor 的 `cursor_mcp_config.json` 或 Claude Desktop 的配置文件）：

```json
{
  "mcpServers": {
    "mcp-mermaid-converter": {
      "command": "uvx",
      "args": ["mcp-mermaid-converter"]
    }
  }
}
```

### 使用示例

#### 转换 Mermaid 文本

```python
# 通过 MCP 客户端调用
convert_mermaid_text(
    mermaid_text="""
    graph TD
        A[开始] --> B[处理]
        B --> C[结束]
    """,
    output_file="diagram.png",
    format="png"
)
```

#### 转换 Mermaid 文件

```python
# 通过 MCP 客户端调用
convert_mermaid_file(
    input_file="diagram.mmd",
    output_file="diagram.svg",
    format="svg"
)
```

## 🛠️ MCP 工具说明

### convert_mermaid_text

将 Mermaid 图表文本直接转换为图片格式。

**参数：**
- `mermaid_text` (string, 必需): Mermaid 图表的文本内容
- `output_file` (string, 必需): 输出图片文件的路径
- `format` (string, 可选): 输出格式，支持 `png` 或 `svg`，默认为 `png`

**返回：**
成功消息，包含输出文件路径和文件大小。

### convert_mermaid_file

将 Mermaid 图表文件（.mmd）转换为图片格式。

**参数：**
- `input_file` (string, 必需): Mermaid 文件的路径（.mmd 文件）
- `output_file` (string, 必需): 输出图片文件的路径
- `format` (string, 可选): 输出格式，支持 `png` 或 `svg`，默认为 `png`

**返回：**
成功消息，包含输出文件路径和文件大小。

## 📝 支持的 Mermaid 图表类型

该服务支持所有 Mermaid 官方支持的图表类型，包括但不限于：

- 流程图 (Flowchart)
- 序列图 (Sequence Diagram)
- 类图 (Class Diagram)
- 状态图 (State Diagram)
- 实体关系图 (ER Diagram)
- 甘特图 (Gantt Chart)
- 饼图 (Pie Chart)
- Git 图 (Git Graph)
- 思维导图 (Mindmap)
- 时间线 (Timeline)

## 🔧 配置示例

### Cursor 配置

在 Cursor 中使用，创建或编辑 `cursor_mcp_config.json`：

```json
{
  "mcpServers": {
    "mcp-mermaid-converter": {
      "command": "uvx",
      "args": ["mcp-mermaid-converter"],
      "env": {}
    }
  }
}
```

### Claude Desktop 配置

在 Claude Desktop 中使用，编辑配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mcp-mermaid-converter": {
      "command": "uvx",
      "args": ["mcp-mermaid-converter"]
    }
  }
}
```

## 🌐 依赖服务

本服务使用 [Kroki.io](https://kroki.io) 提供的免费 API 进行图表渲染。Kroki 是一个开源项目，支持多种图表格式的转换。

**注意事项：**
- 需要网络连接才能使用转换功能
- 大型复杂图表可能需要较长的转换时间
- 建议合理使用，避免频繁请求

## 🔐 隐私说明

- 转换过程中，Mermaid 文本会被发送到 Kroki.io API 进行渲染
- Kroki.io 不会存储你的图表内容
- 生成的图片会保存在你指定的本地路径

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Model Context Protocol](https://modelcontextprotocol.io) - 强大的 AI 助手集成协议
- [Kroki.io](https://kroki.io) - 提供图表渲染服务
- [Mermaid](https://mermaid.js.org) - 强大的文本到图表工具

## 📮 联系方式

- 项目主页: https://github.com/yourusername/mcp-mermaid-converter
- 问题反馈: https://github.com/yourusername/mcp-mermaid-converter/issues

---

如果这个项目对你有帮助，请给一个 ⭐️ Star！


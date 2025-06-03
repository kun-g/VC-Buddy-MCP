<h1 align="center">Vibe Coding Buddy <sup>🚀 MCP Edition</sup></h1>
<p align="center">
  <em>A modern AI-powered coding assistant for your Vibe Coding</em><br>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue.svg"/></a>
  <a href="#"><img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-yellow.svg"/></a>
  <!-- <a href="#"><img alt="CI" src="https://github.com/kun/vc-buddy/actions/workflows/ci.yml/badge.svg"/></a> -->
</p>

## ✨ 功能特性

- 🔄 **MCP 协议**：支持 stdio 
- 🎨 **现代 UI**：PySide6 构建的响应式界面
- 🎤 **语音交互**：录音转文字

## 🚀 快速开始

### 1. 环境准备

确保安装了以下工具：
- **Python 3.11+**
- **uv** (推荐的包管理器)

### 2. 一键安装

```bash
# 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone <repo-url>
cd VC-Buddy-MCP

# 🎉 一键安装所有依赖（包括系统级依赖）
make install
```

**智能依赖安装说明：**
- **macOS**: 自动使用 Homebrew 安装 `portaudio`
- **Ubuntu/Debian**: 自动安装 `portaudio19-dev python3-dev`
- **CentOS/RHEL**: 自动安装 `portaudio-devel python3-devel`  
- **Fedora**: 自动安装 `portaudio-devel python3-devel`
- **Arch Linux**: 自动安装 `portaudio`

如果只想安装系统依赖：
```bash
make install-system-deps
```

### 3. 配置 MCP 服务器

本项目提供了基于 **FastMCP** 的服务器实现，支持交互式反馈功能。

#### 3.1 启动 MCP 服务器

**开发模式（推荐）**
```bash
# 启动开发模式，包含 MCP Inspector 界面
make dev
# 或者
uv run fastmcp dev buddy/server/main.py
```

**标准 stdio 模式**
```bash
# 直接运行 MCP 服务器（stdio 传输）
uv run python buddy/server/main.py
```

#### 3.2 配置客户端连接

**方式一：Claude Desktop 配置**

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "vibe-coding-buddy": {
      "command": "uv",
      "args": ["run", "python", "buddy/server/main.py"],
      "cwd": "/path/to/VC-Buddy-MCP"
    }
  }
}
```

**方式二：直接测试**

```bash
# 测试客户端连接
uv run python buddy/client/test.py
```

#### 3.3 可用工具

MCP 服务器提供以下工具：

- **ask_for_feedback**: 向用户请求交互式反馈
  - 参数：`summary` (必需) - 反馈请求描述
  - 参数：`project_directory` (可选) - 项目目录路径
  - 返回：用户反馈的 JSON 格式字符串

#### 3.4 环境变量配置

```bash
# 可选：自定义配置文件路径
export VC_BUDDY_CONFIG="/path/to/your/config.json"

# 可选：自定义组织信息
export VC_BUDDY_ORG="Your-Organization"
export VC_BUDDY_APP_NAME="Your-App-Name"
```

#### 3.5 验证安装

```bash
# 测试 MCP 服务器和工具
uv run python buddy/client/test.py

# 检查服务器是否正常启动
echo '{"method": "tools/list"}' | uv run python buddy/server/main.py
```

### 4. 调试

## 🔧 开发工具

```bash
make dev           # 等同于 uv run dev
make fastmcp       # 等同于 uv run fastmcp
make test-fastmcp  # 等同于 uv run test-fastmcp
# ... 其他命令
```

## 🔧 MCP 接口说明

## 🔊 语音功能

GUI 支持录音转文字功能：

1. 点击麦克风按钮开始录音
2. 再次点击停止录音
3. 自动调用 Whisper API 转写文字
4. 转写结果填入输入框

## 🧪 测试

```bash
# 运行所有测试
make test

# 运行特定测试
uv run pytest buddy/tests/test_basic.py -v

# 生成覆盖率报告
uv run pytest --cov=buddy --cov-report=html
```

## 🔍 代码质量

```bash
# 代码格式化
make format

# 代码检查
make lint

# 类型检查
uv run mypy .
```

## 📚 开发指南

### 添加新的 AI 提供商

1. 在 `buddy/core/ai_provider.py` 中继承 `BaseProvider`
2. 实现 `send_chat` 和 `transcribe_audio` 方法
3. 在 `ProviderFactory.PROVIDERS` 中注册

### 添加新的 Prompt 流

1. 在 `buddy/data/prompts.json` 中添加新流配置
2. 定义 `system_prompt` 和 `user_prompt_template`
3. 设置适当的参数（temperature、max_tokens 等）

### 扩展 GUI 功能

1. 在 `buddy/ui/main_window.py` 中添加新组件
2. 使用 Qt 信号槽机制处理交互

## 🐛 故障排除

### 常见问题

**1. 音频依赖安装失败**
如果 `make install` 自动安装失败，请手动安装：
```bash
# macOS
brew install portaudio

# Ubuntu/Debian  
sudo apt-get install portaudio19-dev python3-dev

# CentOS/RHEL
sudo yum install portaudio-devel python3-devel

# Fedora
sudo dnf install portaudio-devel python3-devel

# Arch Linux
sudo pacman -S portaudio
```
然后重新运行：`make install`

**2. OpenAI API 错误**
- 检查 `OPENAI_API_KEY` 环境变量
- 确认 API 密钥有效且有余额
- 检查网络连接

**3. GUI 无法启动**
- 确认安装了 PySide6：`uv add PySide6`
- 检查显示环境（Linux 需要 X11 或 Wayland）
- 查看错误日志

**4. MCP 服务器连接失败**
- 确认服务器正在运行：`curl http://localhost:8000/health`
- 检查端口是否被占用
- 查看服务器日志

## 🚧 TODO 清单

### 短期目标
- [ ] 完善 Anthropic Provider 实现
- [ ] 添加 Ollama Provider 支持
- [ ] 实现会话持久化（Redis）
- [ ] 添加更多语音格式支持

### 中期目标
- [ ] 插件系统架构
- [ ] 自定义主题支持
- [ ] 多语言界面
- [ ] 云同步功能

### 长期目标
- [ ] 完整的 Prompt Flow UI 编辑器
- [ ] 代码分析和建议
- [ ] 项目模板生成
- [ ] 团队协作功能

## 📄 许可证

本项目基于 [MIT License](./LICENSE) 开源许可证发布。

---

**享受与 Vibe Coding Buddy 的编程之旅！** 🎉
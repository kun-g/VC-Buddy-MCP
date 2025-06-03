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

### 3. 配置 MCP 服务器

**Cursor**
```bash
make mcp-cursor
```
按照提示，复制配置到对应的配置文件里。

**🔧 Cursor IDE**
- [官方 MCP 配置文档](https://docs.cursor.com/context/model-context-protocol)
- [MCP 服务器配置指南](https://docs.cursor.com/guides/advanced/working-with-documentation)

### 4. 设置 Cursor Rule

**🎯 自动设置（推荐）**
```bash
# 使用 CLI 工具一键设置项目环境
uvx --from vibe-coding-buddy vcbuddy setup .

# 或者从源码运行
uv run --module buddy.cli setup .
```

**📝 手动设置**
将以下内容放到 User Rules 里
```
Whenever you want to ask a question, always call the MCP `vc-buddy`.
Whenever you're about to complete a user request, call the MCP `vc-buddy` instead of simply ending the process. Keep calling MCP until the user's feedback is empty, then end the request.
```

> 💡 **提示**: 使用 CLI 工具可以自动配置完整的开发规范，包括项目结构管理和单元测试规范。详见 [CLI 使用指南](docs/CLI_GUIDE.md)。

### 5. 基本使用

#### 5.1 GUI 界面使用

1. **文本输入**: 在输入框中输入您的问题或需求
2. **语音输入**: 点击麦克风按钮开始录音，支持实时转写
3. **发送消息**: 点击发送按钮或使用快捷键 `Ctrl+E`
4. **TODO 管理**: 自动解析回复中的 TODO 项目，支持标记完成状态

#### 5.2 快捷键

- `Ctrl+E`: 发送消息
- `Ctrl+R`: 开始/停止录音
- `Ctrl+,`: 打开设置

#### 5.3 配置 API Key

首次使用需要配置 OpenAI API Key：

快捷键`Ctrl+,`，输入你的 Key，点击【测试链接】按钮。

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

## 📄 许可证

本项目基于 [MIT License](./LICENSE) 开源许可证发布。

---

**享受与 Vibe Coding Buddy 的编程之旅！** 🎉

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

```bash
make mcp-config
```
按照提示，复制配置到对应的配置文件里。

以下是主流 AI 编程软件的 MCP 配置文档链接：

**🔧 Cursor IDE**
- [官方 MCP 配置文档](https://docs.cursor.com/context/model-context-protocol)
- [MCP 服务器配置指南](https://docs.cursor.com/guides/advanced/working-with-documentation)

**🤖 Claude Desktop**
- [官方 MCP 用户指南](https://modelcontextprotocol.io/quickstart/user)
- [MCP 服务器安装教程](https://docs.mcp.run/mcp-clients/claude-desktop/)

### 4. 启动应用程序

安装完成后，您可以通过以下方式启动应用：

**方式一：启动 GUI 界面**
```bash
# 启动 QML 版本界面（推荐）
make show-ui

# 或者直接运行
uv run buddy/ui/answer_box_qml.py
```

**方式二：启动开发模式**
```bash
# 启动开发模式，包含 MCP Inspector 界面
make dev
```

**方式三：测试语音功能**
```bash
# 启动语音测试工具
make test-voice
```

### 5. 基本使用

#### 5.1 GUI 界面使用

1. **文本输入**: 在输入框中输入您的问题或需求
2. **语音输入**: 点击麦克风按钮开始录音，支持实时转写
3. **发送消息**: 点击发送按钮或使用快捷键 `Ctrl+Enter`
4. **查看回复**: AI 回复会显示在下方区域，支持 Markdown 渲染
5. **TODO 管理**: 自动解析回复中的 TODO 项目，支持标记完成状态

#### 5.2 语音功能设置

1. 点击界面上的"语音设置"按钮
2. 配置自定义语音命令：
   - **停止命令**: "我说完了"、"结束"、"stop" 等
   - **发送命令**: "开工吧"、"发送"、"go" 等
3. 选择录音模式：
   - **传统模式**: 录音完成后一次性转写
   - **流式模式**: 实时转写，边说边显示

#### 5.3 快捷键

- `Ctrl+Enter`: 发送消息
- `Ctrl+R`: 开始/停止录音
- `Ctrl+,`: 打开设置
- `Esc`: 取消当前操作

#### 5.4 配置 API Key

首次使用需要配置 OpenAI API Key：

**方式一：通过环境变量**
```bash
# 设置 OpenAI API Key
export OPENAI_API_KEY="your-api-key-here"

# 可选：设置自定义 API URL（如使用第三方服务）
export OPENAI_API_URL="https://your-api-server.com/v1"
```

**方式二：通过设置界面**
```bash
# 启动设置对话框
uv run tools/settings_dialog.py
```

**方式三：通过配置文件**
在用户目录下创建 `.vc-buddy-config.json` 文件：
```json
{
  "openai_api_key": "your-api-key-here",
  "openai_api_url": "https://api.openai.com/v1"
}
```

#### 5.5 常见使用场景

**代码助手模式**
- 输入代码问题，获得详细解答和示例
- 支持多种编程语言的代码分析和优化建议
- 自动生成 TODO 列表，帮助规划开发任务

**项目管理模式**
- 描述项目需求，获得结构化的开发计划
- TODO 项目自动解析，支持勾选完成状态
- 支持项目进度跟踪和任务管理

**学习助手模式**
- 提出技术问题，获得深入浅出的解释
- 支持语音提问，提高学习效率
- 自动整理学习要点和练习建议

**快速原型模式**
- 描述功能需求，快速生成代码原型
- 支持多种框架和技术栈
- 提供完整的实现方案和部署指导

### 6. 调试

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

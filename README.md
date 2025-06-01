# Vibe Coding Buddy - MCP

一个现代化的桌面编程助手，基于 **MCP (Model Context Protocol)** 和 **PySide6**，提供智能对话、语音交互和命令执行功能。现在支持 **FastMCP** 框架！

 受启发于[interactive-feedback-mcp](https://github.com/noopstudios/interactive-feedback-mcp)

## ✨ 功能特性

- 🔄 **MCP 协议**：支持 stdio 
- 🎨 **现代 UI**：PySide6 构建的响应式界面
- 🎤 **语音交互**：录音转文字（Whisper API）

## 🚀 快速开始

### 1. 环境准备

确保安装了以下工具：
- **Python 3.11+**
- **uv** (推荐的包管理器)

```bash
# 安装 uv (如果尚未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆项目
git clone <repo-url>
cd VC-Buddy-MCP
```

### 2. 安装依赖

```bash
# 使用 uv 安装所有依赖
make install
# 或者直接运行
uv sync
```

### 3. 安装MCP

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

**1. PyAudio 安装失败**
```bash
# macOS
brew install portaudio
uv add pyaudio

# Ubuntu/Debian
sudo apt-get install portaudio19-dev
uv add pyaudio
```

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

MIT License - 详见 LICENSE 文件

---

**享受与 Vibe Coding Buddy 的编程之旅！** 🎉
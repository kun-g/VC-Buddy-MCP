# Vibe Coding Buddy - MCP

一个现代化的桌面编程助手，基于 **MCP (Model Context Protocol)** 和 **PySide6**，提供智能对话、语音交互和命令执行功能。现在支持 **FastMCP** 框架！

## ✨ 功能特性

- 🤖 **多 AI 提供商支持**：OpenAI、Anthropic、Ollama
- 🎤 **语音交互**：录音转文字（Whisper API）
- 💬 **实时对话**：基于 SSE 的流式响应
- ⚡ **命令执行**：内置 pytest 等命令支持
- 🔄 **MCP 协议**：支持 SSE、stdio 和 **FastMCP** 三种传输模式
- 🎨 **现代 UI**：PySide6 构建的响应式界面
- 📝 **Prompt 流管理**：多种对话模式（代码审查、调试、测试等）
- 🚀 **FastMCP 支持**：更简洁的 MCP 服务器和客户端开发体验

## 🏗️ 项目结构

```
VC-Buddy-MCP/
├── buddy/                          # 主要代码包
│   ├── core/                       # 核心模块
│   │   ├── ai_provider.py         # AI 提供商抽象层
│   │   ├── prompt_manager.py      # Prompt 流管理
│   │   └── config.py              # 配置管理
│   ├── server/                     # MCP 服务器
│   │   ├── main.py                # FastAPI 服务器 (SSE)
│   │   ├── fastmcp_server.py      # FastMCP 服务器 ⭐ 新增
│   │   ├── run_fastmcp.py         # FastMCP 启动脚本 ⭐ 新增
│   │   └── stdio_runner.py        # Stdio 模式运行器
│   ├── client/                     # MCP 客户端 ⭐ 新增
│   │   ├── fastmcp_client.py      # FastMCP 客户端
│   │   └── test_fastmcp_client.py # FastMCP 测试脚本
│   ├── ui/                         # PySide6 GUI
│   │   ├── main.py                # 应用程序入口
│   │   └── main_window.py         # 主窗口实现
│   ├── data/                       # 数据文件
│   │   └── prompts.json           # Prompt 配置
│   └── tests/                      # 测试文件
│       └── test_basic.py          # 基础测试
├── pyproject.toml                  # uv 项目配置
├── Makefile                        # 开发任务
└── README.md                       # 项目文档
```

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

### 3. 环境配置

创建 `.env` 文件设置 API 密钥：

```bash
# OpenAI API Key (必需)
OPENAI_API_KEY=your_openai_api_key_here

# 可选配置
ANTHROPIC_API_KEY=your_anthropic_key
OLLAMA_BASE_URL=http://localhost:11434

# 服务器配置
BUDDY_HOST=localhost
BUDDY_PORT=8000

# GUI 配置
BUDDY_WINDOW_WIDTH=1200
BUDDY_WINDOW_HEIGHT=800
```

### 4. 运行应用

**方式一：启动 GUI 应用**
```bash
uv run python -m buddy.ui.main
```

**方式二：启动传统 MCP 服务器 (SSE 模式)**
```bash
uv run uvicorn buddy.server.main:app --reload --port 8000
```

**方式三：启动 Stdio 模式**
```bash
uv run buddy-mcp-stdio
```

**方式四：启动 FastMCP 服务器** ⭐ **新增推荐！**
```bash
uv run python buddy/server/run_fastmcp.py
```

## 🔧 开发工具

### 可用的 uv 命令

我们推荐使用 `uv` 来管理项目，它提供了以下优势：
- 🚀 **更快的依赖解析**：比传统包管理器快 10-100 倍
- 🔒 **锁定文件**：确保依赖版本的一致性
- 🎯 **简化命令**：无需记住复杂的命令行参数
- 🔧 **内置工具链**：集成了格式化、检查、测试等工具

```bash
# 主要启动命令
uv run python -m buddy.ui.main           # 启动 GUI 应用
uv run uvicorn buddy.server.main:app --reload --port 8000  # 启动 FastAPI MCP 服务器 (SSE)
uv run buddy-mcp-stdio                   # 启动 stdio MCP 服务器
uv run python buddy/server/run_fastmcp.py  # 启动 FastMCP 服务器 ⭐

# 测试和示例
uv run pytest                            # 运行测试
uv run python buddy/client/test_fastmcp_client.py  # 测试 FastMCP 客户端
uv run python examples/fastmcp_example.py  # 运行 FastMCP 示例演示

# 代码质量工具
uv run ruff check .                      # 运行代码检查
uv run mypy .                            # 运行类型检查
uv run black .                           # 格式化代码
uv run isort .                           # 排序导入
uv run ruff check . --fix                # 自动修复代码问题

# 安装依赖组
uv sync --group dev                      # 安装开发依赖
uv sync --group test                     # 安装测试依赖
uv sync --group lint                     # 安装代码检查工具
uv sync --group format                  # 安装格式化工具
```

### 传统方式 (仍然支持)

如果您喜欢使用 `make`，传统的 Makefile 命令仍然可用：

```bash
make dev           # 等同于 uv run dev
make fastmcp       # 等同于 uv run fastmcp
make test-fastmcp  # 等同于 uv run test-fastmcp
# ... 其他命令
```

## 🔧 MCP 接口说明

### FastMCP 模式 ⭐ **推荐使用**

FastMCP 提供更简洁、类型安全的 MCP 开发体验。

#### 可用工具 (Tools)

1. **create_session** - 创建新会话
2. **send_message** - 发送消息
3. **send_message_stream** - 流式发送消息
4. **add_user_feedback** - 添加用户反馈
5. **get_session_info** - 获取会话信息
6. **list_sessions** - 列出所有会话
7. **delete_session** - 删除会话
8. **list_prompt_flows** - 列出提示流
9. **get_prompt_flow_info** - 获取提示流信息

#### 可用资源 (Resources)

- `session://sessions` - 所有会话资源
- `session://{session_id}` - 特定会话资源

#### 可用提示 (Prompts)

- `coding-assistant` - 编程助手提示模板

#### 使用 FastMCP 客户端

```python
from buddy.client import VibeCodingBuddyClient

async def example():
    async with VibeCodingBuddyClient() as client:
        # 创建会话
        session_id = await client.create_session(
            provider_type="openai",
            provider_config={"api_key": "your-key"}
        )
        
        # 发送消息
        response = await client.send_message(
            session_id=session_id,
            content="请帮我写一个 Python 函数"
        )
        
        print(f"回复: {response}")
```

#### 测试 FastMCP

```bash
# 测试 FastMCP 客户端
uv run python buddy/client/test_fastmcp_client.py
```

### SSE 模式 API

#### 1. 创建会话
```bash
POST http://localhost:8000/session
Content-Type: application/json

{
  "flow_id": "default",
  "provider_type": "openai",
  "provider_config": {
    "api_key": "your-key",
    "model": "gpt-4"
  }
}
```

#### 2. 发送消息（SSE 流式响应）
```bash
POST http://localhost:8000/session/{session_id}/assistant_response
Content-Type: application/json
Accept: text/event-stream

{
  "content": "请帮我分析这段代码",
  "context": "Python Flask 应用",
  "template_vars": {}
}
```

#### 3. 提交用户反馈
```bash
POST http://localhost:8000/session/{session_id}/user_feedback
Content-Type: application/json

{
  "feedback": "回答很有帮助",
  "rating": 5
}
```

#### 4. 获取可用流
```bash
GET http://localhost:8000/flows
```

### Stdio 模式

通过 JSON 消息与 stdin/stdout 通信：

```bash
# 启动 stdio 服务器
uv run buddy-mcp-stdio

# 发送消息示例
echo '{"method": "create_session", "params": {"flow_id": "default"}, "id": "1"}' | uv run buddy-mcp-stdio

echo '{"method": "send_message", "params": {"content": "Hello", "stream": true}, "id": "2"}' | uv run buddy-mcp-stdio
```

## 🎯 Prompt 流配置

在 `buddy/data/prompts.json` 中定义不同的对话流：

```json
{
  "flows": {
    "default": {
      "id": "default",
      "name": "默认编程助手",
      "system_prompt": "你是一个专业的编程助手...",
      "user_prompt_template": "用户: {user_input}\n\n上下文: {context}",
      "max_tokens": 4000,
      "temperature": 0.7
    },
    "code_review": {
      "id": "code_review",
      "name": "代码审查专家",
      "system_prompt": "你是一个资深的代码审查专家...",
      "capabilities": ["code_review", "optimization"]
    }
  }
}
```

## 🔊 语音功能

GUI 支持录音转文字功能：

1. 点击麦克风按钮开始录音
2. 再次点击停止录音
3. 自动调用 Whisper API 转写文字
4. 转写结果填入输入框

## ⚙️ 命令执行

内置命令执行面板支持：

- **pytest**：运行测试
- **python**：执行 Python 脚本  
- **uv**：包管理操作
- **git**：版本控制命令

实时显示命令输出，支持进度条和错误处理。

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
3. 通过 `qasync` 支持异步操作

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

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

## 📞 联系方式

- 项目主页：[GitHub Repository]
- 问题反馈：[GitHub Issues]
- 文档网站：[Documentation]

---

**享受与 Vibe Coding Buddy 的编程之旅！** 🎉
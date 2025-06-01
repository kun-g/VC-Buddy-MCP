# 🏗️ Project Structure

VC-Buddy-MCP/
├── buddy/                          # 主要代码包
│   ├── core/                       # 核心模块
│   │   ├── ai_provider.py         # AI 提供商抽象层
│   │   ├── prompt_manager.py      # Prompt 流管理
│   │   └── config.py              # 配置管理
│   ├── server/                     # MCP 服务器
│   │   └── main.py                # FastMCP 服务器实现
│   ├── client/                     # MCP 客户端
│   │   └── test.py                # 客户端测试脚本
│   ├── ui/                         # PySide6 GUI
│   │   ├── answer_box.py          # Answer Box 主界面 ⭐ 已优化
│   │   ├── config.py              # 配置管理
│   │   ├── todo_parser.py         # TODO 解析器
│   │   └── voice_recorder.py      # 语音录制模块 ⭐ 新增
│   └── tests/                      # 测试文件
│       └── test_basic.py          # 基础测试
├── docs/                           # 文档目录
│   ├── ProjectStructure.md        # 项目结构文档
│   └── README_CONFIG.md           # 配置管理文档
├── pyproject.toml                  # uv 项目配置 ⭐ 已更新依赖
├── Makefile                        # 开发任务
├── TODO.md                         # 项目 TODO 列表 ⭐ 已更新
└── README.md                       # 项目文档 ⭐ 已优化

## 🆕 最新更新

### 语音输入功能 ⭐ 新增
- **voice_recorder.py**: 完整的语音录制和转写模块
  - VoiceRecorder: 核心录音和转写类
  - VoiceButton: 语音录制按钮组件
  - 支持 OpenAI Whisper API 转写
  - 多线程录音，避免界面阻塞

### Answer Box 界面优化 ⭐ 已优化
- **summary_display**: 从 QLabel 改为 QTextBrowser，支持长文本滚动
- **TODO 完成状态**: 修复加载时不显示 ✅ 标记的问题
- **语音输入集成**: 在输入框旁边添加语音按钮
- **水平布局**: 输入框和语音按钮的优化布局

### MCP 文档完善 ⭐ 已优化
- **README.md**: 基于实际项目结构重写 MCP 安装部分
- **配置说明**: 添加正确的启动命令和验证方法
- **工具说明**: 详细说明 ask_for_feedback 工具的使用

### 依赖更新 ⭐ 已更新
- 添加 pyaudio>=0.2.11 (语音录制)
- 添加 openai>=1.0.0 (Whisper API)
- 添加 requests>=2.31.0 (HTTP 请求)
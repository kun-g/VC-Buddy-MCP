# 🏗️ Project Structure

VC-Buddy-MCP/
├── buddy/                          # 主要代码包
│   ├── core/                       # 核心模块
│   │   ├── ai_provider.py         # AI 提供商抽象层
│   │   ├── prompt_manager.py      # Prompt 流管理
│   │   ├── analytics.py           # 数据统计模块 ⭐ 新增，支持Amplitude集成
│   │   └── config.py              # 配置管理 ⭐ 已扩展OpenAI API Key和API URL支持
│   ├── server/                     # MCP 服务器
│   │   └── main.py                # FastMCP 服务器实现
│   ├── client/                     # MCP 客户端
│   │   └── test.py                # 客户端测试脚本
│   ├── ui/                         # PySide6 GUI
│   │   ├── answer_box.py          # Answer Box 传统界面 ⭐ 已优化，集成数据统计
│   │   ├── answer_box_qml.py      # Answer Box QML版本 ⭐ 已升级，支持流式语音输入和QML语音设置
│   │   ├── style_manager.py       # 样式管理器 ⭐ 新增
│   │   ├── qml/                   # QML 界面文件 ⭐ 新增
│   │   │   ├── Main.qml           # 主界面 QML ⭐ 支持流式语音输入显示
│   │   │   ├── TodoItemDelegate.qml # TODO 项目组件 ⭐ 使用主题系统
│   │   │   ├── VoiceSettingsDialog.qml # QML语音设置对话框 ⭐ 新增，替代Qt Widgets版本
│   │   │   ├── Theme.qml          # QML 主题定义 ⭐ 新增
│   │   │   ├── styles.qss         # QSS 样式文件 ⭐ 移动到qml目录
│   │   │   └── qmldir             # QML 模块配置 ⭐ 已更新
│   │   ├── config.py              # 配置管理
│   │   ├── todo_parser.py         # TODO 解析器 ⭐ 已完善，修复代码块解析问题
│   │   ├── voice_recorder.py      # 传统语音录制模块 ⭐ 已修复崩溃问题，增强稳定性
│   │   ├── streaming_voice_recorder.py # 流式语音录制器 ⭐ 已修复崩溃问题，支持实时转写
│   │   └── voice_settings_dialog.py # 语音设置对话框 ⭐ Qt Widgets版本，仅供工具使用
│   └── tests/                      # 测试文件
│       ├── test_basic.py          # 基础测试
│       ├── test_todo_parser.py    # TODO 解析器单元测试 ⭐ 新增，包含32个测试用例
│       └── test_analytics.py      # 数据统计模块单元测试 ⭐ 新增，包含10个测试用例
├── tools/                          # 工具目录 ⭐ 新增
│   ├── voice_test_unified.py      # 统一语音测试工具 ⭐ 新增，合并传统和流式测试功能
│   ├── settings_dialog.py         # 设置对话框 ⭐ 新增，支持API Key和API URL配置
│   └── README_VOICE_RECORDER.md   # 语音录制器使用说明 ⭐ 新增
├── scripts/                        # 安装脚本目录 ⭐ 新增
│   └── install.py                 # 智能安装脚本 ⭐ 新增，支持跨平台依赖检测和安装
├── docs/                           # 文档目录
│   ├── ProjectStructure.md        # 项目结构文档
│   ├── README_CONFIG.md           # 配置管理文档
│   ├── STREAMING_VOICE_INPUT.md   # 流式语音输入功能指南 ⭐ 新增
│   ├── VOICE_FIXES.md             # 语音功能修复说明 ⭐ 新增，修复崩溃问题
│   └── prd.md                     # 产品需求文档 ⭐ 新增
├── LICENSE                         # MIT 许可证文件 ⭐ 新增
├── pyproject.toml                  # uv 项目配置 ⭐ 已更新依赖
├── Makefile                        # 开发任务 ⭐ 已优化，智能依赖管理，支持跨平台系统依赖自动安装
├── TODO.md                         # 项目 TODO 列表 ⭐ 已更新
└── README.md                       # 项目文档 ⭐ 已优化
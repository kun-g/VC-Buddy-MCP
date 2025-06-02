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
│   │   ├── answer_box.py          # Answer Box 传统界面 ⭐ 已优化
│   │   ├── answer_box_qml.py      # Answer Box QML版本 ⭐ 新增
│   │   ├── style_manager.py       # 样式管理器 ⭐ 新增
│   │   ├── qml/                   # QML 界面文件 ⭐ 新增
│   │   │   ├── Main.qml           # 主界面 QML ⭐ 使用主题系统
│   │   │   ├── TodoItemDelegate.qml # TODO 项目组件 ⭐ 使用主题系统
│   │   │   ├── Theme.qml          # QML 主题定义 ⭐ 新增
│   │   │   ├── styles.qss         # QSS 样式文件 ⭐ 移动到qml目录
│   │   │   └── qmldir             # QML 模块配置 ⭐ 已更新
│   │   ├── config.py              # 配置管理
│   │   ├── todo_parser.py         # TODO 解析器 ⭐ 已完善
│   │   └── voice_recorder.py      # 语音录制模块 ⭐ 新增
│   └── tests/                      # 测试文件
│       ├── test_basic.py          # 基础测试
│       └── test_todo_parser.py    # TODO 解析器单元测试 ⭐ 新增
├── tools/                          # 工具目录 ⭐ 新增
│   ├── voice_recorder_test.py     # 语音录制器测试工具 ⭐ 新增
│   └── README_VOICE_RECORDER.md   # 语音录制器使用说明 ⭐ 新增
├── docs/                           # 文档目录
│   ├── ProjectStructure.md        # 项目结构文档
│   ├── README_CONFIG.md           # 配置管理文档
│   └── prd.md                     # 产品需求文档 ⭐ 新增
├── LICENSE                         # MIT 许可证文件 ⭐ 新增
├── pyproject.toml                  # uv 项目配置 ⭐ 已更新依赖
├── Makefile                        # 开发任务
├── TODO.md                         # 项目 TODO 列表 ⭐ 已更新
└── README.md                       # 项目文档 ⭐ 已优化
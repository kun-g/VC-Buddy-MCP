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
│   │   ├── answer_box_qml.py      # Answer Box QML版本 ⭐ 新增，集成数据统计
│   │   ├── style_manager.py       # 样式管理器 ⭐ 新增
│   │   ├── qml/                   # QML 界面文件 ⭐ 新增
│   │   │   ├── Main.qml           # 主界面 QML ⭐ 使用主题系统
│   │   │   ├── TodoItemDelegate.qml # TODO 项目组件 ⭐ 使用主题系统
│   │   │   ├── Theme.qml          # QML 主题定义 ⭐ 新增
│   │   │   ├── styles.qss         # QSS 样式文件 ⭐ 移动到qml目录
│   │   │   └── qmldir             # QML 模块配置 ⭐ 已更新
│   │   ├── config.py              # 配置管理
│   │   ├── todo_parser.py         # TODO 解析器 ⭐ 已完善，修复代码块解析问题
│   │   └── voice_recorder.py      # 语音录制模块 ⭐ 新增，支持配置管理器和自定义API URL，集成数据统计
│   └── tests/                      # 测试文件
│       ├── test_basic.py          # 基础测试
│       ├── test_todo_parser.py    # TODO 解析器单元测试 ⭐ 新增，包含32个测试用例
│       └── test_analytics.py      # 数据统计模块单元测试 ⭐ 新增，包含10个测试用例
├── tools/                          # 工具目录 ⭐ 新增
│   ├── voice_recorder_test.py     # 语音录制器测试工具 ⭐ 已更新，集成配置管理
│   ├── settings_dialog.py         # 设置对话框 ⭐ 新增，支持API Key和API URL配置
│   └── README_VOICE_RECORDER.md   # 语音录制器使用说明 ⭐ 新增
├── scripts/                        # 安装脚本目录 ⭐ 新增
│   └── install.py                 # 智能安装脚本 ⭐ 新增，支持跨平台依赖检测和安装
├── docs/                           # 文档目录
│   ├── ProjectStructure.md        # 项目结构文档
│   ├── README_CONFIG.md           # 配置管理文档
│   └── prd.md                     # 产品需求文档 ⭐ 新增
├── LICENSE                         # MIT 许可证文件 ⭐ 新增
├── pyproject.toml                  # uv 项目配置 ⭐ 已更新依赖
├── Makefile                        # 开发任务 ⭐ 已优化，智能依赖管理
├── TODO.md                         # 项目 TODO 列表 ⭐ 已更新
└── README.md                       # 项目文档 ⭐ 已优化

## 📊 数据统计功能

新增的数据统计模块 (`buddy/core/analytics.py`) 提供以下功能：

### 统计点覆盖
- **界面开启**: 应用启动时统计来源（项目/通用）
- **快捷键使用**: 统计快捷键名称和操作类型
- **按钮点击**: 统计按钮名称和上下文
- **TODO操作**: 统计点击、双击、右键菜单、标记完成/未完成等操作
- **语音功能**: 统计录音开始/停止、播放、转写完成、错误等事件

### 技术特性
- **Amplitude集成**: 支持Amplitude数据分析平台
- **隐私保护**: 只记录操作类型和统计数据，不记录具体内容
- **配置管理**: 支持启用/禁用统计，设备ID持久化
- **容错处理**: 统计失败不影响主要功能
- **模拟模式**: 在没有Amplitude库时使用模拟统计

### 测试覆盖
- 设备ID创建和持久化
- 统计开关配置
- 事件跟踪功能
- 配置文件管理
- 全局便捷函数
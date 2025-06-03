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

## 🎤 流式语音输入功能

新增的流式语音输入功能 (`buddy/ui/streaming_voice_recorder.py`) 提供以下特性：

### 核心功能
- **实时转写**: 边说边转写，无需等待录音结束
- **流式处理**: 每2秒处理一个音频块，提供即时反馈
- **自定义命令**: 支持用户自定义停止和发送命令
- **智能检测**: 自动识别语音命令并执行相应操作
- **缓冲管理**: 智能管理转写缓冲区，避免重复内容

### 命令系统
- **停止命令**: "我说完了"、"结束"、"stop" 等，停止录音
- **发送命令**: "开工吧"、"发送"、"go" 等，停止录音并自动发送
- **多语言支持**: 同时支持中文和英文命令
- **可配置**: 通过设置界面自定义命令列表

### 用户界面
- **语音设置对话框**: 配置自定义命令的专用界面
- **实时显示**: 在输入框中实时显示转写进度
- **状态反馈**: 清晰的录音状态和命令检测提示
- **统一测试工具**: 合并传统和流式测试功能的综合测试界面

### 技术特性
- **异步处理**: 多线程处理录音和转写，不阻塞UI
- **错误处理**: 完善的错误处理和用户提示
- **配置集成**: 与现有配置系统深度集成
- **统计支持**: 集成数据统计功能

## 🔧 语音功能修复

### 主要修复
- **PyAudio调用错误**: 修复了 `pyaudio.get_sample_size` 调用问题
- **资源管理**: 增强音频资源的安全清理
- **错误处理**: 改进网络和API错误的详细提示
- **兼容性**: 提高第三方API服务器的兼容性
- **QML对话框崩溃**: 修复answer_box_qml中点击「语言设置」按钮崩溃问题 ⭐ 新修复

### QML语音设置对话框
- **原生QML实现**: 使用QML重新实现语音设置对话框，避免在QGuiApplication中使用QDialog
- **ConfigManagerProxy**: 创建配置管理器代理类，桥接Python ConfigManager和QML
- **信号机制**: 使用Qt信号槽机制在QML和Python之间通信
- **主题一致性**: 与主界面保持一致的Material Design主题
- **功能完整**: 保持与原Qt Widgets版本相同的所有功能

### 技术架构改进
- **混合架构**: 主应用使用QGuiApplication + QML，工具继续使用QApplication + Qt Widgets
- **类型注册**: 注册ConfigManagerProxy到QML类型系统
- **错误处理**: 完善的异常处理和用户反馈机制

## 📊 数据统计功能

新增的数据统计模块 (`buddy/core/analytics.py`) 提供以下功能：

### 统计点覆盖
- **界面开启**: 应用启动时统计来源（项目/通用）
- **快捷键使用**: 统计快捷键名称和操作类型
- **按钮点击**: 统计按钮名称和上下文
- **TODO操作**: 统计点击、双击、右键菜单、标记完成/未完成等操作
- **语音功能**: 统计录音开始/停止、播放、转写完成、错误等事件，包含流式语音统计

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
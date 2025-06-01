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
├── docs/                           # 文档目录
│   ├── ProjectStructure.md        # 项目结构文档
│   ├── README_CONFIG.md           # 配置管理文档
│   └── prd.md                     # 产品需求文档 ⭐ 新增
├── test_qml_answerbox.py          # QML Answer Box 测试脚本 ⭐ 新增
├── test_qml_interactive.py       # QML 交互式测试脚本 ⭐ 新增
├── pyproject.toml                  # uv 项目配置 ⭐ 已更新依赖
├── Makefile                        # 开发任务
├── TODO.md                         # 项目 TODO 列表 ⭐ 已更新
└── README.md                       # 项目文档 ⭐ 已优化

## 🆕 最新更新

### QML 界面系统 ⭐ 新增
- **answer_box_qml.py**: QML 版本的 Answer Box
  - AnswerBoxBackend: QML 后端逻辑类
  - TodoListModel: TODO 列表数据模型
  - 完整的信号槽系统和属性绑定
  - Material Design 样式主题
  - 集成语音录制和转写功能 ⭐ 新增
- **Main.qml**: 主界面布局
  - 响应式分割布局
  - TODO 列表和详情显示
  - 输入区域和发送按钮
  - Commit 复选框功能
  - 语音录制按钮和功能 ⭐ 新增
- **TodoItemDelegate.qml**: TODO 项目组件
  - 层级缩进显示
  - 右键菜单操作
  - 属性和内容预览
  - 状态指示器
  - 已完成TODO删除功能 ⭐ 新增

### TODO 解析器增强 ⭐ 已完善
- **todo_parser.py**: 完整的 TODO.md 文件处理
  - TodoItem: 数据结构和方法完善
  - TodoParser: 解析和保存功能
  - 支持属性 (key=value 格式)
  - 状态管理 (done/undone)
  - to_dict() 方法支持 QML 数据绑定
- **test_todo_parser.py**: 全面的单元测试

### 测试脚本 ⭐ 新增
- **test_qml_answerbox.py**: 自动化测试脚本
- **test_qml_interactive.py**: 交互式测试脚本
  - 模拟 MCP 调用流程
  - 实时输出监控
  - JSON 响应验证

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

### 样式系统重构 ⭐ 新增
- **styles.qss**: 完整的 QSS 样式文件（位于qml目录）
  - Material Design 颜色方案
  - 完整的控件样式定义
  - 支持按钮、输入框、列表、滚动条等组件
  - 特殊类样式支持 (.todo-item, .summary-box 等)
- **style_manager.py**: 样式管理器模块
  - StyleManager: 样式加载和应用管理
  - 支持多主题切换 (默认/深色)
  - QSS 文件动态加载
  - 主题配置导入导出
- **Theme.qml**: QML 主题单例
  - 统一的颜色、字体、间距定义
  - 响应式设计常量
  - 动画和阴影配置
- **界面文件更新**: Main.qml 和 TodoItemDelegate.qml
  - 移除硬编码样式值
  - 使用主题系统统一管理
  - 支持实时主题切换

## 🎯 样式系统架构

### QSS 样式 (Qt Widgets)
- **styles.qss**: 传统 Qt Widgets 样式
- **StyleManager**: 动态加载和应用 QSS
- **主题切换**: 支持多套颜色方案

### QML 主题 (QML 界面)
- **Theme.qml**: 单例主题对象
- **声明式**: 通过 Theme.colors.primary 访问
- **响应式**: 自动适配不同屏幕尺寸

### 统一设计语言
- **Material Design**: 遵循 Google Material 设计规范
- **颜色一致性**: QSS 和 QML 使用相同颜色值
- **可维护性**: 集中管理所有样式定义

## 🎯 QML vs 传统界面对比

| 特性 | answer_box.py | answer_box_qml.py |
|-----|--------------|------------------|
| 界面技术 | Qt Widgets | QML + Material Design |
| 布局方式 | 代码定义 | 声明式 QML |
| 主题样式 | 硬编码样式表 | Material Design 主题 |
| 响应性 | 固定布局 | 自适应响应式 |
| 可定制性 | 中等 | 高度可定制 |
| 开发效率 | 中等 | 高 |
| 性能 | 良好 | 优秀 |
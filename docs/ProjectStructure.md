
# 🏗️ Project Structure

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
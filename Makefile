.PHONY: help install install-system-deps dev show-ui show-ui-qml test-voice mcp-claude mcp-cursor

help:
	@echo "Available commands:"
	@echo "  make install            - Install system dependencies and Python packages"
	@echo "  make install-system-deps - Install system-level dependencies only"
	@echo "  make dev                - Start development GUI"
	@echo "  make show-ui            - Show UI (QtWidgets version)"
	@echo "  make test-voice         - Launch voice recorder test tool"
	@echo "  make mcp-claude         - Output MCP configuration for Claude Desktop"
	@echo "  make mcp-cursor         - Output MCP configuration for Cursor"

install-system-deps:
	@echo "🔧 检测操作系统并安装系统依赖..."
	@if [ "$(shell uname)" = "Darwin" ]; then \
		echo "检测到 macOS，使用 Homebrew 安装依赖..."; \
		if ! command -v brew >/dev/null 2>&1; then \
			echo "❌ 未找到 Homebrew，请先安装: https://brew.sh"; \
			exit 1; \
		fi; \
		echo "安装 portaudio..."; \
		brew install portaudio; \
	elif [ "$(shell uname)" = "Linux" ]; then \
		echo "检测到 Linux，使用包管理器安装依赖..."; \
		if command -v apt-get >/dev/null 2>&1; then \
			echo "使用 apt-get 安装 portaudio19-dev..."; \
			sudo apt-get update && sudo apt-get install -y portaudio19-dev python3-dev; \
		elif command -v yum >/dev/null 2>&1; then \
			echo "使用 yum 安装 portaudio-devel..."; \
			sudo yum install -y portaudio-devel python3-devel; \
		elif command -v dnf >/dev/null 2>&1; then \
			echo "使用 dnf 安装 portaudio-devel..."; \
			sudo dnf install -y portaudio-devel python3-devel; \
		elif command -v pacman >/dev/null 2>&1; then \
			echo "使用 pacman 安装 portaudio..."; \
			sudo pacman -S --noconfirm portaudio; \
		else \
			echo "⚠️  未识别的 Linux 发行版，请手动安装 portaudio 开发库"; \
			echo "   Ubuntu/Debian: sudo apt-get install portaudio19-dev"; \
			echo "   CentOS/RHEL: sudo yum install portaudio-devel"; \
			echo "   Fedora: sudo dnf install portaudio-devel"; \
			echo "   Arch: sudo pacman -S portaudio"; \
		fi; \
	else \
		echo "⚠️  未识别的操作系统: $(shell uname)"; \
		echo "请手动安装 portaudio 库"; \
	fi
	@echo "✅ 系统依赖安装完成"

install: install-system-deps
	@echo "📦 安装 Python 依赖包..."
	uv sync
	@echo "🎉 所有依赖安装完成!"
	@echo ""
	@echo "💡 提示："
	@echo "   - 如果遇到音频相关问题，请确保音频设备正常工作"
	@echo "   - 运行 'make test-voice' 测试语音功能"
	@echo "   - 运行 'make dev' 启动开发环境"

dev:
	uv run fastmcp dev buddy/server/main.py

show-ui:
	@echo '{"summary": "我已经完成了 TODO 列表的解析功能，需求你确认验收一下", "project_directory": "'$(PWD)'"}' | uv run buddy/ui/answer_box_qml.py

test-voice: install
	uv run tools/voice_test_unified.py

mcp-claude:
	uv run python tools/mcp_config_generator.py --client claude

mcp-cursor:
	uv run python tools/mcp_config_generator.py --client cursor
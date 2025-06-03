.PHONY: help install dev show-ui show-ui-qml test-voice

help:
	@echo "Available commands:"
	@echo "  make install            - Install dependencies with uv"
	@echo "  make dev                - Start development GUI"
	@echo "  make show-ui            - Show UI (QtWidgets version)"
	@echo "  make show-ui-qml        - Show UI (QML version)"
	@echo "  make test-voice         - Launch voice recorder test tool"

install:
	uv sync

dev: install
	uv run fastmcp dev buddy/server/main.py

show-ui: install
	@echo '{"summary": "我已经完成了 TODO 列表的解析功能，需求你确认验收一下", "project_directory": "'$(PWD)'"}' | uv run buddy/ui/answer_box_qml.py

test-voice: install
	uv run tools/voice_test_unified.py
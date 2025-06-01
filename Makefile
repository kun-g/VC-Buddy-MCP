.PHONY: help install dev show-ui show-ui-qml test-qml test-qml-interactive

help:
	@echo "Available commands:"
	@echo "  make install            - Install dependencies with uv"
	@echo "  make dev                - Start development GUI"
	@echo "  make show-ui            - Show UI (QtWidgets version)"
	@echo "  make show-ui-qml        - Show UI (QML version)"
	@echo "  make test-qml           - Test QML version with sample data"
	@echo "  make test-qml-interactive - Interactive QML test with feedback verification"

install:
	uv sync

dev: install
	uv run fastmcp dev buddy/server/main.py

show-ui: install
	uv run buddy/client/test.py

show-ui-qml: install
	@echo '{"summary": "测试QML版本界面", "project_directory": "'$(PWD)'"}' | uv run buddy/ui/run_qml.py

test-qml: install
	@echo '{"summary": "这是一个测试摘要，用于验证QML界面的功能。包含TODO解析、属性显示、双击插入等功能。", "project_directory": "'$(PWD)'"}' | uv run buddy/ui/run_qml.py

test-qml-interactive: install
	python test_qml_interactive.py

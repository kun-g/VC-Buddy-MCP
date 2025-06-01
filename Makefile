.PHONY: help install dev show-ui

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies with uv"
	@echo "  make dev           - Start development GUI"
	@echo "  make show-ui       - Show UI"

install:
	uv sync

dev: install
	uv run fastmcp dev buddy/server/main.py

show-ui: install
	uv run buddy/client/test.py

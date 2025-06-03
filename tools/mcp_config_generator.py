#!/usr/bin/env python3
"""
MCP 配置生成器

为主流 AI 编程软件生成 MCP 配置项，支持：
- Cursor IDE
- Claude Desktop
- 其他 MCP 客户端

使用方法：
    python tools/mcp_config_generator.py [--client cursor|claude|all]
"""

import argparse
import json
import os
import sys
import platform
from pathlib import Path


def get_project_path():
    """获取项目根目录路径"""
    return Path(__file__).parent.parent.absolute()


def get_os_info():
    """获取操作系统信息"""
    system = platform.system().lower()
    return {
        'is_windows': system == 'windows',
        'is_macos': system == 'darwin',
        'is_linux': system == 'linux'
    }


def format_path_for_json(path, is_windows=False):
    """根据操作系统格式化路径"""
    if is_windows:
        # Windows 路径需要转义反斜杠
        return str(path).replace('\\', '\\\\')
    else:
        # Unix-like 系统直接使用正斜杠
        return str(path)


def generate_cursor_config():
    """生成 Cursor IDE 的 MCP 配置"""
    project_path = get_project_path()
    os_info = get_os_info()
    
    config = {
        "vc-buddy": {
            "command": "uv",
            "args": [
                "--directory",
                format_path_for_json(project_path, os_info['is_windows']),
                "run",
                "buddy/server/main.py"
            ]
        }
    }
    
    return config


def generate_claude_desktop_config():
    """生成 Claude Desktop 的 MCP 配置"""
    project_path = get_project_path()
    os_info = get_os_info()
    
    config = {
        "mcpServers": {
            "vc-buddy": {
                "command": "uv",
                "args": [
                    "--directory",
                    format_path_for_json(project_path, os_info['is_windows']),
                    "run",
                    "buddy/server/main.py"
                ]
            }
        }
    }
    
    return config


def get_cursor_config_locations():
    """获取 Cursor 配置文件位置"""
    os_info = get_os_info()
    
    if os_info['is_windows']:
        return [
            "项目级别：.cursor\\mcp.json",
            "全局级别：%USERPROFILE%\\.cursor\\mcp.json"
        ]
    else:
        return [
            "项目级别：.cursor/mcp.json",
            "全局级别：~/.cursor/mcp.json"
        ]


def get_claude_config_locations():
    """获取 Claude Desktop 配置文件位置"""
    os_info = get_os_info()
    
    locations = []
    if os_info['is_macos']:
        locations.append("macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    if os_info['is_windows']:
        locations.append("Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    if os_info['is_linux']:
        locations.append("Linux: ~/.config/Claude/claude_desktop_config.json")
    
    # 如果检测不到具体系统，显示所有可能的位置
    if not any([os_info['is_macos'], os_info['is_windows'], os_info['is_linux']]):
        locations = [
            "macOS: ~/Library/Application Support/Claude/claude_desktop_config.json",
            "Windows: %APPDATA%\\Claude\\claude_desktop_config.json",
            "Linux: ~/.config/Claude/claude_desktop_config.json"
        ]
    
    return locations


def print_cursor_config():
    """打印 Cursor IDE 配置"""
    config = generate_cursor_config()
    os_info = get_os_info()
    
    print("📋 Cursor IDE MCP 配置")
    print("=" * 50)
    print("将以下配置添加到 Cursor 的 MCP 设置中：")
    print()
    print("配置文件位置：")
    for location in get_cursor_config_locations():
        print(f"- {location}")
    print()
    print("配置内容：")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print()
    
    # 添加操作系统特定的提示
    if os_info['is_windows']:
        print("💡 Windows 用户提示：")
        print("- 使用双反斜杠 (\\\\) 或正斜杠 (/) 作为路径分隔符")
        print("- 确保路径中没有中文字符，可能导致编码问题")
        print()


def print_claude_desktop_config():
    """打印 Claude Desktop 配置"""
    config = generate_claude_desktop_config()
    os_info = get_os_info()
    
    print("🤖 Claude Desktop MCP 配置")
    print("=" * 50)
    print("将以下配置添加到 Claude Desktop 配置文件中：")
    print()
    print("配置文件位置：")
    for location in get_claude_config_locations():
        print(f"- {location}")
    print()
    print("配置内容：")
    print(json.dumps(config, indent=2, ensure_ascii=False))
    print()
    
    # 添加操作系统特定的提示
    if os_info['is_windows']:
        print("💡 Windows 用户提示：")
        print("- 如果配置文件不存在，请手动创建")
        print("- 确保 Node.js 已正确安装并在 PATH 中")
        print()
    elif os_info['is_macos']:
        print("💡 macOS 用户提示：")
        print("- 可以通过 Claude Desktop 菜单 > Settings > Developer > Edit Config 打开配置文件")
        print("- 确保已安装 Homebrew 和 Node.js")
        print()
    elif os_info['is_linux']:
        print("💡 Linux 用户提示：")
        print("- 配置文件目录可能需要手动创建")
        print("- 确保 Node.js 和 npm 已正确安装")
        print()

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="生成 MCP 配置项",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法：
  python tools/mcp_config_generator.py                    # 显示所有配置
  python tools/mcp_config_generator.py --client cursor    # 只显示 Cursor 配置
  python tools/mcp_config_generator.py --client claude    # 只显示 Claude Desktop 配置
        """
    )
    
    parser.add_argument(
        "--client",
        choices=["cursor", "claude", "all"],
        default="all",
        help="指定要生成配置的客户端 (默认: all)"
    )
    
    args = parser.parse_args()
    
    print("🚀 VC-Buddy MCP 配置生成器")
    print("=" * 50)
    print()
    
    if args.client in ["cursor", "all"]:
        print_cursor_config()
    
    if args.client in ["claude", "all"]:
        print_claude_desktop_config()


if __name__ == "__main__":
    main() 
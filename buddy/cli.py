#!/usr/bin/env python3
"""VC-Buddy CLI 工具"""
import argparse
import os
import shutil
import sys
from pathlib import Path


def setup_cursor_rules(target_dir: Path):
    """设置 Cursor rules 到目标目录"""
    # 获取当前项目的 cursor rules 目录
    current_file = Path(__file__)
    project_root = current_file.parent.parent
    cursor_rules_source = project_root / ".cursor" / "rules"
    
    if not cursor_rules_source.exists():
        print("❌ 源 cursor rules 目录不存在")
        return False
    
    # 目标 cursor rules 目录
    target_cursor_dir = target_dir / ".cursor" / "rules"
    target_cursor_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制 cursor rules 文件
    rules_copied = 0
    for rule_file in cursor_rules_source.glob("*.mdc"):
        target_file = target_cursor_dir / rule_file.name
        try:
            shutil.copy2(rule_file, target_file)
            print(f"✅ 复制 cursor rule: {rule_file.name}")
            rules_copied += 1
        except Exception as e:
            print(f"❌ 复制 {rule_file.name} 失败: {e}")
    
    if rules_copied > 0:
        print(f"🎉 成功设置 {rules_copied} 个 cursor rules")
        return True
    else:
        print("❌ 没有复制任何 cursor rules")
        return False


def setup_command(args):
    """处理 setup 命令"""
    target_dir = Path(args.directory).resolve()
    
    print(f"🔧 正在设置项目环境到: {target_dir}")
    
    # 检查目标目录是否存在
    if not target_dir.exists():
        print(f"❌ 目标目录不存在: {target_dir}")
        return 1
    
    # 设置 cursor rules
    if not setup_cursor_rules(target_dir):
        print("⚠️  cursor rules 设置失败")
        return 1
    
    print("✨ 项目环境设置完成！")
    print("\n📝 下一步：")
    print("1. 在 Cursor 中打开项目目录")
    print("2. 开始使用 VC-Buddy 的开发规范")
    
    return 0


def main():
    """CLI 主入口"""
    parser = argparse.ArgumentParser(
        prog="vcbuddy",
        description="VC-Buddy 项目环境设置工具"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # setup 命令
    setup_parser = subparsers.add_parser(
        "setup", 
        help="设置项目环境"
    )
    setup_parser.add_argument(
        "directory", 
        nargs="?", 
        default=".", 
        help="目标目录 (默认: 当前目录)"
    )
    
    args = parser.parse_args()
    
    if args.command == "setup":
        return setup_command(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main()) 
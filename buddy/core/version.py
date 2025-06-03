#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本获取模块
提供统一的版本号获取方法
"""

import sys
import re
from pathlib import Path
from typing import Optional


def get_app_version() -> str:
    """获取应用版本号
    
    优先级：
    1. 从包元数据获取（如果已安装为包）
    2. 从pyproject.toml读取
    3. 默认值 '0.1.0'
    
    Returns:
        str: 应用版本号
    """
    try:
        # 方法1: 尝试从包元数据获取版本（如果uv已经注入或包已安装）
        version = _get_version_from_metadata()
        if version:
            return version
        
        # 方法2: 从pyproject.toml读取
        version = _get_version_from_pyproject()
        if version:
            return version
        
        # 方法3: 默认值
        return "0.1.0"
        
    except Exception as e:
        # 使用print而不是logging，避免循环依赖
        print(f"Warning: Failed to get app version: {e}")
        return "0.1.0"


def _get_version_from_metadata() -> Optional[str]:
    """从包元数据获取版本号"""
    try:
        # Python 3.8+ 使用 importlib.metadata
        if sys.version_info >= (3, 8):
            from importlib.metadata import version, PackageNotFoundError
            try:
                # 尝试获取已安装包的版本
                return version("vibe-coding-buddy")
            except PackageNotFoundError:
                return None
        else:
            # Python 3.7 使用 importlib_metadata
            from importlib_metadata import version, PackageNotFoundError
            try:
                return version("vibe-coding-buddy")
            except PackageNotFoundError:
                return None
    except ImportError:
        return None


def _get_version_from_pyproject() -> Optional[str]:
    """从pyproject.toml文件获取版本号"""
    try:
        # 查找项目根目录下的pyproject.toml
        current_file = Path(__file__)
        
        # 向上查找包含pyproject.toml的目录（最多向上3级）
        search_paths = [
            current_file.parent.parent.parent,  # ../../
            current_file.parent.parent,         # ../
            current_file.parent,                # ./
            Path.cwd(),                         # 当前工作目录
        ]
        
        for parent in search_paths:
            pyproject_file = parent / "pyproject.toml"
            if pyproject_file.exists():
                # 使用简单的文本解析（避免依赖toml库）
                with open(pyproject_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 查找version = "x.x.x"行
                version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if version_match:
                    return version_match.group(1)
        
        return None
        
    except Exception as e:
        # 使用print而不是logging，避免循环依赖
        print(f"Warning: Failed to read version from pyproject.toml: {e}")
        return None 
"""
样式管理器模块
负责加载 QSS 样式文件和管理主题切换
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, Signal, Property
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication
import sys


class StyleManager(QObject):
    """样式管理器类"""
    
    # 信号定义
    themeChanged = Signal(str, arguments=['themeName'])
    styleLoaded = Signal(bool, arguments=['success'])
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 获取样式文件目录
        self._styles_dir = Path(__file__).parent
        self._current_theme = "default"
        self._loaded_styles = {}
        
        # 主题配置
        self._themes = {
            "default": {
                "name": "默认主题",
                "qss_file": "styles.qss",
                "colors": {
                    "primary": "#2196F3",
                    "background": "#FFFFFF",
                    "surface": "#F5F5F5"
                }
            },
            "dark": {
                "name": "深色主题",
                "qss_file": "styles_dark.qss",
                "colors": {
                    "primary": "#1976D2",
                    "background": "#121212",
                    "surface": "#1E1E1E"
                }
            }
        }
        
    @Property(str, notify=themeChanged)
    def currentTheme(self):
        """获取当前主题名称"""
        return self._current_theme
    
    @Property(list, constant=True)
    def availableThemes(self):
        """获取可用主题列表"""
        return list(self._themes.keys())
    
    def load_qss_file(self, qss_file: str) -> str:
        """加载 QSS 文件内容"""
        try:
            qss_path = self._styles_dir / qss_file
            if qss_path.exists():
                with open(qss_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                print(f"WARNING: QSS 文件不存在: {qss_path}")
                return ""
        except Exception as e:
            print(f"ERROR: 加载 QSS 文件失败: {e}")
            return ""
    
    def apply_qss_to_app(self, qss_content: str) -> bool:
        """将 QSS 样式应用到应用程序"""
        try:
            app = QApplication.instance()
            # QGuiApplication (QML应用) 不支持 setStyleSheet，只有 QApplication (Widgets应用) 支持
            if app and qss_content and hasattr(app, 'setStyleSheet'):
                app.setStyleSheet(qss_content)
                return True
            elif app and not hasattr(app, 'setStyleSheet'):
                print("INFO: QML 应用不支持 QSS 样式，跳过 QSS 应用", file=sys.stderr)
                return True  # 对于 QML 应用，这不算错误
            return False
        except Exception as e:
            print(f"ERROR: 应用 QSS 样式失败: {e}", file=sys.stderr)
            return False
    
    def load_theme(self, theme_name: str = "default") -> bool:
        """加载指定主题"""
        if theme_name not in self._themes:
            print(f"WARNING: 主题不存在: {theme_name}")
            return False
        
        theme_config = self._themes[theme_name]
        qss_file = theme_config.get("qss_file", "styles.qss")
        
        # 检查是否已加载
        if theme_name in self._loaded_styles:
            qss_content = self._loaded_styles[theme_name]
        else:
            # 加载 QSS 文件
            qss_content = self.load_qss_file(qss_file)
            self._loaded_styles[theme_name] = qss_content
        
        # 应用样式
        success = self.apply_qss_to_app(qss_content)
        
        if success:
            self._current_theme = theme_name
            self.themeChanged.emit(theme_name)
            print(f"INFO: 成功加载主题: {theme_config['name']}")
        
        self.styleLoaded.emit(success)
        return success
    
    def get_theme_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """获取主题颜色配置"""
        if theme_name is None:
            theme_name = self._current_theme
        
        if theme_name in self._themes:
            return self._themes[theme_name].get("colors", {})
        return {}
    
    def create_custom_qss(self, **color_overrides) -> str:
        """创建自定义 QSS 样式"""
        base_qss = self.load_qss_file("styles.qss")
        
        # 替换颜色变量
        for color_name, color_value in color_overrides.items():
            # 这里可以实现颜色变量替换逻辑
            # 由于 QSS 不支持变量，我们可以使用字符串替换
            pass
        
        return base_qss
    
    def export_theme_config(self, theme_name: str, file_path: str) -> bool:
        """导出主题配置"""
        try:
            if theme_name not in self._themes:
                return False
            
            config = {
                "theme": self._themes[theme_name],
                "qss_content": self._loaded_styles.get(theme_name, "")
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"ERROR: 导出主题配置失败: {e}")
            return False
    
    def import_theme_config(self, file_path: str, theme_name: str) -> bool:
        """导入主题配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if "theme" in config:
                self._themes[theme_name] = config["theme"]
                
                if "qss_content" in config:
                    self._loaded_styles[theme_name] = config["qss_content"]
                
                return True
            
            return False
        except Exception as e:
            print(f"ERROR: 导入主题配置失败: {e}")
            return False


# 全局样式管理器实例
style_manager = StyleManager()


def get_style_manager() -> StyleManager:
    """获取全局样式管理器实例"""
    return style_manager


def load_default_styles() -> bool:
    """加载默认样式"""
    return style_manager.load_theme("default")


def apply_qss_file(qss_file: str) -> bool:
    """直接应用 QSS 文件"""
    qss_content = style_manager.load_qss_file(qss_file)
    return style_manager.apply_qss_to_app(qss_content)


# QML 样式工具函数
def get_qml_theme_properties() -> Dict[str, Any]:
    """获取 QML 主题属性"""
    colors = style_manager.get_theme_colors()
    return {
        "colors": colors,
        "fonts": {
            "family": "Segoe UI, Helvetica Neue, Arial, sans-serif",
            "small": 10,
            "normal": 12,
            "medium": 14,
            "large": 16
        },
        "spacing": {
            "small": 4,
            "normal": 8,
            "medium": 12,
            "large": 16
        }
    } 
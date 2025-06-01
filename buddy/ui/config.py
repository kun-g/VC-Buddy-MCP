import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

class ConfigManager:
    """统一的配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self._config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        # 优先级：环境变量 > 用户主目录 > 当前目录
        if config_path := os.getenv("VC_BUDDY_CONFIG"):
            return config_path
        
        # 在用户主目录下创建配置文件
        home_config = Path.home() / ".vc-buddy" / "config.json"
        home_config.parent.mkdir(exist_ok=True)
        return str(home_config)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config file {self.config_file}: {e}")
        
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "app": {
                "organization_name": "VC-Buddy",
                "application_name": "AnswerBox",
                "organization_domain": "vcbuddy.local"
            },
            "ui": {
                "window": {
                    "default_width": 300,
                    "default_height": 200,
                    "remember_position": True,
                    "stay_on_top": True
                }
            }
        }
    
    def save_config(self):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save config file {self.config_file}: {e}")
    
    def get(self, key_path: str, default=None):
        """
        获取配置值，支持点分隔的路径
        例如: get("app.organization_name")
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value):
        """
        设置配置值，支持点分隔的路径
        例如: set("app.organization_name", "MyCompany")
        """
        keys = key_path.split('.')
        config = self._config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    @property
    def organization_name(self) -> str:
        """获取组织名称，优先使用环境变量"""
        return os.getenv("VC_BUDDY_ORG") or self.get("app.organization_name", "VC-Buddy")
    
    @property
    def application_name(self) -> str:
        """获取应用名称，优先使用环境变量"""
        return os.getenv("VC_BUDDY_APP_NAME") or self.get("app.application_name", "AnswerBox")
    
    @property
    def organization_domain(self) -> str:
        """获取组织域名，优先使用环境变量"""
        return os.getenv("VC_BUDDY_DOMAIN") or self.get("app.organization_domain", "vcbuddy.local")

# 全局配置实例
config_manager = ConfigManager() 
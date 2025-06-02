import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

class ConfigManager:
    """统一的配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None, project_directory: Optional[str] = None):
        self.project_directory = project_directory
        self.config_file = config_file or self._get_default_config_path()
        self._config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        # 优先级：项目目录 > 环境变量 > 用户主目录
        
        # 1. 项目目录配置（最高优先级）
        if self.project_directory and os.path.exists(self.project_directory):
            project_config = Path(self.project_directory) / ".vc-buddy" / "config.json"
            if project_config.exists():
                return str(project_config)
        
        # 2. 环境变量指定的配置
        if config_path := os.getenv("VC_BUDDY_CONFIG"):
            return config_path
        
        # 3. 在用户主目录下创建配置文件
        home_config = Path.home() / ".vc-buddy" / "config.json"
        home_config.parent.mkdir(exist_ok=True)
        return str(home_config)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件，支持多层级配置合并"""
        # 从默认配置开始
        config = self._get_default_config()
        
        # 加载用户主目录配置
        home_config_path = Path.home() / ".vc-buddy" / "config.json"
        if home_config_path.exists():
            try:
                with open(home_config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    config = self._merge_configs(config, user_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load user config file {home_config_path}: {e}")
        
        # 加载环境变量指定的配置
        env_config_path = os.getenv("VC_BUDDY_CONFIG")
        if env_config_path and os.path.exists(env_config_path):
            try:
                with open(env_config_path, 'r', encoding='utf-8') as f:
                    env_config = json.load(f)
                    config = self._merge_configs(config, env_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load env config file {env_config_path}: {e}")
        
        # 加载项目目录配置（最高优先级）
        if self.project_directory and os.path.exists(self.project_directory):
            project_config_path = Path(self.project_directory) / ".vc-buddy" / "config.json"
            if project_config_path.exists():
                try:
                    with open(project_config_path, 'r', encoding='utf-8') as f:
                        project_config = json.load(f)
                        config = self._merge_configs(config, project_config)
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Could not load project config file {project_config_path}: {e}")
        
        return config
    
    def _merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并配置字典"""
        result = base_config.copy()
        
        for key, value in override_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
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
                    "default_width": 623,
                    "default_height": 631,
                    "remember_position": True,
                    "stay_on_top": True
                }
            },
            "openai": {
                "api_key": "",
                "api_url": "https://api.openai.com/v1"
            }
        }
    
    def save_config(self, save_to_project: bool = False):
        """保存配置到文件"""
        target_file = self.config_file
        
        # 如果指定保存到项目目录
        if save_to_project and self.project_directory:
            project_config_dir = Path(self.project_directory) / ".vc-buddy"
            project_config_dir.mkdir(exist_ok=True)
            target_file = str(project_config_dir / "config.json")
        
        try:
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            with open(target_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not save config file {target_file}: {e}")
    
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
    
    @property
    def openai_api_key(self) -> str:
        """获取OpenAI API Key，优先使用配置文件，其次使用环境变量"""
        config_key = self.get("openai.api_key", "")
        if config_key:
            return config_key
        return os.getenv("OPENAI_API_KEY", "")
    
    @property
    def openai_api_url(self) -> str:
        """获取OpenAI API URL，优先使用配置文件，其次使用环境变量"""
        config_url = self.get("openai.api_url", "")
        if config_url:
            return config_url
        return os.getenv("OPENAI_API_URL", "https://api.openai.com/v1")
    
    def set_openai_api_key(self, api_key: str):
        """设置OpenAI API Key到配置文件"""
        self.set("openai.api_key", api_key)
    
    def set_openai_api_url(self, api_url: str):
        """设置OpenAI API URL到配置文件"""
        self.set("openai.api_url", api_url)
    
    def has_openai_api_key(self) -> bool:
        """检查是否有可用的OpenAI API Key"""
        return bool(self.openai_api_key)

# 全局配置实例
config_manager = ConfigManager()

def get_project_config_manager(project_directory: str) -> ConfigManager:
    """获取项目特定的配置管理器"""
    return ConfigManager(project_directory=project_directory) 
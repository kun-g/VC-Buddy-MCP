#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据统计模块
使用Amplitude进行用户行为统计
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json
import threading
import time

# 尝试导入Amplitude，如果不存在则使用模拟版本
try:
    from amplitude import Amplitude, BaseEvent
    AMPLITUDE_AVAILABLE = True
except ImportError:
    logging.warning("Amplitude library not available, using mock analytics")
    AMPLITUDE_AVAILABLE = False
    
    # 模拟类定义
    class BaseEvent:
        def __init__(self, event_type: str, device_id: str = None, event_properties: Dict[str, Any] = None):
            self.event_type = event_type
            self.device_id = device_id
            self.event_properties = event_properties or {}
    
    class Amplitude:
        def __init__(self, api_key: str):
            self.api_key = api_key
        
        def track(self, event: BaseEvent):
            logging.info(f"Mock analytics: {event.event_type} - {event.event_properties}")


class AnalyticsManager:
    """数据统计管理器"""
    
    def __init__(self, api_key: str = "19f4e9af0ddd8891fab01dd53202af2f", config_dir: str = None):
        self.api_key = api_key
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".vc-buddy"
        self.config_file = self.config_dir / "analytics_config.json"
        self.device_id = self._get_or_create_device_id()
        
        # 初始化Amplitude
        self.amplitude = Amplitude(api_key) if AMPLITUDE_AVAILABLE else Amplitude(api_key)
        
        # 统计配置
        self.enabled = self._load_analytics_config()
        
        # 线程安全锁
        self._lock = threading.Lock()
        
        logging.info(f"Analytics initialized: enabled={self.enabled}, device_id={self.device_id}")
    
    def _get_or_create_device_id(self) -> str:
        """获取或创建设备ID"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'device_id' in config:
                        return config['device_id']
            
            # 生成新的设备ID
            import uuid
            device_id = str(uuid.uuid4())
            self._save_device_id(device_id)
            return device_id
            
        except Exception as e:
            logging.warning(f"Failed to get device ID: {e}")
            import uuid
            return str(uuid.uuid4())
    
    def _save_device_id(self, device_id: str):
        """保存设备ID到配置文件"""
        try:
            self.config_dir.mkdir(exist_ok=True)
            config = {'device_id': device_id, 'analytics_enabled': True}
            
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
                    config.update(existing_config)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logging.warning(f"Failed to save device ID: {e}")
    
    def _load_analytics_config(self) -> bool:
        """加载统计配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('analytics_enabled', True)
        except Exception as e:
            logging.warning(f"Failed to load analytics config: {e}")
        
        return True  # 默认启用
    
    def set_analytics_enabled(self, enabled: bool):
        """设置统计开关"""
        self.enabled = enabled
        try:
            self.config_dir.mkdir(exist_ok=True)
            config = {'device_id': self.device_id, 'analytics_enabled': enabled}
            
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    existing_config = json.load(f)
                    config.update(existing_config)
                    config['analytics_enabled'] = enabled
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logging.warning(f"Failed to save analytics config: {e}")
    
    def track_event(self, event_type: str, properties: Dict[str, Any] = None):
        """跟踪事件"""
        if not self.enabled:
            return
        
        try:
            with self._lock:
                event_properties = properties or {}
                event_properties['timestamp'] = time.time()
                
                event = BaseEvent(
                    event_type=event_type,
                    device_id=self.device_id,
                    event_properties=event_properties
                )
                
                self.amplitude.track(event)
                logging.debug(f"Tracked event: {event_type} - {event_properties}")
                
        except Exception as e:
            logging.error(f"Failed to track event {event_type}: {e}")
    
    # 具体的统计方法
    def track_app_opened(self, source: str = "unknown"):
        """跟踪应用开启"""
        self.track_event("app_opened", {"source": source})
    
    def track_shortcut_used(self, shortcut_name: str, action: str = "unknown"):
        """跟踪快捷键使用"""
        self.track_event("shortcut_used", {
            "shortcut_name": shortcut_name,
            "action": action
        })
    
    def track_button_clicked(self, button_name: str, context: str = "unknown"):
        """跟踪按钮点击"""
        self.track_event("button_clicked", {
            "button_name": button_name,
            "context": context
        })
    
    def track_todo_action(self, action: str, todo_title: str = None, todo_level: int = None):
        """跟踪TODO相关操作"""
        properties = {"action": action}
        if todo_title:
            properties["todo_title_length"] = len(todo_title)  # 不记录具体标题，只记录长度
        if todo_level:
            properties["todo_level"] = todo_level
            
        self.track_event("todo_action", properties)
    
    def track_voice_action(self, action: str, duration: float = None):
        """跟踪语音相关操作"""
        properties = {"action": action}
        if duration:
            properties["duration"] = duration
            
        self.track_event("voice_action", properties)
    
    def track_config_action(self, action: str, config_type: str = None):
        """跟踪配置相关操作"""
        properties = {"action": action}
        if config_type:
            properties["config_type"] = config_type
            
        self.track_event("config_action", properties)


# 全局单例
_analytics_instance: Optional[AnalyticsManager] = None


def get_analytics_manager() -> AnalyticsManager:
    """获取统计管理器单例"""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = AnalyticsManager()
    return _analytics_instance


def init_analytics(api_key: str = None, config_dir: str = None) -> AnalyticsManager:
    """初始化统计管理器"""
    global _analytics_instance
    if api_key:
        _analytics_instance = AnalyticsManager(api_key, config_dir)
    else:
        _analytics_instance = AnalyticsManager(config_dir=config_dir)
    return _analytics_instance


# 便捷函数
def track_event(event_type: str, properties: Dict[str, Any] = None):
    """跟踪事件的便捷函数"""
    get_analytics_manager().track_event(event_type, properties)


def track_app_opened(source: str = "unknown"):
    """跟踪应用开启的便捷函数"""
    get_analytics_manager().track_app_opened(source)


def track_shortcut_used(shortcut_name: str, action: str = "unknown"):
    """跟踪快捷键使用的便捷函数"""
    get_analytics_manager().track_shortcut_used(shortcut_name, action)


def track_button_clicked(button_name: str, context: str = "unknown"):
    """跟踪按钮点击的便捷函数"""
    get_analytics_manager().track_button_clicked(button_name, context)


def track_todo_action(action: str, todo_title: str = None, todo_level: int = None):
    """跟踪TODO操作的便捷函数"""
    get_analytics_manager().track_todo_action(action, todo_title, todo_level)


def track_voice_action(action: str, duration: float = None):
    """跟踪语音操作的便捷函数"""
    get_analytics_manager().track_voice_action(action, duration)


def track_config_action(action: str, config_type: str = None):
    """跟踪配置操作的便捷函数"""
    get_analytics_manager().track_config_action(action, config_type) 
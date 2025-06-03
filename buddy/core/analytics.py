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
import platform
import sys

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
            logging.debug(f"Mock analytics: {event.event_type} - {event.event_properties}")


class AnalyticsManager:
    """数据统计管理器"""
    
    def __init__(self, api_key: str = "19f4e9af0ddd8891fab01dd53202af2f", config_dir: str = None):
        self.api_key = api_key
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".vc-buddy"
        self.config_file = self.config_dir / "analytics_config.json"
        self.device_id = self._get_or_create_device_id()
        
        # 收集平台信息
        self.platform_info = self._collect_platform_info()
        
        # 初始化Amplitude
        self.amplitude = Amplitude(api_key) if AMPLITUDE_AVAILABLE else Amplitude(api_key)
        
        # 统计配置
        self.enabled = self._load_analytics_config()
        
        # 线程安全锁
        self._lock = threading.Lock()
        
        logging.info(f"Analytics initialized: enabled={self.enabled}, device_id={self.device_id}, platform={self.platform_info.get('os_name')}")
    
    def _collect_platform_info(self) -> Dict[str, Any]:
        """收集平台信息（隐私安全）"""
        try:
            info = {
                'os_name': platform.system(),  # Windows, Darwin, Linux
                'os_version': platform.release(),  # 操作系统版本
                'architecture': platform.machine(),  # x86_64, arm64, etc.
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'platform_summary': platform.platform(),  # 综合平台信息
            }
            
            # 针对不同操作系统添加特定信息
            if info['os_name'] == 'Darwin':  # macOS
                try:
                    # 从platform获取macOS版本信息
                    mac_version = platform.mac_ver()[0]
                    if mac_version:
                        info['os_friendly_name'] = f"macOS {mac_version}"
                    else:
                        info['os_friendly_name'] = "macOS"
                except Exception:
                    info['os_friendly_name'] = "macOS"
            elif info['os_name'] == 'Windows':
                try:
                    # Windows版本信息
                    win_version = platform.win32_ver()[0]
                    if win_version:
                        info['os_friendly_name'] = f"Windows {win_version}"
                    else:
                        info['os_friendly_name'] = "Windows"
                except Exception:
                    info['os_friendly_name'] = "Windows"
            elif info['os_name'] == 'Linux':
                try:
                    # Linux发行版信息
                    linux_dist = platform.freedesktop_os_release()
                    if linux_dist and 'NAME' in linux_dist:
                        info['os_friendly_name'] = linux_dist['NAME']
                    else:
                        info['os_friendly_name'] = "Linux"
                except Exception:
                    info['os_friendly_name'] = "Linux"
            else:
                info['os_friendly_name'] = info['os_name']
            
            # 检测是否为Apple Silicon
            if info['os_name'] == 'Darwin' and info['architecture'] == 'arm64':
                info['is_apple_silicon'] = True
            else:
                info['is_apple_silicon'] = False
            
            # 检测处理器类型
            if info['architecture'] in ['x86_64', 'AMD64']:
                info['processor_type'] = 'x64'
            elif info['architecture'] in ['arm64', 'aarch64']:
                info['processor_type'] = 'arm64'
            elif info['architecture'].startswith('arm'):
                info['processor_type'] = 'arm'
            else:
                info['processor_type'] = info['architecture']
            
            return info
            
        except Exception as e:
            logging.warning(f"Failed to collect platform info: {e}")
            return {
                'os_name': 'unknown',
                'os_version': 'unknown',
                'architecture': 'unknown',
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
                'platform_summary': 'unknown',
                'os_friendly_name': 'unknown',
                'is_apple_silicon': False,
                'processor_type': 'unknown'
            }
    
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
                
                # 自动添加平台信息到所有事件
                event_properties.update({
                    'platform_os': self.platform_info['os_name'],
                    'platform_os_version': self.platform_info['os_version'],
                    'platform_architecture': self.platform_info['architecture'],
                    'platform_python_version': self.platform_info['python_version'],
                    'platform_friendly_name': self.platform_info['os_friendly_name'],
                    'platform_processor_type': self.platform_info['processor_type'],
                    'platform_is_apple_silicon': self.platform_info['is_apple_silicon'],
                })
                
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
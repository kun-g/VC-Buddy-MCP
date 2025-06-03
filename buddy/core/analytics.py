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

# 导入版本获取模块
from .version import get_app_version

# 尝试导入Amplitude，如果不存在则使用模拟版本
try:
    from amplitude import Amplitude, BaseEvent, Identify, EventOptions
    AMPLITUDE_AVAILABLE = True
except ImportError:
    logging.warning("Amplitude library not available, using mock analytics")
    AMPLITUDE_AVAILABLE = False
    
    # 模拟类定义
    class BaseEvent:
        def __init__(self, event_type: str, device_id: str = None, user_id: str = None, event_properties: Dict[str, Any] = None):
            self.event_type = event_type
            self.device_id = device_id
            self.user_id = user_id
            self.event_properties = event_properties or {}
    
    class Identify:
        def __init__(self):
            self.properties = {}
        
        def set(self, property: str, value: Any):
            self.properties[property] = value
            return self
    
    class EventOptions:
        def __init__(self, device_id: str = None, user_id: str = None):
            self.device_id = device_id
            self.user_id = user_id
    
    class Amplitude:
        def __init__(self, api_key: str):
            self.api_key = api_key
        
        def track(self, event: BaseEvent):
            logging.debug(f"Mock analytics: {event.event_type} - {event.event_properties}")
        
        def identify(self, identify_obj: Identify, options: EventOptions = None):
            logging.debug(f"Mock identify: {identify_obj.properties}")


class AnalyticsManager:
    """数据统计管理器"""
    
    def __init__(self, api_key: str = "19f4e9af0ddd8891fab01dd53202af2f", config_dir: str = None):
        self.api_key = api_key
        self.config_dir = Path(config_dir) if config_dir else Path.home() / ".vc-buddy"
        self.config_file = self.config_dir / "analytics_config.json"
        self.device_id = self._get_or_create_device_id()
        
        # 获取应用版本号（缓存）
        self.app_version = get_app_version()
        
        # 收集平台信息
        self.platform_info = self._collect_platform_info()
        
        # 收集IP地址和网络信息
        self.network_info = self._collect_network_info()
        
        # 初始化Amplitude
        self.amplitude = Amplitude(api_key) if AMPLITUDE_AVAILABLE else Amplitude(api_key)
        
        # 统计配置
        self.enabled = self._load_analytics_config()
        
        # 线程安全锁
        self._lock = threading.Lock()
        
        # 用户属性是否已设置标记
        self._user_properties_set = False
        
        logging.info(f"Analytics initialized: enabled={self.enabled}, device_id={self.device_id}, version={self.app_version}, platform={self.platform_info.get('os_name')}, ip={self.network_info.get('public_ip', 'unknown')}")
    
    def _collect_network_info(self) -> Dict[str, Any]:
        """收集网络和IP信息（隐私安全）"""
        network_info = {}
        
        try:
            # 尝试获取公网IP地址
            import urllib.request
            import socket
            
            # 方法1: 使用httpbin.org获取公网IP
            try:
                with urllib.request.urlopen('https://httpbin.org/ip', timeout=3) as response:
                    data = json.loads(response.read().decode())
                    network_info['public_ip'] = data.get('origin', '').split(',')[0].strip()
            except Exception:
                # 方法2: 使用ipify.org备选
                try:
                    with urllib.request.urlopen('https://api.ipify.org?format=json', timeout=3) as response:
                        data = json.loads(response.read().decode())
                        network_info['public_ip'] = data.get('ip', 'unknown')
                except Exception:
                    network_info['public_ip'] = 'unknown'
            
            # 获取本地网络信息
            try:
                hostname = socket.gethostname()
                network_info['hostname'] = hostname
                
                # 获取本地IP地址
                local_ip = socket.gethostbyname(hostname)
                network_info['local_ip'] = local_ip
            except Exception:
                network_info['hostname'] = 'unknown'
                network_info['local_ip'] = 'unknown'
            
            # 检测网络类型
            if 'local_ip' in network_info:
                local_ip = network_info['local_ip']
                if local_ip.startswith('192.168.') or local_ip.startswith('10.') or local_ip.startswith('172.'):
                    network_info['network_type'] = 'private'
                elif local_ip == '127.0.0.1':
                    network_info['network_type'] = 'localhost'
                else:
                    network_info['network_type'] = 'public'
            else:
                network_info['network_type'] = 'unknown'
                
        except Exception as e:
            logging.warning(f"Failed to collect network info: {e}")
            network_info = {
                'public_ip': 'unknown',
                'local_ip': 'unknown',
                'hostname': 'unknown',
                'network_type': 'unknown'
            }
        
        return network_info
    
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
            
            # 收集语言和地区信息
            try:
                import locale
                
                # 获取系统默认语言环境
                default_locale = locale.getdefaultlocale()
                if default_locale[0]:
                    info['system_language'] = default_locale[0]
                    # 解析语言代码 (例如: 'zh_CN' -> 语言='zh', 国家='CN')
                    if '_' in default_locale[0]:
                        lang_parts = default_locale[0].split('_')
                        info['language_code'] = lang_parts[0]  # zh, en, ja, etc.
                        info['country_code'] = lang_parts[1]   # CN, US, JP, etc.
                    else:
                        info['language_code'] = default_locale[0]
                        info['country_code'] = 'unknown'
                else:
                    info['system_language'] = 'unknown'
                    info['language_code'] = 'unknown'
                    info['country_code'] = 'unknown'
                
                # 获取系统编码
                if default_locale[1]:
                    info['system_encoding'] = default_locale[1]
                else:
                    info['system_encoding'] = 'unknown'
                
                # 获取当前语言环境设置
                try:
                    current_locale = locale.getlocale()
                    if current_locale[0]:
                        info['current_locale'] = current_locale[0]
                    else:
                        info['current_locale'] = 'C'  # 默认C locale
                except Exception:
                    info['current_locale'] = 'unknown'
                
                # 尝试获取更详细的地区信息（仅在特定平台）
                if info['os_name'] == 'Darwin':  # macOS
                    try:
                        import subprocess
                        # 获取macOS的地区设置
                        result = subprocess.run(['defaults', 'read', '-g', 'AppleLocale'], 
                                              capture_output=True, text=True, timeout=2)
                        if result.returncode == 0:
                            info['macos_locale'] = result.stdout.strip()
                    except Exception:
                        pass
                        
                elif info['os_name'] == 'Windows':  # Windows
                    try:
                        import subprocess
                        # 获取Windows的地区设置
                        result = subprocess.run(['powershell', '-Command', 
                                               'Get-Culture | Select-Object Name'], 
                                              capture_output=True, text=True, timeout=2)
                        if result.returncode == 0:
                            lines = result.stdout.strip().split('\n')
                            if len(lines) > 2:  # 跳过标题行
                                info['windows_culture'] = lines[2].strip()
                    except Exception:
                        pass
                
            except Exception as e:
                # 如果语言检测失败，设置默认值
                logging.warning(f"Failed to detect language/locale: {e}")
                info.update({
                    'system_language': 'unknown',
                    'language_code': 'unknown', 
                    'country_code': 'unknown',
                    'system_encoding': 'unknown',
                    'current_locale': 'unknown'
                })
            
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
                'python_version': 'unknown',
                'platform_summary': 'unknown',
                'os_friendly_name': 'unknown',
                'processor_type': 'unknown',
                'is_apple_silicon': False,
                'language_code': 'unknown',
                'country_code': 'unknown',
                'system_language': 'unknown',
                'system_encoding': 'unknown',
                'current_locale': 'unknown'
            }

    def _setup_user_properties(self):
        """设置用户属性（只调用一次）"""
        if self._user_properties_set or not self.enabled:
            return
        
        try:
            with self._lock:
                if self._user_properties_set:  # 双重检查锁定
                    return
                
                # 创建用户属性标识对象
                identify_obj = Identify()
                
                # 设置平台相关的用户属性
                identify_obj.set("platform_os", self.platform_info['os_name'])
                identify_obj.set("platform_os_version", self.platform_info['os_version'])
                identify_obj.set("platform_architecture", self.platform_info['architecture'])
                identify_obj.set("platform_python_version", self.platform_info['python_version'])
                identify_obj.set("platform_friendly_name", self.platform_info['os_friendly_name'])
                identify_obj.set("platform_processor_type", self.platform_info['processor_type'])
                identify_obj.set("platform_is_apple_silicon", self.platform_info['is_apple_silicon'])
                
                # 语言和地区作为用户属性
                identify_obj.set("user_language_code", self.platform_info['language_code'])
                identify_obj.set("user_country_code", self.platform_info['country_code'])
                identify_obj.set("user_system_language", self.platform_info['system_language'])
                identify_obj.set("user_system_encoding", self.platform_info['system_encoding'])
                identify_obj.set("user_current_locale", self.platform_info['current_locale'])
                
                # 网络和IP信息作为用户属性
                identify_obj.set("user_public_ip", self.network_info['public_ip'])
                identify_obj.set("user_local_ip", self.network_info['local_ip'])
                identify_obj.set("user_hostname", self.network_info['hostname'])
                identify_obj.set("user_network_type", self.network_info['network_type'])
                
                # 设备标识
                identify_obj.set("device_id", self.device_id)
                
                # 发送用户属性标识
                event_options = EventOptions(device_id=self.device_id)
                self.amplitude.identify(identify_obj, event_options)
                
                self._user_properties_set = True
                logging.info(f"User properties set: language={self.platform_info['language_code']}, country={self.platform_info['country_code']}, ip={self.network_info['public_ip']}")
                
        except Exception as e:
            logging.error(f"Failed to setup user properties: {e}")

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
            # 确保用户属性已设置（只在第一次调用时设置）
            self._setup_user_properties()
            
            with self._lock:
                event_properties = properties or {}
                event_properties['timestamp'] = time.time()
                
                # 只添加基本的事件级别信息，不重复用户属性
                # 用户属性（语言、国家、平台等）已通过identify()设置
                event_properties.update({
                    'session_id': self.device_id,  # 使用设备ID作为会话标识
                    'app_version': self.app_version,  # 动态获取的应用版本
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
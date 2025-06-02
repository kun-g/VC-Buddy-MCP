#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据统计模块的单元测试
测试AnalyticsManager的各种功能
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
import sys

# 添加buddy模块到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from buddy.core.analytics import AnalyticsManager, get_analytics_manager, track_event, track_app_opened


class TestAnalyticsManager(unittest.TestCase):
    """测试AnalyticsManager类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录作为配置目录
        self.temp_dir = tempfile.mkdtemp()
        self.analytics = AnalyticsManager(config_dir=self.temp_dir)
    
    def tearDown(self):
        """测试后清理"""
        # 清理临时目录
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_device_id_creation(self):
        """测试设备ID创建"""
        self.assertIsNotNone(self.analytics.device_id)
        self.assertTrue(len(self.analytics.device_id) > 0)
        
        # 验证设备ID是UUID格式
        import uuid
        try:
            uuid.UUID(self.analytics.device_id)
        except ValueError:
            self.fail("Device ID is not a valid UUID")
    
    def test_device_id_persistence(self):
        """测试设备ID持久化"""
        original_device_id = self.analytics.device_id
        
        # 创建新的AnalyticsManager实例，应该使用相同的设备ID
        new_analytics = AnalyticsManager(config_dir=self.temp_dir)
        self.assertEqual(original_device_id, new_analytics.device_id)
    
    def test_analytics_enabled_config(self):
        """测试统计开关配置"""
        # 默认应该启用
        self.assertTrue(self.analytics.enabled)
        
        # 禁用统计
        self.analytics.set_analytics_enabled(False)
        self.assertFalse(self.analytics.enabled)
        
        # 重新启用
        self.analytics.set_analytics_enabled(True)
        self.assertTrue(self.analytics.enabled)
    
    def test_track_event(self):
        """测试事件跟踪"""
        # 这个测试主要验证方法不会抛出异常
        try:
            self.analytics.track_event("test_event", {"key": "value"})
        except Exception as e:
            self.fail(f"track_event raised an exception: {e}")
    
    def test_specific_tracking_methods(self):
        """测试特定的跟踪方法"""
        try:
            self.analytics.track_app_opened("test")
            self.analytics.track_shortcut_used("Ctrl+C", "copy")
            self.analytics.track_button_clicked("save", "toolbar")
            self.analytics.track_todo_action("click", "Test TODO", 1)
            self.analytics.track_voice_action("start_recording")
            self.analytics.track_config_action("update", "api_key")
        except Exception as e:
            self.fail(f"Specific tracking method raised an exception: {e}")
    
    def test_disabled_analytics(self):
        """测试禁用统计时的行为"""
        self.analytics.set_analytics_enabled(False)
        
        # 禁用时调用跟踪方法应该不会抛出异常
        try:
            self.analytics.track_event("test_event")
            self.analytics.track_app_opened("test")
        except Exception as e:
            self.fail(f"Disabled analytics raised an exception: {e}")


class TestAnalyticsGlobalFunctions(unittest.TestCase):
    """测试全局便捷函数"""
    
    def test_get_analytics_manager(self):
        """测试获取统计管理器单例"""
        manager1 = get_analytics_manager()
        manager2 = get_analytics_manager()
        
        # 应该返回同一个实例
        self.assertIs(manager1, manager2)
    
    def test_convenience_functions(self):
        """测试便捷函数"""
        try:
            track_event("test_event", {"test": "data"})
            track_app_opened("unittest")
        except Exception as e:
            self.fail(f"Convenience function raised an exception: {e}")


class TestAnalyticsConfig(unittest.TestCase):
    """测试统计配置功能"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_file_creation(self):
        """测试配置文件创建"""
        analytics = AnalyticsManager(config_dir=self.temp_dir)
        config_file = Path(self.temp_dir) / "analytics_config.json"
        
        # 配置文件应该被创建
        self.assertTrue(config_file.exists())
        
        # 验证配置文件内容
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.assertIn('device_id', config)
            self.assertIn('analytics_enabled', config)
    
    def test_config_persistence(self):
        """测试配置持久化"""
        analytics = AnalyticsManager(config_dir=self.temp_dir)
        
        # 修改配置
        analytics.set_analytics_enabled(False)
        
        # 创建新实例，配置应该被保持
        new_analytics = AnalyticsManager(config_dir=self.temp_dir)
        self.assertFalse(new_analytics.enabled)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2) 
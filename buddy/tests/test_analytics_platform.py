#!/usr/bin/env python3
"""
平台统计功能测试

测试埋点系统中的平台信息收集功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from buddy.core.analytics import AnalyticsManager, get_analytics_manager
import platform
import json


def test_platform_info_collection():
    """测试平台信息收集"""
    print("=== 平台信息收集测试 ===")
    
    # 创建临时的analytics管理器
    analytics = AnalyticsManager(config_dir="/tmp/test_analytics")
    
    print(f"设备ID: {analytics.device_id}")
    print(f"统计启用状态: {analytics.enabled}")
    
    print("\n收集到的平台信息:")
    for key, value in analytics.platform_info.items():
        print(f"  {key}: {value}")
    
    # 验证关键字段存在
    required_fields = [
        'os_name', 'os_version', 'architecture', 'python_version',
        'platform_summary', 'os_friendly_name', 'is_apple_silicon', 'processor_type'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in analytics.platform_info:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"\n❌ 缺少字段: {missing_fields}")
        return False
    else:
        print("\n✅ 所有必需字段都存在")
        return True


def test_event_tracking_with_platform():
    """测试带平台信息的事件跟踪"""
    print("\n=== 事件跟踪测试 ===")
    
    analytics = AnalyticsManager(config_dir="/tmp/test_analytics")
    
    # 模拟跟踪一个事件
    test_properties = {
        "test_property": "test_value",
        "action": "test_action"
    }
    
    print("跟踪测试事件...")
    analytics.track_event("test_event", test_properties)
    
    print("✅ 事件跟踪完成（包含平台信息）")
    return True


def test_shortcut_tracking():
    """测试快捷键统计"""
    print("\n=== 快捷键统计测试 ===")
    
    analytics = get_analytics_manager()
    
    shortcuts_to_test = [
        ("Ctrl+R", "toggle_recording"),
        ("Ctrl+E", "send_message"),
        ("Ctrl+,", "open_settings")
    ]
    
    for shortcut, action in shortcuts_to_test:
        print(f"测试快捷键: {shortcut} -> {action}")
        analytics.track_shortcut_used(shortcut, action)
    
    print("✅ 快捷键统计测试完成")
    return True


def test_config_action_tracking():
    """测试配置操作统计"""
    print("\n=== 配置操作统计测试 ===")
    
    analytics = get_analytics_manager()
    
    config_actions = [
        ("save_settings", "openai_config"),
        ("test_connection", "openai_api"),
        ("toggle_api_key_visibility", "security")
    ]
    
    for action, config_type in config_actions:
        print(f"测试配置操作: {action} -> {config_type}")
        analytics.track_config_action(action, config_type)
    
    print("✅ 配置操作统计测试完成")
    return True


def display_platform_summary():
    """显示平台信息摘要"""
    print("\n=== 当前平台摘要 ===")
    
    print(f"操作系统: {platform.system()}")
    print(f"版本: {platform.release()}")
    print(f"架构: {platform.machine()}")
    print(f"平台: {platform.platform()}")
    
    # 检测特殊平台
    if platform.system() == 'Darwin' and platform.machine() == 'arm64':
        print("🍎 检测到 Apple Silicon Mac")
    elif platform.system() == 'Windows':
        print("🪟 检测到 Windows 系统")
    elif platform.system() == 'Linux':
        print("🐧 检测到 Linux 系统")


def main():
    """主测试函数"""
    print("平台统计功能测试")
    print("=" * 50)
    
    # 显示平台信息
    display_platform_summary()
    
    # 运行测试
    tests = [
        test_platform_info_collection,
        test_event_tracking_with_platform,
        test_shortcut_tracking,
        test_config_action_tracking
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ 测试失败: {test_func.__name__} - {e}")
    
    print(f"\n测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！平台统计功能正常工作。")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查实现。")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
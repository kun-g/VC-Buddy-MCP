#!/usr/bin/env python3
"""
窗口几何保存功能测试脚本
测试 QML Answer Box 的窗口位置和大小保存恢复功能
"""

import sys
import json
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from buddy.ui.answer_box_qml import AnswerBoxQML


def test_window_geometry():
    """测试窗口几何保存功能"""
    print("🧪 测试窗口几何保存功能...")
    
    try:
        # 准备测试数据
        test_data = {
            "summary": "窗口几何测试 - 请移动和调整窗口大小，然后关闭窗口。再次运行测试以验证位置是否被保存。",
            "project_directory": str(project_root)
        }
        
        # 模拟标准输入
        import io
        sys.stdin = io.StringIO(json.dumps(test_data))
        
        print("🚀 启动 QML Answer Box...")
        print("💡 测试步骤:")
        print("   1. 移动窗口到不同位置")
        print("   2. 调整窗口大小")
        print("   3. 关闭窗口")
        print("   4. 再次运行此脚本验证位置是否保存")
        print("\n⚠️  按 Ctrl+C 或关闭窗口来结束测试")
        
        # 启动应用
        answer_box = AnswerBoxQML()
        return_code = answer_box.run()
        
        print(f"🏁 应用退出，返回码: {return_code}")
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断测试")
        return True
    except Exception as e:
        print(f"❌ 窗口几何测试失败: {e}")
        return False
    finally:
        # 恢复标准输入
        sys.stdin = sys.__stdin__


def check_saved_geometry():
    """检查保存的几何信息"""
    print("\n🔍 检查保存的几何信息...")
    
    try:
        from PySide6.QtCore import QSettings
        from buddy.ui.config import config_manager
        
        settings = QSettings(
            config_manager.organization_name,
            config_manager.application_name
        )
        
        x = settings.value("window/x", -1, type=int)
        y = settings.value("window/y", -1, type=int)
        width = settings.value("window/width", -1, type=int)
        height = settings.value("window/height", -1, type=int)
        
        if x >= 0 and y >= 0 and width > 0 and height > 0:
            print(f"✅ 找到保存的几何信息:")
            print(f"   位置: ({x}, {y})")
            print(f"   大小: {width} x {height}")
            return True
        else:
            print("❌ 未找到有效的保存几何信息")
            return False
            
    except Exception as e:
        print(f"❌ 检查几何信息时出错: {e}")
        return False


def clear_saved_geometry():
    """清除保存的几何信息"""
    print("\n🧹 清除保存的几何信息...")
    
    try:
        from PySide6.QtCore import QSettings
        from buddy.ui.config import config_manager
        
        settings = QSettings(
            config_manager.organization_name,
            config_manager.application_name
        )
        
        settings.remove("window/x")
        settings.remove("window/y")
        settings.remove("window/width")
        settings.remove("window/height")
        settings.sync()
        
        print("✅ 几何信息已清除")
        return True
        
    except Exception as e:
        print(f"❌ 清除几何信息时出错: {e}")
        return False


def main():
    """主函数"""
    print("🪟 VC-Buddy 窗口几何保存功能测试")
    print("=" * 50)
    
    # 检查当前保存的几何信息
    has_saved = check_saved_geometry()
    
    print("\n" + "=" * 50)
    print("🤔 选择测试选项:")
    print("1. 启动界面测试窗口几何保存")
    print("2. 清除保存的几何信息")
    print("3. 退出")
    
    choice = input("\n请选择 (1-3): ").strip()
    
    if choice == "1":
        print("\n" + "=" * 50)
        success = test_window_geometry()
        
        if success:
            print("\n✅ 测试完成！")
            if not has_saved:
                print("💡 提示: 再次运行选项1以验证位置恢复功能")
        else:
            print("\n❌ 测试失败")
            
    elif choice == "2":
        print("\n" + "=" * 50)
        if clear_saved_geometry():
            print("✅ 几何信息已清除，下次启动将居中显示")
        else:
            print("❌ 清除失败")
            
    elif choice == "3":
        print("👋 再见！")
        
    else:
        print("❌ 无效选择")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 
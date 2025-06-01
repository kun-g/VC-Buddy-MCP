#!/usr/bin/env python3
"""
样式系统测试脚本
测试 QSS 样式文件和 QML 主题系统的加载和应用
"""

import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from buddy.ui.style_manager import StyleManager, get_style_manager, load_default_styles
from buddy.ui.answer_box_qml import AnswerBoxQML


def test_style_manager():
    """测试样式管理器"""
    print("🧪 测试样式管理器...")
    
    manager = StyleManager()
    
    # 测试可用主题
    themes = manager.availableThemes
    print(f"📋 可用主题: {themes}")
    
    # 测试加载默认主题
    success = manager.load_theme("default")
    print(f"🎨 加载默认主题: {'✅ 成功' if success else '❌ 失败'}")
    
    # 测试获取主题颜色
    colors = manager.get_theme_colors()
    print(f"🎨 主题颜色: {colors}")
    
    # 测试 QSS 文件加载
    qss_content = manager.load_qss_file("styles.qss")
    qss_loaded = len(qss_content) > 0
    print(f"📄 QSS 文件加载: {'✅ 成功' if qss_loaded else '❌ 失败'} ({len(qss_content)} 字符)")
    
    return success and qss_loaded


def test_qml_theme():
    """测试 QML 主题系统"""
    print("\n🧪 测试 QML 主题系统...")
    
    # 检查 Theme.qml 文件
    theme_file = project_root / "buddy" / "ui" / "qml" / "Theme.qml"
    theme_exists = theme_file.exists()
    print(f"📄 Theme.qml 文件: {'✅ 存在' if theme_exists else '❌ 不存在'}")
    
    # 检查 qmldir 文件
    qmldir_file = project_root / "buddy" / "ui" / "qml" / "qmldir"
    qmldir_exists = qmldir_file.exists()
    print(f"📄 qmldir 文件: {'✅ 存在' if qmldir_exists else '❌ 不存在'}")
    
    if qmldir_exists:
        with open(qmldir_file, 'r', encoding='utf-8') as f:
            qmldir_content = f.read()
        has_theme_singleton = "singleton Theme" in qmldir_content
        print(f"🔗 Theme 单例注册: {'✅ 已注册' if has_theme_singleton else '❌ 未注册'}")
        print(f"📋 qmldir 内容:\n{qmldir_content}")
    
    return theme_exists and qmldir_exists


def test_qml_answer_box():
    """测试 QML Answer Box 样式集成"""
    print("\n🧪 测试 QML Answer Box 样式集成...")
    
    try:
        # 准备测试数据
        test_data = {
            "summary": "样式系统测试 - 这是一个测试摘要，用于验证 QML 主题系统是否正常工作。主题颜色应该正确应用到各个 UI 组件上。",
            "project_directory": str(project_root)
        }
        
        # 模拟标准输入
        import io
        sys.stdin = io.StringIO(json.dumps(test_data))
        
        print("🚀 启动 QML Answer Box...")
        print("💡 请检查界面是否使用了主题颜色:")
        print("   - 主色调应该是蓝色 (#2196F3)")
        print("   - 背景色应该是白色和浅灰色")
        print("   - 字体应该是统一的 Segoe UI")
        print("   - 间距应该是一致的")
        print("   - 按钮应该有悬停效果")
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
        print(f"❌ QML Answer Box 测试失败: {e}")
        return False
    finally:
        # 恢复标准输入
        sys.stdin = sys.__stdin__


def main():
    """主函数"""
    print("🎨 VC-Buddy 样式系统测试")
    print("=" * 50)
    
    results = []
    
    # 测试样式管理器
    results.append(test_style_manager())
    
    # 测试 QML 主题
    results.append(test_qml_theme())
    
    # 询问是否测试 QML 界面
    print("\n" + "=" * 50)
    user_input = input("🤔 是否启动 QML 界面进行可视化测试? (y/N): ").strip().lower()
    
    if user_input in ['y', 'yes']:
        results.append(test_qml_answer_box())
    else:
        print("⏭️  跳过 QML 界面测试")
    
    # 总结结果
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ 通过: {passed}/{total}")
    
    if all(results):
        print("🎉 所有测试通过！样式系统工作正常。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查相关配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
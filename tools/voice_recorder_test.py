#!/usr/bin/env python3
"""
语音录制器测试工具

这是一个完整的语音录制器测试界面，支持录音、播放录音和语音转写功能。
"""

import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QHBoxLayout, QWidget, QTextEdit, QLabel, QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from buddy.ui.voice_recorder import VoiceButton, PlayButton
from buddy.ui.config import ConfigManager
from settings_dialog import SettingsDialog


class VoiceRecorderTestWindow(QMainWindow):
    """语音录制器测试窗口"""
    
    def __init__(self):
        super().__init__()
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("语音录制器测试工具")
        self.setGeometry(100, 100, 600, 500)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题和设置按钮行
        title_layout = QHBoxLayout()
        
        title_label = QLabel("语音录制器测试工具")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        # 设置按钮
        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.setFixedSize(80, 35)
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """)
        title_layout.addWidget(self.settings_btn)
        
        main_layout.addLayout(title_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 创建语音按钮（传入配置管理器）
        self.voice_button = VoiceButton(config_manager=self.config_manager)
        self.voice_button.connect_transcription_ready(self.on_transcription_ready)
        button_layout.addWidget(self.voice_button)
        
        # 添加间距
        button_layout.addSpacing(15)
        
        # 创建播放按钮
        self.play_button = PlayButton(self.voice_button.recorder)
        button_layout.addWidget(self.play_button)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # 按钮说明
        button_info_layout = QHBoxLayout()
        button_info_layout.addStretch()
        
        record_info = QLabel("🎤 录音")
        record_info.setAlignment(Qt.AlignCenter)
        record_info.setStyleSheet("color: #666; font-size: 12px;")
        button_info_layout.addWidget(record_info)
        
        button_info_layout.addSpacing(15)
        
        play_info = QLabel("🔊 播放")
        play_info.setAlignment(Qt.AlignCenter)
        play_info.setStyleSheet("color: #666; font-size: 12px;")
        button_info_layout.addWidget(play_info)
        
        button_info_layout.addStretch()
        main_layout.addLayout(button_info_layout)
        
        # API Key 状态显示
        self.api_status_label = QLabel()
        self.update_api_status_display()
        self.api_status_label.setAlignment(Qt.AlignCenter)
        self.api_status_label.setStyleSheet("font-size: 13px; padding: 8px; border-radius: 4px; margin: 5px;")
        main_layout.addWidget(self.api_status_label)
        
        # 说明文字
        instruction_label = QLabel("点击麦克风按钮开始录音，再次点击停止录音并进行语音转写\n录音完成后，可以点击喇叭按钮播放录音")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setWordWrap(True)
        instruction_label.setStyleSheet("color: #666; font-size: 14px; line-height: 1.5;")
        main_layout.addWidget(instruction_label)
        
        # 转写结果显示区域
        result_label = QLabel("转写结果:")
        result_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        main_layout.addWidget(result_label)
        
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("转写结果将显示在这里...")
        self.result_text.setMinimumHeight(200)
        self.result_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #f9f9f9;
            }
            QTextEdit:focus {
                border-color: #4CAF50;
            }
        """)
        main_layout.addWidget(self.result_text)
        
        # 状态提示
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888; font-size: 12px; padding: 5px;")
        main_layout.addWidget(self.status_label)
        
        # 连接录音器的信号
        self.voice_button.recorder.recording_started.connect(self.on_recording_started)
        self.voice_button.recorder.recording_stopped.connect(self.on_recording_stopped)
        self.voice_button.recorder.error_occurred.connect(self.on_error_occurred)
        self.voice_button.recorder.audio_saved.connect(self.on_audio_saved)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
    
    def update_api_status_display(self):
        """更新API Key状态显示"""
        if self.config_manager.has_openai_api_key():
            self.api_status_label.setText("✅ OpenAI API Key 已配置，语音转写功能可用")
            self.api_status_label.setStyleSheet(
                "color: #155724; background-color: #d4edda; border: 1px solid #c3e6cb; "
                "font-size: 13px; padding: 8px; border-radius: 4px; margin: 5px;"
            )
        else:
            self.api_status_label.setText("⚠️ 未配置 OpenAI API Key，语音转写功能不可用（录音和播放功能正常）")
            self.api_status_label.setStyleSheet(
                "color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; "
                "font-size: 13px; padding: 8px; border-radius: 4px; margin: 5px;"
            )
    
    def open_settings(self):
        """打开设置对话框"""
        dialog = SettingsDialog(self.config_manager, self)
        if dialog.exec() == SettingsDialog.Accepted:
            # 设置保存后，更新录音器的API配置
            api_key = self.config_manager.openai_api_key
            api_url = self.config_manager.openai_api_url
            self.voice_button.recorder.update_api_config(api_key, api_url)
            # 更新状态显示
            self.update_api_status_display()
    
    def on_transcription_ready(self, text: str):
        """处理转写结果"""
        current_text = self.result_text.toPlainText()
        if current_text:
            new_text = current_text + "\n\n" + text
        else:
            new_text = text
        self.result_text.setPlainText(new_text)
        
        # 滚动到底部
        cursor = self.result_text.textCursor()
        cursor.movePosition(cursor.End)
        self.result_text.setTextCursor(cursor)
        
        self.status_label.setText("转写完成")
        self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px; padding: 5px;")
    
    def on_recording_started(self):
        """录音开始时的处理"""
        self.status_label.setText("正在录音...")
        self.status_label.setStyleSheet("color: #ff4444; font-size: 12px; padding: 5px;")
        # 禁用播放按钮
        self.play_button.setEnabled(False)
    
    def on_recording_stopped(self):
        """录音停止时的处理"""
        if self.config_manager.has_openai_api_key():
            self.status_label.setText("录音完成，正在转写...")
            self.status_label.setStyleSheet("color: #FF9800; font-size: 12px; padding: 5px;")
        else:
            self.status_label.setText("录音完成，但未配置 API Key，无法转写")
            self.status_label.setStyleSheet("color: #FF5722; font-size: 12px; padding: 5px;")
    
    def on_audio_saved(self, file_path: str):
        """音频保存完成时的处理"""
        self.status_label.setText("音频已保存，可以播放录音")
        self.status_label.setStyleSheet("color: #2196F3; font-size: 12px; padding: 5px;")
    
    def on_error_occurred(self, error_message: str):
        """错误处理"""
        self.status_label.setText(f"错误: {error_message}")
        self.status_label.setStyleSheet("color: #f44336; font-size: 12px; padding: 5px;")
    
    def closeEvent(self, event):
        """窗口关闭时清理临时文件"""
        self.voice_button.recorder.cleanup()
        event.accept()


def check_dependencies():
    """检查依赖是否已安装"""
    missing_deps = []
    
    try:
        import pyaudio
    except ImportError:
        missing_deps.append("pyaudio")
    
    try:
        import openai
    except ImportError:
        missing_deps.append("openai")
    
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        missing_deps.append("PySide6")
    
    if missing_deps:
        print("❌ 缺少以下依赖:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n安装方法:")
        print(f"   pip install {' '.join(missing_deps)}")
        return False
    
    return True


def check_audio_permissions():
    """检查音频权限"""
    try:
        import pyaudio
        pa = pyaudio.PyAudio()
        
        # 检查输入设备
        input_devices = []
        for i in range(pa.get_device_count()):
            device_info = pa.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices.append(device_info['name'])
        
        # 检查输出设备  
        output_devices = []
        for i in range(pa.get_device_count()):
            device_info = pa.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0:
                output_devices.append(device_info['name'])
        
        pa.terminate()
        
        if not input_devices:
            print("⚠️  未检测到可用的音频输入设备")
            return False
            
        if not output_devices:
            print("⚠️  未检测到可用的音频输出设备")
            return False
        
        print("✅ 音频设备检查通过")
        print(f"   输入设备: {len(input_devices)} 个")
        print(f"   输出设备: {len(output_devices)} 个")
        
        return True
        
    except Exception as e:
        print(f"❌ 音频设备检查失败: {e}")
        return False


def main():
    """主函数"""
    print("🎤 语音录制器测试工具启动中...")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    # 检查音频设备
    if not check_audio_permissions():
        print("提示：如果是权限问题，请在系统设置中允许应用访问麦克风和扬声器")
    
    print("=" * 50)
    print("启动图形界面...")
    
    app = QApplication(sys.argv)
    
    window = VoiceRecorderTestWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
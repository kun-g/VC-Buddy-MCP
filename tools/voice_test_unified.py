#!/usr/bin/env python3
"""
统一语音测试工具

合并传统语音录制和流式语音输入功能的综合测试界面
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QTextEdit, QLabel, QPushButton, QTabWidget,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 检查依赖
def check_dependencies():
    """检查必要的依赖"""
    missing_deps = []
    
    try:
        import pyaudio
    except ImportError:
        missing_deps.append("pyaudio")
    
    try:
        import openai
    except ImportError:
        missing_deps.append("openai")
    
    return missing_deps

# 导入项目模块
try:
    from buddy.ui.config import ConfigManager
    from tools.settings_dialog import SettingsDialog
    IMPORTS_OK = True
except ImportError as e:
    print(f"导入错误: {e}")
    IMPORTS_OK = False


class UnifiedVoiceTestWindow(QMainWindow):
    """统一语音测试窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 检查依赖
        missing_deps = check_dependencies()
        if missing_deps:
            QMessageBox.critical(
                None, 
                "依赖缺失", 
                f"缺少以下依赖包:\n{', '.join(missing_deps)}\n\n请运行: pip install {' '.join(missing_deps)}"
            )
            sys.exit(1)
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 初始化界面
        self.init_ui()
        
        # 延迟初始化语音组件
        self.traditional_recorder = None
        self.streaming_recorder = None
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("统一语音测试工具")
        self.setGeometry(100, 100, 800, 700)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题和设置按钮行
        title_layout = QHBoxLayout()
        
        title_label = QLabel("统一语音测试工具")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        # API设置按钮
        self.settings_btn = QPushButton("⚙️ API设置")
        self.settings_btn.setFixedSize(100, 35)
        self.settings_btn.clicked.connect(self.open_api_settings)
        title_layout.addWidget(self.settings_btn)
        
        main_layout.addLayout(title_layout)
        
        # API Key 状态显示
        self.api_status_label = QLabel()
        self.update_api_status_display()
        self.api_status_label.setAlignment(Qt.AlignCenter)
        self.api_status_label.setStyleSheet("font-size: 13px; padding: 8px; border-radius: 4px; margin: 5px;")
        main_layout.addWidget(self.api_status_label)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 传统录音选项卡
        self.init_traditional_tab()
        
        # 流式录音选项卡
        self.init_streaming_tab()
        
        # 状态提示
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888; font-size: 12px; padding: 5px;")
        main_layout.addWidget(self.status_label)
        
        # 设置窗口样式
        self.setStyleSheet("QMainWindow { background-color: #ffffff; }")
    
    def init_traditional_tab(self):
        """初始化传统录音选项卡"""
        traditional_tab = QWidget()
        self.tab_widget.addTab(traditional_tab, "传统录音")
        
        layout = QVBoxLayout(traditional_tab)
        layout.setSpacing(15)
        
        # 说明文字
        instruction = QLabel(
            "传统录音模式：点击录音按钮开始录音，再次点击停止录音并进行语音转写。\n"
            "录音完成后可以播放录音文件。"
        )
        instruction.setWordWrap(True)
        instruction.setStyleSheet("color: #666; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(instruction)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 初始化传统录音按钮
        self.traditional_record_btn = QPushButton("🎤 开始录音")
        self.traditional_record_btn.setFixedSize(120, 40)
        self.traditional_record_btn.clicked.connect(self.toggle_traditional_recording)
        button_layout.addWidget(self.traditional_record_btn)
        
        button_layout.addSpacing(15)
        
        # 播放按钮
        self.play_btn = QPushButton("🔊 播放")
        self.play_btn.setFixedSize(80, 40)
        self.play_btn.clicked.connect(self.play_traditional_recording)
        self.play_btn.setEnabled(False)
        button_layout.addWidget(self.play_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 转写结果显示
        result_label = QLabel("转写结果:")
        result_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(result_label)
        
        self.traditional_result_text = QTextEdit()
        self.traditional_result_text.setPlaceholderText("转写结果将显示在这里...")
        self.traditional_result_text.setMinimumHeight(200)
        self.traditional_result_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #007bff;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #f8f9ff;
            }
            QTextEdit:focus { border-color: #0056b3; }
        """)
        layout.addWidget(self.traditional_result_text)
    
    def init_streaming_tab(self):
        """初始化流式录音选项卡"""
        streaming_tab = QWidget()
        self.tab_widget.addTab(streaming_tab, "流式录音")
        
        layout = QVBoxLayout(streaming_tab)
        layout.setSpacing(15)
        
        # 说明文字
        instruction = QLabel(
            "流式录音模式：边说边转写，实时显示结果。\n"
            "说出停止命令（如\"我说完了\"）自动停止，说出发送命令（如\"开工吧\"）自动发送。"
        )
        instruction.setWordWrap(True)
        instruction.setStyleSheet("color: #666; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(instruction)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 开始/停止流式录音按钮
        self.streaming_record_btn = QPushButton("🎤 开始流式录音")
        self.streaming_record_btn.setFixedSize(150, 40)
        self.streaming_record_btn.clicked.connect(self.toggle_streaming_recording)
        button_layout.addWidget(self.streaming_record_btn)
        
        button_layout.addSpacing(15)
        
        # 清空按钮
        self.clear_streaming_btn = QPushButton("🗑️ 清空")
        self.clear_streaming_btn.setFixedSize(80, 40)
        self.clear_streaming_btn.clicked.connect(self.clear_streaming_results)
        button_layout.addWidget(self.clear_streaming_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 实时转写显示
        realtime_label = QLabel("实时转写:")
        realtime_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(realtime_label)
        
        self.streaming_realtime_text = QTextEdit()
        self.streaming_realtime_text.setPlaceholderText("实时转写结果将在这里显示...")
        self.streaming_realtime_text.setMinimumHeight(150)
        self.streaming_realtime_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #28a745;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #f8fff9;
            }
            QTextEdit:focus { border-color: #20c997; }
        """)
        layout.addWidget(self.streaming_realtime_text)
        
        # 最终结果显示
        final_label = QLabel("最终结果:")
        final_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(final_label)
        
        self.streaming_final_text = QTextEdit()
        self.streaming_final_text.setPlaceholderText("完整的转写结果将在这里显示...")
        self.streaming_final_text.setMinimumHeight(150)
        self.streaming_final_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #007bff;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #f8f9ff;
            }
            QTextEdit:focus { border-color: #0056b3; }
        """)
        layout.addWidget(self.streaming_final_text)
    
    def init_traditional_recorder(self):
        """延迟初始化传统录音器"""
        if self.traditional_recorder is not None:
            return
        
        try:
            from buddy.ui.voice_recorder import VoiceRecorder
            self.traditional_recorder = VoiceRecorder(self.config_manager)
            
            # 连接信号
            self.traditional_recorder.recording_started.connect(self.on_traditional_recording_started)
            self.traditional_recorder.recording_stopped.connect(self.on_traditional_recording_stopped)
            self.traditional_recorder.transcription_ready.connect(self.on_traditional_transcription_ready)
            self.traditional_recorder.error_occurred.connect(self.on_traditional_error)
            self.traditional_recorder.audio_saved.connect(self.on_audio_saved)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"初始化传统录音器失败: {str(e)}")
    
    def init_streaming_recorder(self):
        """延迟初始化流式录音器"""
        if self.streaming_recorder is not None:
            return
        
        try:
            from buddy.ui.streaming_voice_recorder import StreamingVoiceRecorder
            from buddy.ui.voice_settings_dialog import VoiceSettingsDialog
            self.streaming_recorder = StreamingVoiceRecorder(self.config_manager)
            
            # 连接信号
            self.streaming_recorder.recording_started.connect(self.on_streaming_recording_started)
            self.streaming_recorder.recording_stopped.connect(self.on_streaming_recording_stopped)
            self.streaming_recorder.transcription_chunk_ready.connect(self.on_streaming_chunk_ready)
            self.streaming_recorder.final_transcription_ready.connect(self.on_streaming_final_ready)
            self.streaming_recorder.error_occurred.connect(self.on_streaming_error)
            self.streaming_recorder.stop_command_detected.connect(self.on_stop_command)
            self.streaming_recorder.send_command_detected.connect(self.on_send_command)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"初始化流式录音器失败: {str(e)}")
    
    def update_api_status_display(self):
        """更新API Key状态显示"""
        if self.config_manager.has_openai_api_key():
            self.api_status_label.setText("✅ OpenAI API Key 已配置，语音转写功能可用")
            self.api_status_label.setStyleSheet(
                "color: #155724; background-color: #d4edda; border: 1px solid #c3e6cb; "
                "font-size: 13px; padding: 8px; border-radius: 4px; margin: 5px;"
            )
        else:
            self.api_status_label.setText("⚠️ 未配置 OpenAI API Key，语音转写功能不可用")
            self.api_status_label.setStyleSheet(
                "color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; "
                "font-size: 13px; padding: 8px; border-radius: 4px; margin: 5px;"
            )
    
    def open_api_settings(self):
        """打开API设置对话框"""
        try:
            dialog = SettingsDialog(self.config_manager, self)
            if dialog.exec() == SettingsDialog.Accepted:
                # 更新API配置
                if self.traditional_recorder:
                    api_key = self.config_manager.openai_api_key
                    api_url = self.config_manager.openai_api_url
                    self.traditional_recorder.update_api_config(api_key, api_url)
                
                # 更新状态显示
                self.update_api_status_display()
                self.status_label.setText("API设置已更新")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开API设置失败: {str(e)}")
    
    # 传统录音相关方法
    def toggle_traditional_recording(self):
        """切换传统录音状态"""
        self.init_traditional_recorder()
        if not self.traditional_recorder:
            return
        
        if not self.traditional_recorder.is_recording:
            self.traditional_recorder.start_recording()
        else:
            self.traditional_recorder.stop_recording()
    
    def play_traditional_recording(self):
        """播放传统录音"""
        if self.traditional_recorder:
            self.traditional_recorder.play_last_recording()
    
    def on_traditional_recording_started(self):
        """传统录音开始"""
        self.traditional_record_btn.setText("⏹️ 停止录音")
        self.status_label.setText("传统录音中...")
    
    def on_traditional_recording_stopped(self):
        """传统录音停止"""
        self.traditional_record_btn.setText("🎤 开始录音")
        self.status_label.setText("传统录音已停止，正在转写...")
    
    def on_traditional_transcription_ready(self, text: str):
        """传统录音转写完成"""
        self.traditional_result_text.setPlainText(text)
        self.status_label.setText("传统录音转写完成")
    
    def on_traditional_error(self, error_message: str):
        """传统录音错误"""
        self.status_label.setText(f"传统录音错误: {error_message}")
        self.traditional_record_btn.setText("🎤 开始录音")
    
    def on_audio_saved(self, file_path: str):
        """音频文件保存完成"""
        self.play_btn.setEnabled(True)
        self.status_label.setText("音频已保存，可以播放")
    
    # 流式录音相关方法
    def toggle_streaming_recording(self):
        """切换流式录音状态"""
        self.init_streaming_recorder()
        if not self.streaming_recorder:
            return
        
        if not self.streaming_recorder.is_recording:
            self.streaming_recorder.start_recording()
        else:
            self.streaming_recorder.stop_recording()
    
    def clear_streaming_results(self):
        """清空流式录音结果"""
        self.streaming_realtime_text.clear()
        self.streaming_final_text.clear()
        if self.streaming_recorder:
            self.streaming_recorder.clear_transcription_buffer()
        self.status_label.setText("已清空流式录音结果")
    
    def on_streaming_recording_started(self):
        """流式录音开始"""
        print("测试工具: 流式录音已开始")
        self.streaming_record_btn.setText("⏹️ 停止流式录音")
        self.status_label.setText("流式录音中...实时转写")
    
    def on_streaming_recording_stopped(self):
        """流式录音停止"""
        print("测试工具: 流式录音已停止")
        self.streaming_record_btn.setText("🎤 开始流式录音")
        self.status_label.setText("流式录音已停止")
    
    def on_streaming_chunk_ready(self, chunk: str):
        """流式转写片段准备就绪"""
        print(f"测试工具: 收到转写片段: '{chunk}'")
        current_text = self.streaming_realtime_text.toPlainText()
        if current_text:
            self.streaming_realtime_text.setPlainText(current_text + " " + chunk)
        else:
            self.streaming_realtime_text.setPlainText(chunk)
        
        # 滚动到末尾
        cursor = self.streaming_realtime_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.streaming_realtime_text.setTextCursor(cursor)
    
    def on_streaming_final_ready(self, transcription: str):
        """流式转写最终结果准备就绪"""
        print(f"测试工具: 收到最终转写结果: '{transcription}'")
        self.streaming_final_text.setPlainText(transcription)
        self.status_label.setText("流式转写完成！")
    
    def on_streaming_error(self, error_message: str):
        """流式录音错误"""
        print(f"测试工具: 流式录音错误: {error_message}")
        self.status_label.setText(f"流式录音错误: {error_message}")
        self.streaming_record_btn.setText("🎤 开始流式录音")
    
    def on_stop_command(self, command: str):
        """检测到停止命令"""
        print(f"测试工具: 检测到停止命令: {command}")
        self.status_label.setText(f"检测到停止命令: {command}")
    
    def on_send_command(self, command: str):
        """检测到发送命令"""
        print(f"测试工具: 检测到发送命令: {command}")
        self.status_label.setText(f"检测到发送命令: {command} - 模拟发送中...")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.streaming_recorder and self.streaming_recorder.is_recording:
            self.streaming_recorder.stop_recording()
        if self.streaming_recorder:
            self.streaming_recorder.cleanup()
        if self.traditional_recorder:
            self.traditional_recorder.cleanup()
        event.accept()


def main():
    """主函数"""
    if not IMPORTS_OK:
        print("无法导入必要的模块，请检查项目结构和依赖")
        return 1
    
    # 设置异常处理
    import signal
    import sys
    
    def signal_handler(sig, frame):
        print('DEBUG: 收到中断信号，正在清理资源...')
        QApplication.quit()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    app = QApplication(sys.argv)
    
    # 设置应用程序异常处理
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        print(f"DEBUG: 未处理的异常: {exc_type.__name__}: {exc_value}")
        import traceback
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        
        # 尝试优雅地关闭应用
        try:
            QApplication.quit()
        except:
            pass
    
    sys.excepthook = handle_exception
    
    window = None
    try:
        print("DEBUG: 正在创建主窗口...")
        window = UnifiedVoiceTestWindow()
        print("DEBUG: 主窗口创建成功")
        
        print("DEBUG: 显示主窗口...")
        window.show()
        print("DEBUG: 主窗口显示成功")
        
        print("DEBUG: 启动应用程序事件循环...")
        result = app.exec()
        print(f"DEBUG: 应用程序事件循环结束，返回值: {result}")
        return result
        
    except Exception as e:
        print(f"DEBUG: 启动应用失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 尝试清理资源
        if window:
            try:
                window.close()
            except:
                pass
        
        try:
            app.quit()
        except:
            pass
        
        return 1
    finally:
        print("DEBUG: 程序清理完成")


if __name__ == "__main__":
    sys.exit(main()) 
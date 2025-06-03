#!/usr/bin/env python3
"""
语音设置对话框

允许用户自定义语音命令，包括停止录音和发送命令
"""

import json
from typing import List, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QMessageBox, QTabWidget, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

try:
    from .config import ConfigManager
except ImportError:
    # 如果作为脚本直接运行，需要添加路径
    import sys
    from pathlib import Path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir.parent))
    from ui.config import ConfigManager


class VoiceSettingsDialog(QDialog):
    """语音设置对话框"""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("语音设置")
        self.setModal(True)
        self.setFixedSize(500, 600)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("语音识别设置")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # 说明文字
        description = QLabel(
            "配置语音识别的自定义命令。支持中文和英文命令。\n"
            "录音时说出这些命令会触发相应的操作。"
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #666; font-size: 13px; margin-bottom: 10px;")
        main_layout.addWidget(description)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 停止命令选项卡
        stop_tab = QWidget()
        tab_widget.addTab(stop_tab, "停止录音命令")
        
        stop_layout = QVBoxLayout(stop_tab)
        stop_layout.setSpacing(10)
        
        stop_description = QLabel(
            "说出以下任意命令将停止录音：\n"
            "每行一个命令，支持中英文混合"
        )
        stop_description.setStyleSheet("color: #555; font-size: 12px;")
        stop_layout.addWidget(stop_description)
        
        self.stop_commands_edit = QTextEdit()
        self.stop_commands_edit.setPlaceholderText(
            "我说完了\n"
            "说完了\n"
            "结束\n"
            "停止录音\n"
            "停止\n"
            "finish\n"
            "done\n"
            "stop\n"
            "end"
        )
        self.stop_commands_edit.setMinimumHeight(200)
        stop_layout.addWidget(self.stop_commands_edit)
        
        # 发送命令选项卡
        send_tab = QWidget()
        tab_widget.addTab(send_tab, "发送命令")
        
        send_layout = QVBoxLayout(send_tab)
        send_layout.setSpacing(10)
        
        send_description = QLabel(
            "说出以下任意命令将停止录音并自动发送：\n"
            "每行一个命令，支持中英文混合"
        )
        send_description.setStyleSheet("color: #555; font-size: 12px;")
        send_layout.addWidget(send_description)
        
        self.send_commands_edit = QTextEdit()
        self.send_commands_edit.setPlaceholderText(
            "开工吧\n"
            "发送\n"
            "提交\n"
            "执行\n"
            "开始干活\n"
            "开始工作\n"
            "send\n"
            "submit\n"
            "go\n"
            "execute\n"
            "let's go"
        )
        self.send_commands_edit.setMinimumHeight(200)
        send_layout.addWidget(self.send_commands_edit)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 重置按钮
        reset_button = QPushButton("重置为默认")
        reset_button.clicked.connect(self.reset_to_defaults)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
        """)
        button_layout.addWidget(reset_button)
        
        button_layout.addSpacing(10)
        
        # 取消按钮
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        button_layout.addWidget(cancel_button)
        
        # 保存按钮
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save_settings)
        save_button.setDefault(True)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        button_layout.addWidget(save_button)
        
        main_layout.addLayout(button_layout)
    
    def load_settings(self):
        """加载当前设置"""
        # 加载停止命令
        stop_commands = self.config_manager.get("voice.stop_commands", [])
        if stop_commands:
            self.stop_commands_edit.setPlainText("\n".join(stop_commands))
        
        # 加载发送命令
        send_commands = self.config_manager.get("voice.send_commands", [])
        if send_commands:
            self.send_commands_edit.setPlainText("\n".join(send_commands))
    
    def save_settings(self):
        """保存设置"""
        try:
            # 解析停止命令
            stop_text = self.stop_commands_edit.toPlainText().strip()
            stop_commands = [
                cmd.strip() for cmd in stop_text.split('\n') 
                if cmd.strip()
            ] if stop_text else []
            
            # 解析发送命令
            send_text = self.send_commands_edit.toPlainText().strip()
            send_commands = [
                cmd.strip() for cmd in send_text.split('\n') 
                if cmd.strip()
            ] if send_text else []
            
            # 验证命令不为空
            if not stop_commands and not send_commands:
                QMessageBox.warning(
                    self, 
                    "警告", 
                    "至少需要设置一个停止命令或发送命令！"
                )
                return
            
            # 保存设置
            self.config_manager.set("voice.stop_commands", stop_commands)
            self.config_manager.set("voice.send_commands", send_commands)
            
            # 显示成功消息
            QMessageBox.information(
                self, 
                "成功", 
                "语音命令设置已保存！\n下次录音时生效。"
            )
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                "错误", 
                f"保存设置时出错：{str(e)}"
            )
    
    def reset_to_defaults(self):
        """重置为默认值"""
        reply = QMessageBox.question(
            self,
            "确认重置",
            "确定要重置为默认的语音命令吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 默认停止命令
            default_stop_commands = [
                "我说完了", "说完了", "结束", "停止录音", "停止",
                "finish", "done", "stop", "end"
            ]
            
            # 默认发送命令
            default_send_commands = [
                "开工吧", "发送", "提交", "执行", "开始干活", "开始工作",
                "send", "submit", "go", "execute", "let's go"
            ]
            
            self.stop_commands_edit.setPlainText("\n".join(default_stop_commands))
            self.send_commands_edit.setPlainText("\n".join(default_send_commands))
    
    def get_stop_commands(self) -> List[str]:
        """获取停止命令列表"""
        text = self.stop_commands_edit.toPlainText().strip()
        return [cmd.strip() for cmd in text.split('\n') if cmd.strip()] if text else []
    
    def get_send_commands(self) -> List[str]:
        """获取发送命令列表"""
        text = self.send_commands_edit.toPlainText().strip()
        return [cmd.strip() for cmd in text.split('\n') if cmd.strip()] if text else []


def main():
    """测试函数"""
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    config_manager = ConfigManager()
    dialog = VoiceSettingsDialog(config_manager)
    dialog.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 
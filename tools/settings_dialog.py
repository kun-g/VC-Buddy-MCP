#!/usr/bin/env python3
"""
设置对话框

用于配置OpenAI API Key等设置项
"""

import sys
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QFormLayout, QGroupBox,
                               QMessageBox, QTextEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from buddy.ui.config import ConfigManager


class SettingsDialog(QDialog):
    """设置对话框"""
    
    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("设置")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("VC-Buddy 设置")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # OpenAI 设置组
        openai_group = QGroupBox("OpenAI 配置")
        openai_layout = QFormLayout(openai_group)
        
        # API Key 输入
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("请输入您的 OpenAI API Key")
        openai_layout.addRow("API Key:", self.api_key_input)
        
        # API URL 输入
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("https://api.openai.com/v1")
        openai_layout.addRow("API URL:", self.api_url_input)
        
        # URL说明
        url_note = QLabel("留空使用默认地址，或输入自定义API端点（如代理服务器地址）")
        url_note.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        url_note.setWordWrap(True)
        openai_layout.addRow("", url_note)
        
        # 显示/隐藏 API Key 的按钮
        show_hide_layout = QHBoxLayout()
        self.show_api_key_btn = QPushButton("显示")
        self.show_api_key_btn.setFixedWidth(60)
        self.show_api_key_btn.clicked.connect(self.toggle_api_key_visibility)
        show_hide_layout.addWidget(self.show_api_key_btn)
        show_hide_layout.addStretch()
        openai_layout.addRow("", show_hide_layout)
        
        # API Key 说明
        api_key_info = QTextEdit()
        api_key_info.setReadOnly(True)
        api_key_info.setMaximumHeight(120)
        api_key_info.setPlainText(
            "获取 API Key 的步骤：\n"
            "1. 访问 https://platform.openai.com/api-keys\n"
            "2. 登录您的 OpenAI 账户\n"
            "3. 点击 'Create new secret key' 创建新的密钥\n"
            "4. 复制生成的密钥并粘贴到上方输入框中\n\n"
            "API URL 配置：\n"
            "• 默认：https://api.openai.com/v1 （官方API）\n"
            "• 可配置代理服务器或第三方兼容服务的URL"
        )
        api_key_info.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                color: #6c757d;
                font-size: 12px;
                padding: 8px;
            }
        """)
        openai_layout.addRow("说明:", api_key_info)
        
        main_layout.addWidget(openai_group)
        
        # 当前状态显示
        status_group = QGroupBox("当前状态")
        status_layout = QFormLayout(status_group)
        
        self.status_label = QLabel()
        self.update_status_display()
        status_layout.addRow("API Key 状态:", self.status_label)
        
        main_layout.addWidget(status_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 测试连接按钮
        self.test_btn = QPushButton("测试连接")
        self.test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(self.test_btn)
        
        # 保存按钮
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setDefault(True)
        button_layout.addWidget(self.save_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        main_layout.addLayout(button_layout)
        
        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                padding: 8px 16px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
            QPushButton[default="true"] {
                background-color: #007bff;
                color: white;
                border-color: #007bff;
            }
            QPushButton[default="true"]:hover {
                background-color: #0056b3;
            }
        """)
    
    def load_settings(self):
        """加载当前设置"""
        api_key = self.config_manager.openai_api_key
        if api_key:
            self.api_key_input.setText(api_key)
        
        api_url = self.config_manager.openai_api_url
        # 如果是默认URL，显示为空（让用户看到placeholder）
        if api_url and api_url != "https://api.openai.com/v1":
            self.api_url_input.setText(api_url)
        
        self.update_status_display()
    
    def update_status_display(self):
        """更新状态显示"""
        if self.config_manager.has_openai_api_key():
            self.status_label.setText("✅ 已配置")
            self.status_label.setStyleSheet("color: #28a745;")
        else:
            self.status_label.setText("❌ 未配置")
            self.status_label.setStyleSheet("color: #dc3545;")
    
    def toggle_api_key_visibility(self):
        """切换API Key的显示/隐藏"""
        if self.api_key_input.echoMode() == QLineEdit.Password:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.show_api_key_btn.setText("隐藏")
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.show_api_key_btn.setText("显示")
    
    def test_connection(self):
        """测试API Key连接"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "测试失败", "请先输入 API Key")
            return
        
        api_url = self.api_url_input.text().strip()
        if not api_url:
            api_url = "https://api.openai.com/v1"  # 使用默认URL
        
        # 显示测试中的状态
        self.test_btn.setText("测试中...")
        self.test_btn.setEnabled(False)
        
        try:
            import openai
            
            # 验证URL格式
            if not api_url.startswith(('http://', 'https://')):
                raise ValueError("API URL 必须以 http:// 或 https:// 开头")
            
            # 根据URL创建客户端
            try:
                if api_url == "https://api.openai.com/v1":
                    client = openai.OpenAI(api_key=api_key)
                else:
                    # 确保URL格式正确
                    if not api_url.endswith('/v1'):
                        if not api_url.endswith('/'):
                            api_url += '/v1'
                        else:
                            api_url += 'v1'
                    client = openai.OpenAI(api_key=api_key, base_url=api_url)
            except Exception as client_error:
                raise Exception(f"创建客户端失败: {str(client_error)}")
            
            # 简单的测试请求
            try:
                response = client.models.list()
                model_count = len(response.data) if hasattr(response, 'data') else 0
            except Exception as api_error:
                # 如果模型列表失败，尝试其他简单请求
                try:
                    # 尝试一个更简单的请求
                    client.completions.create(
                        model="gpt-3.5-turbo-instruct",
                        prompt="test",
                        max_tokens=1
                    )
                    model_count = "未知"
                except:
                    raise api_error
            
            # 测试成功
            QMessageBox.information(self, "测试成功", 
                                   f"API 连接成功！\n"
                                   f"API URL: {api_url}\n"
                                   f"可用模型: {model_count} 个")
            
        except Exception as e:
            error_msg = str(e)
            if "Incorrect API key" in error_msg or "invalid_api_key" in error_msg:
                QMessageBox.critical(self, "测试失败", "API Key 无效，请检查后重试。")
            elif "quota" in error_msg.lower() or "rate_limit" in error_msg.lower():
                QMessageBox.warning(self, "测试失败", "API Key 有效，但配额不足或请求频率过高。")
            elif "Connection" in error_msg or "timeout" in error_msg.lower() or "网络" in error_msg:
                QMessageBox.critical(self, "测试失败", 
                                   f"网络连接失败，请检查：\n"
                                   f"1. API URL 是否正确: {api_url}\n"
                                   f"2. 网络连接是否正常\n"
                                   f"3. 防火墙或代理设置\n\n"
                                   f"错误详情：{error_msg}")
            elif "创建客户端失败" in error_msg:
                QMessageBox.critical(self, "测试失败", 
                                   f"客户端配置错误：\n{error_msg}\n\n"
                                   f"请检查 API URL 格式是否正确。")
            else:
                QMessageBox.critical(self, "测试失败", 
                                   f"连接失败：{error_msg}\n\n"
                                   f"请检查API配置是否正确。")
        
        finally:
            # 恢复按钮状态
            self.test_btn.setText("测试连接")
            self.test_btn.setEnabled(True)
    
    def save_settings(self):
        """保存设置"""
        api_key = self.api_key_input.text().strip()
        api_url = self.api_url_input.text().strip()
        
        # 如果URL为空，使用默认值
        if not api_url:
            api_url = "https://api.openai.com/v1"
        
        # 保存API配置
        self.config_manager.set_openai_api_key(api_key)
        self.config_manager.set_openai_api_url(api_url)
        
        try:
            # 保存到配置文件
            self.config_manager.save_config()
            
            # 显示成功消息
            if api_key:
                msg = "设置已保存！\n\n"
                msg += f"API Key: 已配置\n"
                msg += f"API URL: {api_url}"
                QMessageBox.information(self, "保存成功", msg)
            else:
                QMessageBox.information(self, "保存成功", "设置已保存，API Key 已清除。")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存设置时出错：{str(e)}") 
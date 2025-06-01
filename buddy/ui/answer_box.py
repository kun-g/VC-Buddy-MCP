import sys
import json
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QPushButton, QDialog, QLabel, QVBoxLayout, QTextEdit
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QKeySequence, QShortcut

# 处理相对导入问题
try:
    from .config import config_manager
except ImportError:
    # 如果作为脚本直接运行，需要添加路径
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    from config import config_manager

# --- 设置工具类 ---
class SettingsManager:
    """QSettings的封装管理类"""
    
    @staticmethod
    def get_settings():
        """获取QSettings实例"""
        return QSettings(
            config_manager.organization_name, 
            config_manager.application_name
        )
    
    @staticmethod
    def save_window_geometry(widget):
        """保存窗口几何信息"""
        if config_manager.get("ui.window.remember_position", True):
            settings = SettingsManager.get_settings()
            settings.setValue("pos", widget.pos())
            settings.setValue("size", widget.size())
    
    @staticmethod
    def restore_window_geometry(widget):
        """恢复窗口几何信息"""
        if not config_manager.get("ui.window.remember_position", True):
            return False
            
        settings = SettingsManager.get_settings()
        pos = settings.value("pos", None)
        size = settings.value("size", None)
        
        if pos and size:
            widget.move(pos)
            widget.resize(size)
            return True
        return False

# --- 主处理逻辑 ---
class AnswerBox(QDialog):
    def __init__(self, app=None):
        super().__init__()
        self.app = app or QApplication.instance() or QApplication(sys.argv)
        self.setWindowTitle("Answer Box")
        
        # 设置窗口置顶
        if config_manager.get("ui.window.stay_on_top", True):
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 使用配置文件中的默认尺寸
        default_width = config_manager.get("ui.window.default_width", 300)
        default_height = config_manager.get("ui.window.default_height", 200)
        self.setGeometry(100, 100, default_width, default_height)
        
        self._restore_geometry_or_center()

        # 读取输入数据
        summary = ""
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            summary += line
        summary = summary.strip()
        data = json.loads(summary)
        
        # 解析输入数据
        self.summary_text = data.get("summary", "")
        self.project_directory = data.get("project_directory", None)
        
        # 更新窗口标题以显示项目信息
        if self.project_directory:
            project_name = os.path.basename(self.project_directory)
            self.setWindowTitle(f"Answer Box - {project_name}")
        
        self.label = QLabel(self.summary_text)
        self.label.show()

        self.input = QTextEdit()
        self.input.show()

        self.button = QPushButton("Send (Ctrl+Enter)")
        self.button.clicked.connect(self.respond)
        self.button.show()

        # 设置 Ctrl+Enter 快捷键
        self.send_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.send_shortcut.activated.connect(self.respond)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.show()

    def respond(self):
        response = {
            "result": f"{self.input.toPlainText()}"
        }
        # 如果有项目目录，也包含在响应中
        if self.project_directory:
            response["project_directory"] = self.project_directory
            
        sys.stdout.write(json.dumps(response, ensure_ascii=False))
        sys.stdout.flush()
        self.app.quit()

    def _restore_geometry_or_center(self):
        if not SettingsManager.restore_window_geometry(self):
            # 如果无法恢复几何信息，则居中显示
            screen = QApplication.primaryScreen()
            rect = screen.availableGeometry()
            self.move(
                rect.center() - self.rect().center()
            )

    def closeEvent(self, event):
        SettingsManager.save_window_geometry(self)
        return super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    answer_box = AnswerBox(app)
    answer_box.show()
    app.exec()

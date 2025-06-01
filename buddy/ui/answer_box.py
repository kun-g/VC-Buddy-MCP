import sys
import json
import os
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QPushButton, QDialog, QLabel, 
                               QVBoxLayout, QTextEdit, QTreeWidget, QTreeWidgetItem,
                               QHBoxLayout, QSplitter, QTextBrowser)
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QKeySequence, QShortcut

# 处理相对导入问题
try:
    from .config import config_manager, get_project_config_manager
    from .todo_parser import TodoParser, TodoItem
except ImportError:
    # 如果作为脚本直接运行，需要添加路径
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    from config import config_manager, get_project_config_manager
    from todo_parser import TodoParser, TodoItem

# --- 设置工具类 ---
class SettingsManager:
    """QSettings的封装管理类"""
    
    def __init__(self, config_mgr):
        self.config_mgr = config_mgr
    
    def get_settings(self):
        """获取QSettings实例"""
        return QSettings(
            self.config_mgr.organization_name, 
            self.config_mgr.application_name
        )
    
    def save_window_geometry(self, widget):
        """保存窗口几何信息"""
        if self.config_mgr.get("ui.window.remember_position", True):
            settings = self.get_settings()
            settings.setValue("pos", widget.pos())
            settings.setValue("size", widget.size())
    
    def restore_window_geometry(self, widget):
        """恢复窗口几何信息"""
        if not self.config_mgr.get("ui.window.remember_position", True):
            return False
            
        settings = self.get_settings()
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
        
        # 根据项目目录获取配置管理器
        if self.project_directory:
            self.config_mgr = get_project_config_manager(self.project_directory)
            project_name = os.path.basename(self.project_directory)
            self.setWindowTitle(f"Answer Box - {project_name}")
        else:
            self.config_mgr = config_manager
        
        # 创建设置管理器
        self.settings_mgr = SettingsManager(self.config_mgr)
        
        # 设置窗口置顶
        if self.config_mgr.get("ui.window.stay_on_top", True):
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 使用配置文件中的默认尺寸
        default_width = self.config_mgr.get("ui.window.default_width", 300)
        default_height = self.config_mgr.get("ui.window.default_height", 200)
        self.setGeometry(100, 100, default_width, default_height)
        
        self._restore_geometry_or_center()
        
        # 加载TODO数据
        self.todo_parser = TodoParser()
        self.todo_items = []
        if self.project_directory:
            self.todo_items = self.todo_parser.load_project_todos(self.project_directory)
        
        self._setup_ui()
        self.show()

    def _setup_ui(self):
        """设置用户界面"""
        self.layout = QVBoxLayout()
        
        # 摘要显示区域 - 使用QTextBrowser美化显示
        self.summary_display = QTextBrowser()
        self.summary_display.setMaximumHeight(100)
        self.summary_display.setStyleSheet("""
            QTextBrowser {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        
        # 设置摘要内容
        if self.summary_text:
            # 将纯文本转换为HTML格式
            html_content = f"""
            <div style="color: #333; line-height: 1.4;">
                <strong style="color: #2c5aa0;">📋 任务摘要:</strong><br>
                {self.summary_text.replace(chr(10), '<br>')}
            </div>
            """
            self.summary_display.setHtml(html_content)
        else:
            self.summary_display.setHtml("<i style='color: #888;'>无任务摘要</i>")
        
        self.layout.addWidget(self.summary_display)
        
        # 如果有TODO项目，创建分割器布局
        if self.todo_items:
            splitter = QSplitter(Qt.Horizontal)
            
            # 左侧：TODO树状视图
            self.todo_tree = QTreeWidget()
            self.todo_tree.setHeaderLabel("📝 TODO 任务")
            self.todo_tree.setStyleSheet("""
                QTreeWidget {
                    border: 1px solid #d0d0d0;
                    border-radius: 5px;
                    background-color: white;
                }
                QTreeWidget::item {
                    padding: 4px;
                    border-bottom: 1px solid #f0f0f0;
                }
                QTreeWidget::item:selected {
                    background-color: #e3f2fd;
                    color: #1976d2;
                }
                QTreeWidget::item:hover {
                    background-color: #f5f5f5;
                }
            """)
            self.todo_tree.itemClicked.connect(self._on_todo_item_clicked)
            self.todo_tree.itemDoubleClicked.connect(self._on_todo_item_double_clicked)
            self._populate_todo_tree()
            splitter.addWidget(self.todo_tree)
            
            # 右侧：详情和输入区域
            right_widget = self._create_right_panel()
            splitter.addWidget(right_widget)
            
            # 设置分割器比例
            splitter.setSizes([200, 300])
            self.layout.addWidget(splitter)
        else:
            # 没有TODO时，只显示输入区域
            self.input = QTextEdit()
            self.input.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #d0d0d0;
                    border-radius: 5px;
                    padding: 8px;
                    font-size: 12px;
                }
            """)
            self.layout.addWidget(self.input)
        
        # 发送按钮
        self.button = QPushButton("📤 Send (Ctrl+Enter)")
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        self.button.clicked.connect(self.respond)
        self.layout.addWidget(self.button)
        
        # 设置 Ctrl+Enter 快捷键
        self.send_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.send_shortcut.activated.connect(self.respond)
        
        self.setLayout(self.layout)

    def _create_right_panel(self):
        """创建右侧面板"""
        from PySide6.QtWidgets import QWidget
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        # TODO详情显示
        detail_label = QLabel("📄 任务详情:")
        detail_label.setStyleSheet("font-weight: bold; color: #333; margin-bottom: 4px;")
        layout.addWidget(detail_label)
        
        self.todo_detail = QTextBrowser()
        self.todo_detail.setMaximumHeight(150)
        self.todo_detail.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                background-color: #fafafa;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.todo_detail)
        
        # 输入区域
        input_label = QLabel("💬 反馈内容:")
        input_label.setStyleSheet("font-weight: bold; color: #333; margin-top: 8px; margin-bottom: 4px;")
        layout.addWidget(input_label)
        
        self.input = QTextEdit()
        self.input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }
            QTextEdit:focus {
                border: 2px solid #2196f3;
            }
        """)
        layout.addWidget(self.input)
        
        widget.setLayout(layout)
        return widget

    def _populate_todo_tree(self):
        """填充TODO树状视图"""
        for todo_item in self.todo_items:
            tree_item = self._create_tree_item(todo_item)
            self.todo_tree.addTopLevelItem(tree_item)
        
        # 展开所有项目
        self.todo_tree.expandAll()

    def _create_tree_item(self, todo_item: TodoItem) -> QTreeWidgetItem:
        """创建树状视图项目"""
        tree_item = QTreeWidgetItem([todo_item.title])
        tree_item.setData(0, Qt.UserRole, todo_item)
        
        # 添加子项目
        for child in todo_item.children:
            child_item = self._create_tree_item(child)
            tree_item.addChild(child_item)
        
        return tree_item

    def _on_todo_item_clicked(self, item: QTreeWidgetItem, column: int):
        """处理TODO项目点击事件"""
        todo_item = item.data(0, Qt.UserRole)
        if todo_item and hasattr(self, 'todo_detail'):
            # 显示任务详情
            detail_text = f"<h3>{todo_item.title}</h3>"
            if todo_item.content:
                detail_text += f"<p>{todo_item.content.replace(chr(10), '<br>')}</p>"
            else:
                detail_text += "<p><i>无详细说明</i></p>"
            
            self.todo_detail.setHtml(detail_text)

    def _on_todo_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """处理TODO项目双击事件 - 插入说明到输入框"""
        todo_item = item.data(0, Qt.UserRole)
        if todo_item and hasattr(self, 'input'):
            # 获取当前输入框内容
            current_text = self.input.toPlainText()
            
            # 准备要插入的内容
            insert_text = ""
            if todo_item.content:
                insert_text = todo_item.content
            else:
                insert_text = f"关于任务: {todo_item.title}"
            
            # 如果输入框不为空，添加换行
            if current_text.strip():
                insert_text = "\n\n" + insert_text
            
            # 插入内容到输入框
            self.input.append(insert_text)
            
            # 将焦点设置到输入框
            self.input.setFocus()

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
        if not self.settings_mgr.restore_window_geometry(self):
            # 如果无法恢复几何信息，则居中显示
            screen = QApplication.primaryScreen()
            rect = screen.availableGeometry()
            self.move(
                rect.center() - self.rect().center()
            )

    def closeEvent(self, event):
        self.settings_mgr.save_window_geometry(self)
        return super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    answer_box = AnswerBox(app)
    answer_box.show()
    app.exec()

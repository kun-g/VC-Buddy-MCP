import sys
import json
import os
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QObject, Signal, Slot, Property, QAbstractListModel, QModelIndex, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

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


class TodoListModel(QAbstractListModel):
    """TODO项目的列表模型"""
    
    TodoItemRole = Qt.UserRole + 1
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._todos: List[TodoItem] = []
        self._flat_todos: List[TodoItem] = []
    
    def roleNames(self):
        return {
            self.TodoItemRole: b"todoItem"
        }
    
    def rowCount(self, parent=QModelIndex()):
        return len(self._flat_todos)
    
    def data(self, index, role):
        if not index.isValid() or index.row() >= len(self._flat_todos):
            return None
        
        if role == self.TodoItemRole:
            todo_item = self._flat_todos[index.row()]
            return todo_item.to_dict()
        
        return None
    
    def setTodos(self, todos: List[TodoItem]):
        """设置TODO列表"""
        self.beginResetModel()
        self._todos = todos
        self._flat_todos = self._flatten_todos(todos)
        self.endResetModel()
    
    def _flatten_todos(self, todos: List[TodoItem]) -> List[TodoItem]:
        """将嵌套的TODO列表扁平化"""
        result = []
        for todo in todos:
            result.append(todo)
            result.extend(self._flatten_todos(todo.children))
        return result
    
    def getTodoItem(self, index: int) -> Optional[TodoItem]:
        """获取指定索引的TODO项目"""
        if 0 <= index < len(self._flat_todos):
            return self._flat_todos[index]
        return None


class AnswerBoxBackend(QObject):
    """QML后端逻辑类"""
    
    # 信号定义
    todoContentInserted = Signal(str, arguments=['content'])
    responseReady = Signal(str, arguments=['response'])
    selectedTodoDetailChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 读取输入数据
        summary = ""
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            summary += line
        summary = summary.strip()
        
        if not summary:
            # 如果没有输入，使用默认测试数据
            data = {
                "summary": "QML测试模式",
                "project_directory": os.getcwd()
            }
        else:
            data = json.loads(summary)
        
        # 解析输入数据
        self._summary_text = data.get("summary", "")
        self._project_directory = data.get("project_directory", None)
        
        # 根据项目目录获取配置管理器
        if self._project_directory:
            self._config_mgr = get_project_config_manager(self._project_directory)
            project_name = os.path.basename(self._project_directory)
            self._window_title = f"Answer Box - {project_name}"
        else:
            self._config_mgr = config_manager
            self._window_title = "Answer Box"
        
        # 加载TODO数据
        self._todo_parser = TodoParser()
        self._todo_items = []
        if self._project_directory:
            self._todo_items = self._todo_parser.load_project_todos(self._project_directory)
        
        # 创建TODO模型
        self._todo_model = TodoListModel(self)
        self._todo_model.setTodos(self._todo_items)
        
        # 选中的TODO详情
        self._selected_todo_detail = "选择一个任务查看详情"
        
        # 调试信息
        print(f"DEBUG: 加载了 {len(self._todo_items)} 个TODO项目", file=sys.stderr)
        print(f"DEBUG: 项目目录: {self._project_directory}", file=sys.stderr)
    
    # 属性定义
    @Property(str, constant=True)
    def summaryText(self):
        return self._summary_text
    
    @Property(str, constant=True)
    def windowTitle(self):
        return self._window_title
    
    @Property(int, constant=True)
    def defaultWidth(self):
        return self._config_mgr.get("ui.window.default_width", 400)
    
    @Property(int, constant=True)
    def defaultHeight(self):
        return self._config_mgr.get("ui.window.default_height", 600)
    
    @Property(bool, constant=True)
    def stayOnTop(self):
        return self._config_mgr.get("ui.window.stay_on_top", True)
    
    @Property(bool, constant=True)
    def hasTodos(self):
        return len(self._todo_items) > 0
    
    @Property(QObject, constant=True)
    def todoModel(self):
        return self._todo_model
    
    @Property(str, notify=selectedTodoDetailChanged)
    def selectedTodoDetail(self):
        return self._selected_todo_detail
    
    # 槽函数定义
    @Slot(int)
    def selectTodoItem(self, index: int):
        """选择TODO项目"""
        print(f"DEBUG: 选择TODO项目 {index}", file=sys.stderr)
        todo_item = self._todo_model.getTodoItem(index)
        if todo_item:
            detail_text = f"<h3>{todo_item.display_title}</h3>"
            
            # 显示属性
            if todo_item.attributes:
                detail_text += "<p><strong>属性:</strong></p><ul>"
                for key, value in todo_item.attributes.items():
                    detail_text += f"<li><strong>{key}:</strong> {value}</li>"
                detail_text += "</ul>"
            
            # 显示内容
            if todo_item.content:
                detail_text += f"<p><strong>详情:</strong></p><p>{todo_item.content.replace(chr(10), '<br>')}</p>"
            else:
                detail_text += "<p><i>无详细说明</i></p>"
            
            self._selected_todo_detail = detail_text
            self.selectedTodoDetailChanged.emit()
            print(f"DEBUG: 更新TODO详情", file=sys.stderr)
    
    @Slot(int)
    def insertTodoContent(self, index: int):
        """插入TODO内容到输入框"""
        print(f"DEBUG: 插入TODO内容 {index}", file=sys.stderr)
        todo_item = self._todo_model.getTodoItem(index)
        if todo_item:
            # 准备要插入的内容
            if todo_item.content:
                insert_text = todo_item.content
            else:
                insert_text = todo_item.title
            
            # 发送信号插入内容
            self.todoContentInserted.emit(insert_text)
            print(f"DEBUG: 发送插入信号: {insert_text[:50]}...", file=sys.stderr)
    
    @Slot(int)
    def markTodoDone(self, index: int):
        """标记TODO任务为完成"""
        print(f"DEBUG: 标记TODO完成 {index}", file=sys.stderr)
        todo_item = self._todo_model.getTodoItem(index)
        if todo_item:
            todo_item.mark_as_done()
            self._save_todos_to_file()
            # 刷新模型以更新显示
            self._todo_model.setTodos(self._todo_items)
    
    @Slot(int)
    def markTodoUndone(self, index: int):
        """标记TODO任务为未完成"""
        print(f"DEBUG: 标记TODO未完成 {index}", file=sys.stderr)
        todo_item = self._todo_model.getTodoItem(index)
        if todo_item:
            todo_item.mark_as_undone()
            self._save_todos_to_file()
            # 刷新模型以更新显示
            self._todo_model.setTodos(self._todo_items)
    
    def _save_todos_to_file(self):
        """保存TODO列表到文件"""
        if not self._project_directory or not self._todo_items:
            return
        
        try:
            # 查找TODO文件
            todo_file = self._todo_parser.find_todo_file(self._project_directory)
            
            if todo_file:
                # 保存更新后的TODO列表
                success = self._todo_parser.save_todos_to_file(self._todo_items, todo_file)
                if not success:
                    print("WARNING: 无法保存TODO文件，请检查文件权限。", file=sys.stderr)
            else:
                print("WARNING: 在项目目录中未找到TODO.md文件。", file=sys.stderr)
        except Exception as e:
            print(f"ERROR: 保存TODO文件时发生错误：{str(e)}", file=sys.stderr)
    
    @Slot(str)
    def sendResponse(self, feedback_text: str):
        """发送响应"""
        print(f"DEBUG: 发送响应: {feedback_text[:50]}...", file=sys.stderr)
        response = {
            "result": feedback_text
        }
        
        # 输出响应并退出
        sys.stdout.write(json.dumps(response, ensure_ascii=False))
        sys.stdout.flush()
        print(f"DEBUG: 响应已发送，准备退出", file=sys.stderr)
        QGuiApplication.instance().quit()


class AnswerBoxQML:
    """QML版本的AnswerBox应用"""
    
    def __init__(self):
        self.app = QGuiApplication(sys.argv)
        self.engine = QQmlApplicationEngine()
        
        # 注册自定义类型
        qmlRegisterType(AnswerBoxBackend, "AnswerBoxBackend", 1, 0, "AnswerBoxBackend")
        
        # 创建后端对象
        self.backend = AnswerBoxBackend()
        
        # 设置QML上下文属性
        self.engine.rootContext().setContextProperty("backend", self.backend)
        
        # 添加QML模块路径
        qml_dir = Path(__file__).parent / "qml"
        self.engine.addImportPath(str(qml_dir.parent))
        
        # 加载QML文件
        qml_file = qml_dir / "Main.qml"
        self.engine.load(qml_file)
        
        # 检查是否加载成功
        if not self.engine.rootObjects():
            print("ERROR: 无法加载QML文件", file=sys.stderr)
            sys.exit(-1)
    
    def run(self):
        """运行应用"""
        return self.app.exec()


def main():
    """主函数"""
    answer_box = AnswerBoxQML()
    return answer_box.run()


if __name__ == "__main__":
    sys.exit(main()) 
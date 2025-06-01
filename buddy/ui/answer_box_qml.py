import sys
import json
import os
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QObject, Signal, Slot, Property, QAbstractListModel, QModelIndex, Qt, QSettings
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

# 处理相对导入问题
try:
    from .config import config_manager, get_project_config_manager
    from .todo_parser import TodoParser, TodoItem
    from .style_manager import StyleManager, load_default_styles
except ImportError:
    # 如果作为脚本直接运行，需要添加路径
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    from config import config_manager, get_project_config_manager
    from todo_parser import TodoParser, TodoItem
    from style_manager import StyleManager, load_default_styles


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
    windowGeometryChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 首先初始化默认值
        self._summary_text = "等待数据输入..."
        self._project_directory = None
        
        # 尝试读取输入数据（非阻塞）
        data = None
        try:
            # 检查是否有标准输入数据
            if not sys.stdin.isatty():  # 如果有管道输入
                input_data = sys.stdin.read().strip()
                if input_data:
                    data = json.loads(input_data)
                    print(f"DEBUG: 读取到输入数据: {data}", file=sys.stderr)
                else:
                    print("DEBUG: 标准输入为空", file=sys.stderr)
            else:
                print("DEBUG: 没有管道输入，使用测试模式", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON解析错误: {e}", file=sys.stderr)
        except Exception as e:
            print(f"DEBUG: 读取输入时出错: {e}", file=sys.stderr)
        
        # 如果没有输入数据，使用测试数据
        if not data:
            current_dir = os.getcwd()
            data = {
                "summary": f"QML测试模式 - 当前目录: {current_dir}",
                "project_directory": current_dir
            }
            print(f"DEBUG: 使用测试数据: {data}", file=sys.stderr)
        
        # 解析输入数据
        self._summary_text = data.get("summary", "无任务摘要")
        self._project_directory = data.get("project_directory", None)
        
        print(f"DEBUG: 摘要文本: {self._summary_text[:100]}...", file=sys.stderr)
        print(f"DEBUG: 项目目录: {self._project_directory}", file=sys.stderr)
        
        # 根据项目目录获取配置管理器
        if self._project_directory:
            self._config_mgr = get_project_config_manager(self._project_directory)
            project_name = os.path.basename(self._project_directory)
            self._window_title = f"Answer Box - {project_name}"
        else:
            self._config_mgr = config_manager
            self._window_title = "Answer Box"
        
        # 创建设置管理器（用于保存窗口几何信息）
        self._settings = QSettings(
            self._config_mgr.organization_name,
            self._config_mgr.application_name
        )
        
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
        self._selected_todo_title = None
        
        # 调试信息
        print(f"DEBUG: 加载了 {len(self._todo_items)} 个TODO项目", file=sys.stderr)
        print(f"DEBUG: 窗口标题: {self._window_title}", file=sys.stderr)
    
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
    
    @Property(str, notify=selectedTodoDetailChanged)
    def selectedTodoTitle(self):
        return self._selected_todo_title
    
    @Property(bool, constant=True)
    def rememberPosition(self):
        """是否记住窗口位置"""
        return self._config_mgr.get("ui.window.remember_position", True)
    
    @Property(int, notify=windowGeometryChanged)
    def savedX(self):
        """保存的窗口X坐标"""
        if not self.rememberPosition:
            return -1
        return self._settings.value("window/x", -1, type=int)
    
    @Property(int, notify=windowGeometryChanged)
    def savedY(self):
        """保存的窗口Y坐标"""
        if not self.rememberPosition:
            return -1
        return self._settings.value("window/y", -1, type=int)
    
    @Property(int, notify=windowGeometryChanged)
    def savedWidth(self):
        """保存的窗口宽度"""
        if not self.rememberPosition:
            return self.defaultWidth
        return self._settings.value("window/width", self.defaultWidth, type=int)
    
    @Property(int, notify=windowGeometryChanged)
    def savedHeight(self):
        """保存的窗口高度"""
        if not self.rememberPosition:
            return self.defaultHeight
        return self._settings.value("window/height", self.defaultHeight, type=int)
    
    # 槽函数定义
    @Slot(int)
    def selectTodoItem(self, index: int):
        """选择TODO项目"""
        todo_item = self._todo_model.getTodoItem(index)
        if todo_item:
            # 设置选中的标题
            self._selected_todo_title = todo_item.display_title
            
            # 详情框只显示内容，不包含标题
            if todo_item.content:
                detail_text = todo_item.content.replace(chr(10), '<br>')
            else:
                detail_text = "<i>无详细说明</i>"
            
            self._selected_todo_detail = detail_text
            self.selectedTodoDetailChanged.emit()
        else:
            # 没有选中任何项目
            self._selected_todo_title = None
            self._selected_todo_detail = "选择一个任务查看详情"
            self.selectedTodoDetailChanged.emit()
    
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
        print(f"DEBUG: 准备发送响应: {feedback_text[:100]}...", file=sys.stderr)
        
        try:
            response = {
                "result": feedback_text
            }
            
            # 输出到标准输出
            output = json.dumps(response, ensure_ascii=False)
            print(output)  # 使用 print 而不是 sys.stdout.write
            sys.stdout.flush()
            
            print(f"DEBUG: 响应已发送到标准输出", file=sys.stderr)
            
            # 延迟退出，确保输出完成
            QGuiApplication.instance().quit()
            
        except Exception as e:
            print(f"ERROR: 发送响应时出错: {e}", file=sys.stderr)
            QGuiApplication.instance().quit()
    
    @Slot(int, int, int, int)
    def saveWindowGeometry(self, x: int, y: int, width: int, height: int):
        """保存窗口几何信息"""
        if not self.rememberPosition:
            return
        
        print(f"DEBUG: 保存窗口几何信息: x={x}, y={y}, width={width}, height={height}", file=sys.stderr)
        
        self._settings.setValue("window/x", x)
        self._settings.setValue("window/y", y)
        self._settings.setValue("window/width", width)
        self._settings.setValue("window/height", height)
        self._settings.sync()
        
        self.windowGeometryChanged.emit()
    
    @Slot(result=bool)
    def hasValidSavedGeometry(self):
        """检查是否有有效的保存几何信息"""
        if not self.rememberPosition:
            return False
        
        x = self.savedX
        y = self.savedY
        width = self.savedWidth
        height = self.savedHeight
        
        # 检查坐标是否有效（不为-1且在合理范围内）
        return (x >= 0 and y >= 0 and 
                width >= 200 and height >= 150 and
                width <= 3000 and height <= 2000)


class AnswerBoxQML:
    """QML版本的AnswerBox应用"""
    
    def __init__(self):
        # 设置 QML 样式，避免样式警告
        import os
        os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
        
        self.app = QGuiApplication(sys.argv)
        
        # 初始化样式管理器
        self.style_manager = StyleManager()
        
        # 加载默认 QSS 样式
        print("DEBUG: 加载 QSS 样式", file=sys.stderr)
        style_loaded = load_default_styles()
        if style_loaded:
            print("DEBUG: QSS 样式加载成功", file=sys.stderr)
        else:
            print("WARNING: QSS 样式加载失败，使用默认样式", file=sys.stderr)
        
        self.engine = QQmlApplicationEngine()
        
        # 注册自定义类型
        qmlRegisterType(AnswerBoxBackend, "AnswerBoxBackend", 1, 0, "AnswerBoxBackend")
        qmlRegisterType(StyleManager, "StyleManager", 1, 0, "StyleManager")
        
        # 创建后端对象
        self.backend = AnswerBoxBackend()
        
        # 设置QML上下文属性
        self.engine.rootContext().setContextProperty("backend", self.backend)
        self.engine.rootContext().setContextProperty("styleManager", self.style_manager)
        
        # 添加QML模块路径
        qml_dir = Path(__file__).parent / "qml"
        print(f"DEBUG: QML 目录: {qml_dir}", file=sys.stderr)
        print(f"DEBUG: QML 目录是否存在: {qml_dir.exists()}", file=sys.stderr)
        
        # 添加模块搜索路径
        self.engine.addImportPath(str(qml_dir))
        self.engine.addImportPath(str(qml_dir.parent))
        
        # 检查 qmldir 文件
        qmldir_file = qml_dir / "qmldir"
        print(f"DEBUG: qmldir 文件: {qmldir_file}", file=sys.stderr)
        print(f"DEBUG: qmldir 是否存在: {qmldir_file.exists()}", file=sys.stderr)
        if qmldir_file.exists():
            with open(qmldir_file, 'r', encoding='utf-8') as f:
                qmldir_content = f.read()
            print(f"DEBUG: qmldir 内容:\n{qmldir_content}", file=sys.stderr)
        
        # 加载QML文件
        qml_file = qml_dir / "Main.qml"
        print(f"DEBUG: 加载QML文件: {qml_file}", file=sys.stderr)
        self.engine.load(qml_file)
        
        # 检查是否加载成功
        if not self.engine.rootObjects():
            print("ERROR: 无法加载QML文件", file=sys.stderr)
            sys.exit(-1)
        else:
            print("DEBUG: QML界面加载成功", file=sys.stderr)
    
    def run(self):
        """运行应用"""
        print("DEBUG: 启动GUI事件循环", file=sys.stderr)
        return self.app.exec()


def main():
    """主函数"""
    answer_box = AnswerBoxQML()
    return answer_box.run()


if __name__ == "__main__":
    sys.exit(main()) 
import sys
import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

from PySide6.QtCore import QObject, Signal, Slot, Property, QAbstractListModel, QModelIndex, Qt, QSettings, QTimer, QThread
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, qmlRegisterType

# 处理相对导入问题
try:
    from .config import config_manager, get_project_config_manager
    from .todo_parser import TodoParser, TodoItem
    from .style_manager import StyleManager, load_default_styles
    from .voice_recorder import VoiceRecorder
    from .streaming_voice_recorder import StreamingVoiceRecorder
    from ..core.analytics import get_analytics_manager, track_app_opened, track_button_clicked, track_todo_action, track_voice_action
except ImportError:
    # 如果作为脚本直接运行，需要添加路径
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir.parent))  # 添加buddy目录到路径
    from ui.config import config_manager, get_project_config_manager
    from ui.todo_parser import TodoParser, TodoItem
    from ui.style_manager import StyleManager, load_default_styles
    from ui.voice_recorder import VoiceRecorder
    from ui.streaming_voice_recorder import StreamingVoiceRecorder
    from core.analytics import get_analytics_manager, track_app_opened, track_button_clicked, track_todo_action, track_voice_action


class DeepSeekSummaryWorker(QThread):
    """DeepSeek总结工作线程"""
    
    # 信号定义
    summaryCompleted = Signal(str)  # 总结完成信号
    summaryError = Signal(str)      # 总结错误信号
    
    def __init__(self, content, project_directory, parent=None):
        super().__init__(parent)
        self.content = content
        self.project_directory = project_directory
    
    def run(self):
        """在子线程中执行DeepSeek总结"""
        try:
            # 导入DeepSeek客户端
            try:
                from ..core.deepseek_client import DeepSeekClient
                from ..core.prompt_manager import get_deepseek_prompt
                from .config import ConfigManager
            except ImportError:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from core.deepseek_client import DeepSeekClient
                from core.prompt_manager import get_deepseek_prompt
                from ui.config import ConfigManager
            
            # 获取配置
            config = ConfigManager(project_directory=self.project_directory)
            
            if not config.has_deepseek_api_key():
                error_msg = "DeepSeek API密钥未配置，请先配置API密钥"
                self.summaryError.emit(error_msg)
                return
            
            # 创建DeepSeek客户端
            client = DeepSeekClient(
                api_key=config.deepseek_api_key,
                base_url=config.deepseek_api_url
            )
            
            # 使用提示词管理器获取系统提示词
            system_prompt = get_deepseek_prompt()
            
            # 调用DeepSeek处理
            response = client.simple_chat(
                user_input=f"请总结以下内容：\n\n{self.content}",
                system_prompt=system_prompt,
                model=config.deepseek_model,
                temperature=config.deepseek_temperature
            )
            
            # 发送完成信号
            self.summaryCompleted.emit(response)
            
        except Exception as e:
            error_msg = f"DeepSeek处理失败: {str(e)}"
            print(error_msg, file=sys.stderr)
            self.summaryError.emit(error_msg)


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


class ConfigManagerProxy(QObject):
    """ConfigManager的QML代理类"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self._config_manager = config_manager
    
    @Slot(str, result='QVariant')
    @Slot(str, 'QVariant', result='QVariant')
    def get(self, key_path, default=None):
        """获取配置值"""
        return self._config_manager.get(key_path, default)
    
    @Slot(str, 'QVariant')
    def set(self, key_path, value):
        """设置配置值"""
        self._config_manager.set(key_path, value)
    
    @Slot()
    def save_config(self):
        """保存配置"""
        self._config_manager.save_config()
    
    @Slot(result=str)
    def getConfigFilePath(self):
        """获取配置文件路径"""
        return self._config_manager.config_file_path


class AnswerBoxBackend(QObject):
    """QML后端逻辑类"""
    
    # 信号定义
    todoContentInserted = Signal(str, arguments=['content'])
    responseReady = Signal(str, arguments=['response'])
    selectedTodoDetailChanged = Signal()
    windowGeometryChanged = Signal()
    voiceTranscriptionReady = Signal(str, arguments=['transcription'])
    voiceTranscriptionChunkReady = Signal(str, arguments=['chunk'])
    voiceRecordingStateChanged = Signal(bool, arguments=['isRecording'])
    voiceTranscriptionStateChanged = Signal(bool, arguments=['isTranscribing'])  # 新增：转写状态信号
    voiceErrorOccurred = Signal(str, arguments=['errorMessage'])
    voiceCommandDetected = Signal(str, str, arguments=['commandType', 'text'])
    voiceSettingsRequested = Signal('QVariant', arguments=['configManager'])  # 修复：使用QVariant而不是var
    settingsRequested = Signal('QVariant', arguments=['configManager'])  # 新增：主设置对话框信号
    deepseekSummaryReady = Signal(str, arguments=['summary'])  # 新增：DeepSeek总结完成信号
    deepseekSummaryStateChanged = Signal(bool, arguments=['isSummarizing'])  # 新增：DeepSeek总结状态信号
    deepseekSummaryError = Signal(str, arguments=['errorMessage'])  # 新增：DeepSeek总结错误信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 首先初始化默认值
        self._summary_text = "等待数据输入..."
        self._project_directory = None
        self._is_transcribing = False  # 新增：转写状态标志
        self._is_summarizing = False  # 新增：总结状态标志
        
        # 尝试读取输入数据（非阻塞）
        data = None
        input_data = ""
        try:
            # 检查是否有标准输入数据
            if not sys.stdin.isatty():  # 如果有管道输入
                # 尝试多种方式读取UTF-8编码的输入
                try:
                    if hasattr(sys.stdin, 'buffer'):
                        # 方法1：使用buffer以UTF-8编码读取
                        input_bytes = sys.stdin.buffer.read()
                        input_data = input_bytes.decode('utf-8').strip()
                    else:
                        # 方法2：直接读取
                        input_data = sys.stdin.read().strip()
                except UnicodeDecodeError:
                    # 方法3：尝试其他编码
                    try:
                        if hasattr(sys.stdin, 'buffer'):
                            input_bytes = sys.stdin.buffer.read()
                            # 尝试GBK编码（Windows中文系统）
                            input_data = input_bytes.decode('gbk').strip()
                        else:
                            input_data = sys.stdin.read().strip()
                    except UnicodeDecodeError:
                        # 方法4：忽略错误字符
                        if hasattr(sys.stdin, 'buffer'):
                            input_bytes = sys.stdin.buffer.read()
                            input_data = input_bytes.decode('utf-8', errors='ignore').strip()
                        else:
                            input_data = sys.stdin.read().strip()
                
                if input_data:
                    data = json.loads(input_data)
                    print(f"DEBUG: 成功读取输入数据: {len(input_data)} 字符", file=sys.stderr)
                else:
                    print("DEBUG: 标准输入为空", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(f"DEBUG: JSON解析错误: {e}", file=sys.stderr)
            print(f"DEBUG: 原始输入数据: {input_data[:100]}...", file=sys.stderr)
        except Exception as e:
            print(f"DEBUG: 读取输入时出错: {e}", file=sys.stderr)
        
        # 如果没有输入数据，使用测试数据
        if not data:
            current_dir = os.getcwd()
            data = {
                "summary": f"QML测试模式 - 当前目录: {current_dir}",
                "project_directory": current_dir
            }
        
        # 解析输入数据
        self._summary_text = data.get("summary", "无任务摘要")
        self._project_directory = data.get("project_directory", None)
        
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
        
        # 初始化传统录音器作为主要录音器
        self._voice_recorder = VoiceRecorder(config_manager=self._config_mgr)
        self._is_recording = False
        
        # DeepSeek总结工作线程引用
        self._deepseek_worker = None
        
        # 连接传统录音器信号
        self._voice_recorder.recording_started.connect(self._on_recording_started)
        self._voice_recorder.recording_stopped.connect(self._on_recording_stopped)
        self._voice_recorder.transcription_ready.connect(self._on_transcription_ready)
        self._voice_recorder.error_occurred.connect(self._on_voice_error)
        
        # 保留流式录音器用于高级功能（如需要时）
        self._streaming_voice_recorder = StreamingVoiceRecorder(config_manager=self._config_mgr)
        
        # 连接流式录音器信号（保留以支持语音设置功能）
        self._streaming_voice_recorder.recording_started.connect(self._on_streaming_recording_started)
        self._streaming_voice_recorder.recording_stopped.connect(self._on_streaming_recording_stopped)
        self._streaming_voice_recorder.transcription_chunk_ready.connect(self._on_transcription_chunk_ready)
        self._streaming_voice_recorder.final_transcription_ready.connect(self._on_final_transcription_ready)
        self._streaming_voice_recorder.error_occurred.connect(self._on_streaming_voice_error)
        self._streaming_voice_recorder.stop_command_detected.connect(self._on_stop_command_detected)
        self._streaming_voice_recorder.send_command_detected.connect(self._on_send_command_detected)
        
        # 初始化统计管理器
        self._analytics = get_analytics_manager()
        
        # 统计应用打开
        if self._project_directory:
            track_app_opened(source="project")
        else:
            track_app_opened(source="general")
        
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
    
    @Property(bool, notify=voiceRecordingStateChanged)
    def isRecording(self):
        """录音状态属性"""
        return self._is_recording
    
    @Property(bool, notify=voiceTranscriptionStateChanged)
    def isTranscribing(self):
        """获取转写状态"""
        return self._is_transcribing
    
    @Property(bool, notify=deepseekSummaryStateChanged)
    def isSummarizing(self):
        """获取DeepSeek总结状态"""
        return self._is_summarizing
    
    # 录音相关的槽函数
    @Slot()
    def toggleRecording(self):
        """切换录音状态（使用传统录音器）"""
        try:
            if self._is_recording:
                self._voice_recorder.stop_recording()
                track_button_clicked("voice_stop_traditional")
            else:
                self._voice_recorder.start_recording()
                track_button_clicked("voice_start_traditional")
        except Exception as e:
            self.voiceErrorOccurred.emit(f"录音操作失败: {str(e)}")
    
    @Slot()
    def toggleRecordingShortcut(self):
        """通过快捷键切换录音状态"""
        # 不能在转写过程中切换录音状态
        if self._is_transcribing:
            return
        self.toggleRecording()
        track_button_clicked("voice_toggle_shortcut")
    
    def _on_streaming_recording_started(self):
        """流式录音开始"""
        self._is_recording = True
        self.voiceRecordingStateChanged.emit(True)
    
    def _on_streaming_recording_stopped(self):
        """流式录音停止"""
        self._is_recording = False
        self.voiceRecordingStateChanged.emit(False)
    
    def _on_transcription_chunk_ready(self, chunk: str):
        """处理实时转写片段"""
        if chunk.strip():
            self.voiceTranscriptionChunkReady.emit(chunk)
    
    def _on_final_transcription_ready(self, transcription: str):
        """处理最终转写结果"""
        if transcription.strip():
            # 直接发送原始转写结果，不再自动调用DeepSeek
            self.voiceTranscriptionReady.emit(transcription)
    
    def _on_streaming_voice_error(self, error_message: str):
        """处理流式录音错误"""
        self._is_recording = False
        self.voiceRecordingStateChanged.emit(False)
        self.voiceErrorOccurred.emit(error_message)
    
    def _on_stop_command_detected(self, command: str):
        """处理停止命令"""
        self.voiceCommandDetected.emit("stop", command)
    
    def _on_send_command_detected(self, command: str):
        """处理发送命令"""
        self.voiceCommandDetected.emit("send", command)
        # 自动发送当前转写结果
        current_text = self._streaming_voice_recorder.get_current_transcription()
        if current_text.strip():
            self.sendResponse(current_text)
    
    def _on_recording_started(self):
        """录音开始（原版本）"""
        self._is_recording = True
        self.voiceRecordingStateChanged.emit(True)
    
    def _on_recording_stopped(self):
        """录音停止（原版本）"""
        self._is_recording = False
        self.voiceRecordingStateChanged.emit(False)
        # 录音停止后开始转写
        self._is_transcribing = True
        self.voiceTranscriptionStateChanged.emit(True)
    
    def _on_transcription_ready(self, transcription: str):
        """转写结果准备就绪（原版本）"""
        # 转写完成，更新状态
        self._is_transcribing = False
        self.voiceTranscriptionStateChanged.emit(False)
        
        if transcription.strip():
            # 直接发送原始转写结果，不再自动调用DeepSeek
            self.voiceTranscriptionReady.emit(transcription)
    
    def _on_voice_error(self, error_message: str):
        """录音错误（原版本）"""
        self._is_recording = False
        self.voiceRecordingStateChanged.emit(False)
        # 错误时也要重置转写状态
        self._is_transcribing = False
        self.voiceTranscriptionStateChanged.emit(False)
        self.voiceErrorOccurred.emit(error_message)
    
    @Slot(result=str)
    def getCurrentTranscription(self):
        """获取当前转写结果（传统录音器不支持实时转写）"""
        return ""
    
    @Slot()
    def clearTranscriptionBuffer(self):
        """清空转写缓冲区（传统录音器不需要）"""
        pass
    
    @Slot(str)
    def updateStopCommands(self, commands_json: str):
        """更新停止命令（JSON格式）"""
        try:
            import json
            commands = json.loads(commands_json)
            self._streaming_voice_recorder.update_stop_commands(commands)
        except Exception as e:
            self.voiceErrorOccurred.emit(f"更新停止命令失败: {str(e)}")
    
    @Slot(str) 
    def updateSendCommands(self, commands_json: str):
        """更新发送命令（JSON格式）"""
        try:
            import json
            commands = json.loads(commands_json)
            self._streaming_voice_recorder.update_send_commands(commands)
        except Exception as e:
            self.voiceErrorOccurred.emit(f"更新发送命令失败: {str(e)}")
    
    # 槽函数定义
    @Slot(int)
    def selectTodoItem(self, index: int):
        """选择TODO项目"""
        track_todo_action("click", todo_level=1)
        
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
        todo_item = self._todo_model.getTodoItem(index)
        if todo_item:
            # 如果有子任务，插入完整的任务树（包括总任务）
            if todo_item.children:
                insert_text = todo_item.to_markdown()
            else:
                # 没有子任务时，使用原来的逻辑
                if todo_item.content:
                    insert_text = todo_item.content
                else:
                    insert_text = todo_item.title
            
            # 发送信号插入内容
            self.todoContentInserted.emit(insert_text)
    
    @Slot(int)
    def markTodoDone(self, index: int):
        """标记TODO任务为完成"""
        todo_item = self._todo_model.getTodoItem(index)
        if todo_item:
            todo_item.mark_as_done()
            self._save_todos_to_file()
            # 刷新模型以更新显示
            self._todo_model.setTodos(self._todo_items)
    
    @Slot(int)
    def markTodoUndone(self, index: int):
        """标记TODO任务为未完成"""
        todo_item = self._todo_model.getTodoItem(index)
        if todo_item:
            todo_item.mark_as_undone()
            self._save_todos_to_file()
            # 刷新模型以更新显示
            self._todo_model.setTodos(self._todo_items)
    
    @Slot(int)
    def deleteTodoItem(self, index: int):
        """删除已完成的TODO项目"""
        todo_item = self._todo_model.getTodoItem(index)
        if todo_item and todo_item.is_done:
            # 从列表中移除该项目
            self._remove_todo_from_tree(todo_item)
            self._save_todos_to_file()
            # 刷新模型以更新显示
            self._todo_model.setTodos(self._todo_items)
            # 清除选中状态
            self._selected_todo_title = None
            self._selected_todo_detail = "选择一个任务查看详情"
            self.selectedTodoDetailChanged.emit()
        else:
            print("WARNING: 只能删除已完成的TODO项目", file=sys.stderr)
    
    def _remove_todo_from_tree(self, todo_item):
        """从TODO树中移除指定项目"""
        # 如果有父项目，从父项目的children中移除
        if todo_item.parent:
            if todo_item in todo_item.parent.children:
                todo_item.parent.children.remove(todo_item)
        else:
            # 如果是顶级项目，从根列表中移除
            if todo_item in self._todo_items:
                self._todo_items.remove(todo_item)
    
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
        try:
            response = {
                "result": feedback_text
            }
            
            # 输出到标准输出，确保使用UTF-8编码
            output = json.dumps(response, ensure_ascii=False)
            
            # 只输出JSON结果到stdout，所有调试信息都发送到stderr
            try:
                # 方法1：直接使用UTF-8编码写入
                print(output, flush=True)
            except UnicodeEncodeError:
                # 方法2：如果print失败，使用buffer方式
                if hasattr(sys.stdout, 'buffer'):
                    sys.stdout.buffer.write(output.encode('utf-8'))
                    sys.stdout.buffer.write(b'\n')
                    sys.stdout.buffer.flush()
                else:
                    # 方法3：最后的后备方案，使用ASCII安全输出
                    ascii_output = json.dumps(response, ensure_ascii=True)
                    sys.stdout.write(ascii_output)
                    sys.stdout.write('\n')
                    sys.stdout.flush()
            
            # 立即退出，避免额外输出
            QGuiApplication.instance().quit()
            
        except Exception as e:
            print(f"发送响应时出错: {str(e)}", file=sys.stderr)
            QGuiApplication.instance().quit()
    
    @Slot(str, result=str)
    def summarizeWithDeepSeek(self, content: str) -> str:
        """使用DeepSeek总结文本内容 - 异步版本"""
        if self._is_summarizing:
            return content  # 如果正在总结中，直接返回原内容
        
        # 启动异步总结
        self.startDeepSeekSummary(content)
        return content  # 立即返回原内容，避免阻塞UI
    
    @Slot(str)
    def startDeepSeekSummary(self, content: str):
        """开始DeepSeek总结任务"""
        if self._is_summarizing:
            return  # 如果正在总结中，忽略新请求
        
        self._is_summarizing = True
        self.deepseekSummaryStateChanged.emit(True)
        
        # 保存原始内容
        self._pending_summary_content = content
        
        # 使用QTimer延迟执行，避免阻塞UI
        QTimer.singleShot(50, self._performDeepSeekSummary)
    
    def _performDeepSeekSummary(self):
        """执行DeepSeek总结的实际工作"""
        try:
            content = self._pending_summary_content
            
            # 如果有旧的worker线程，先清理
            if self._deepseek_worker is not None:
                self._deepseek_worker.wait()  # 等待旧线程完成
                self._deepseek_worker.deleteLater()
            
            # 创建DeepSeekSummaryWorker实例
            self._deepseek_worker = DeepSeekSummaryWorker(content, self._project_directory, self)
            
            # 连接信号
            self._deepseek_worker.summaryCompleted.connect(self._on_summary_completed)
            self._deepseek_worker.summaryError.connect(self._on_summary_error)
            
            # 当线程完成时自动清理
            self._deepseek_worker.finished.connect(self._deepseek_worker.deleteLater)
            
            # 启动线程
            self._deepseek_worker.start()
            
        except Exception as e:
            error_msg = f"DeepSeek总结失败: {str(e)}"
            print(error_msg, file=sys.stderr)
            
            # 更新状态并发送错误
            self._is_summarizing = False
            self.deepseekSummaryStateChanged.emit(False)
            self.deepseekSummaryError.emit(error_msg)
    
    def _on_summary_completed(self, summary: str):
        """处理DeepSeek总结完成"""
        self._is_summarizing = False
        self.deepseekSummaryStateChanged.emit(False)
        self.deepseekSummaryReady.emit(summary)
    
    def _on_summary_error(self, error_message: str):
        """处理DeepSeek总结错误"""
        self._is_summarizing = False
        self.deepseekSummaryStateChanged.emit(False)
        self.deepseekSummaryError.emit(error_message)
    
    @Slot(int, int, int, int)
    def saveWindowGeometry(self, x: int, y: int, width: int, height: int):
        """保存窗口几何信息"""
        if not self.rememberPosition:
            return
        
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

    @Slot()
    def openVoiceSettings(self):
        """打开语音设置对话框 - QML版本"""
        try:
            config_proxy = ConfigManagerProxy(self._config_mgr, self)
            self.voiceSettingsRequested.emit(config_proxy)
            track_button_clicked("voice_settings_opened")
        except Exception as e:
            self.voiceErrorOccurred.emit(f"打开语音设置失败: {str(e)}")
    
    @Slot()
    def openSettings(self):
        """打开主设置对话框"""
        try:
            config_proxy = ConfigManagerProxy(self._config_mgr, self)
            self.settingsRequested.emit(config_proxy)
            track_button_clicked("settings_opened")
        except Exception as e:
            self.voiceErrorOccurred.emit(f"打开设置失败: {str(e)}")
    
    @Slot(str, str)
    def trackShortcutUsed(self, shortcut_name: str, action: str):
        """统计快捷键使用"""
        try:
            from ..core.analytics import track_shortcut_used
            track_shortcut_used(shortcut_name, action)
        except Exception as e:
            print(f"Failed to track shortcut usage: {e}", file=sys.stderr)
    
    @Slot(str, str)
    def trackConfigAction(self, action: str, config_type: str):
        """统计配置操作"""
        try:
            from ..core.analytics import track_config_action
            track_config_action(action, config_type)
        except Exception as e:
            print(f"Failed to track config action: {e}", file=sys.stderr)

    @Slot('QVariant', 'QVariant')
    def onVoiceSettingsSaved(self, stopCommands, sendCommands):
        """处理语音设置保存事件"""
        try:
            # 更新流式录音器的命令设置
            if stopCommands and len(stopCommands) > 0:
                self._streaming_voice_recorder.update_stop_commands(stopCommands)
            if sendCommands and len(sendCommands) > 0:
                self._streaming_voice_recorder.update_send_commands(sendCommands)
                
            track_button_clicked("voice_settings_saved")
        except Exception as e:
            self.voiceErrorOccurred.emit(f"保存语音设置失败: {str(e)}")

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
        style_loaded = load_default_styles()
        
        self.engine = QQmlApplicationEngine()
        
        # 注册自定义类型
        qmlRegisterType(AnswerBoxBackend, "AnswerBoxBackend", 1, 0, "AnswerBoxBackend")
        qmlRegisterType(StyleManager, "StyleManager", 1, 0, "StyleManager")
        qmlRegisterType(ConfigManagerProxy, "ConfigManagerProxy", 1, 0, "ConfigManagerProxy")
        
        # 创建后端对象
        self.backend = AnswerBoxBackend()
        
        # 设置QML上下文属性
        self.engine.rootContext().setContextProperty("backend", self.backend)
        self.engine.rootContext().setContextProperty("styleManager", self.style_manager)
        
        # 添加QML模块路径
        qml_dir = Path(__file__).parent / "qml"
        
        # 添加模块搜索路径
        self.engine.addImportPath(str(qml_dir))
        self.engine.addImportPath(str(qml_dir.parent))
        
        # 检查 qmldir 文件
        qmldir_file = qml_dir / "qmldir"
        if qmldir_file.exists():
            with open(qmldir_file, 'r', encoding='utf-8') as f:
                qmldir_content = f.read()
        
        # 加载QML文件
        qml_file = qml_dir / "Main.qml"
        self.engine.load(qml_file)
        
        # 检查是否加载成功
        if not self.engine.rootObjects():
            print("ERROR: 无法加载QML文件", file=sys.stderr)
            sys.exit(-1)
        else:
            print("DEBUG: QML界面加载成功", file=sys.stderr)
    
    def run(self):
        """运行应用"""
        return self.app.exec()


def main():
    """主函数"""
    answer_box = AnswerBoxQML()
    return answer_box.run()


if __name__ == "__main__":
    sys.exit(main()) 
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

class TodoItem:
    """TODO项目数据结构"""
    
    def __init__(self, title: str, content: str = "", level: int = 1, parent: Optional['TodoItem'] = None, attributes: Optional[Dict[str, str]] = None):
        self.title = title
        self.content = content
        self.level = level
        self.parent = parent
        self.children: List['TodoItem'] = []
        self.attributes = attributes or {}
    
    def add_child(self, child: 'TodoItem'):
        """添加子项目"""
        child.parent = self
        self.children.append(child)
    
    @property
    def is_done(self) -> bool:
        """检查任务是否完成"""
        return self.attributes.get('state', '').lower() == 'done'
    
    @property
    def display_title(self) -> str:
        """获取显示标题，如果完成则添加✅"""
        if self.is_done:
            return f"✅ {self.title}"
        return self.title
    
    def get_attribute(self, key: str, default: str = "") -> str:
        """获取属性值"""
        return self.attributes.get(key, default)
    
    def set_attribute(self, key: str, value: str):
        """设置属性值"""
        self.attributes[key] = value
    
    def mark_as_done(self):
        """标记任务为完成"""
        self.set_attribute("state", "done")
    
    def mark_as_undone(self):
        """标记任务为未完成"""
        if "state" in self.attributes:
            del self.attributes["state"]
    
    def to_markdown(self) -> str:
        """转换为markdown格式"""
        # 标题行
        header = "#" * self.level + " " + self.title
        lines = [header]
        
        # 属性行
        for key, value in self.attributes.items():
            lines.append(f"{key}={value}")
        
        # 内容
        if self.content:
            if self.attributes:  # 如果有属性，添加空行分隔
                lines.append("")
            lines.append(self.content)
        
        # 递归添加子项目
        for child in self.children:
            lines.append("")  # 在子项目前添加空行
            child_markdown = child.to_markdown()
            lines.append(child_markdown)
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "display_title": self.display_title,
            "content": self.content,
            "level": self.level,
            "attributes": self.attributes,
            "is_done": self.is_done,
            "children": [child.to_dict() for child in self.children]
        }

class TodoParser:
    """TODO.md文件解析器"""
    
    def __init__(self):
        self.root_items: List[TodoItem] = []
        self.current_file_path: Optional[str] = None
    
    def parse_file(self, file_path: str) -> List[TodoItem]:
        """解析TODO.md文件"""
        path = Path(file_path)
        if not path.exists():
            return []
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.current_file_path = file_path
            return self.parse_content(content)
        except (IOError, UnicodeDecodeError) as e:
            print(f"Warning: Could not read TODO file {file_path}: {e}")
            return []
    
    def save_todos_to_file(self, todos: List[TodoItem], file_path: Optional[str] = None) -> bool:
        """保存TODO列表到文件"""
        if not file_path:
            file_path = self.current_file_path
        
        if not file_path:
            print("Error: No file path specified for saving")
            return False
        
        try:
            # 转换为markdown格式
            markdown_content = self._todos_to_markdown(todos)
            
            # 保存到文件
            path = Path(file_path)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            return True
        except (IOError, UnicodeEncodeError) as e:
            print(f"Error: Could not save TODO file {file_path}: {e}")
            return False
    
    def _todos_to_markdown(self, todos: List[TodoItem]) -> str:
        """将TODO列表转换为markdown格式"""
        lines = []
        for i, todo in enumerate(todos):
            todo_markdown = todo.to_markdown()
            lines.append(todo_markdown)
            
            # 在顶级TODO之间添加额外空行（除了最后一个）
            if i < len(todos) - 1:
                lines.append("")
        
        return "\n".join(lines).rstrip() + "\n"  # 确保文件以换行符结尾
    
    def _parse_attributes(self, lines: List[str]) -> Dict[str, str]:
        """解析属性行，返回属性字典"""
        attributes = {}
        for line in lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                # 匹配 key=value 格式
                match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*)$', line)
                if match:
                    key = match.group(1)
                    value = match.group(2).strip()
                    attributes[key] = value
        return attributes
    
    def parse_content(self, content: str) -> List[TodoItem]:
        """解析TODO内容"""
        lines = content.split('\n')
        self.root_items = []
        current_stack: List[TodoItem] = []
        current_content_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # 检查是否是标题行
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            
            if header_match:
                # 处理之前积累的内容和属性
                if current_stack and current_content_lines:
                    # 分离内容和属性
                    content_lines, attributes = self._extract_content_and_attributes(current_content_lines)
                    current_stack[-1].content = '\n'.join(content_lines).strip()
                    current_stack[-1].attributes.update(attributes)
                    current_content_lines = []
                
                # 解析新标题
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                # 创建新的TODO项目
                todo_item = TodoItem(title=title, level=level)
                
                # 调整栈结构
                while current_stack and current_stack[-1].level >= level:
                    current_stack.pop()
                
                # 添加到父项目或根项目
                if current_stack:
                    current_stack[-1].add_child(todo_item)
                else:
                    self.root_items.append(todo_item)
                
                current_stack.append(todo_item)
            
            elif line.strip():  # 非空行作为内容
                current_content_lines.append(line)
            
            i += 1
        
        # 处理最后的内容和属性
        if current_stack and current_content_lines:
            content_lines, attributes = self._extract_content_and_attributes(current_content_lines)
            current_stack[-1].content = '\n'.join(content_lines).strip()
            current_stack[-1].attributes.update(attributes)
        
        return self.root_items
    
    def _extract_content_and_attributes(self, lines: List[str]) -> tuple[List[str], Dict[str, str]]:
        """从行列表中提取内容和属性"""
        content_lines = []
        attributes = {}
        
        for line in lines:
            stripped_line = line.strip()
            
            # 检查是否是属性行 (key=value格式)
            if '=' in stripped_line and not stripped_line.startswith('#'):
                match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*)$', stripped_line)
                if match:
                    key = match.group(1)
                    value = match.group(2).strip()
                    attributes[key] = value
                    continue
            
            # 如果不是属性行，就是内容行
            content_lines.append(line)
        
        return content_lines, attributes
    
    def find_todo_file(self, project_directory: str) -> Optional[str]:
        """在项目目录中查找TODO.md文件"""
        if not project_directory:
            return None
        
        project_path = Path(project_directory)
        if not project_path.exists():
            return None
        
        # 查找TODO.md文件（不区分大小写）
        for pattern in ['TODO.md', 'todo.md', 'Todo.md', 'TODO.MD']:
            todo_file = project_path / pattern
            if todo_file.exists():
                return str(todo_file)
        
        return None
    
    def load_project_todos(self, project_directory: str) -> List[TodoItem]:
        """加载项目的TODO列表"""
        todo_file = self.find_todo_file(project_directory)
        if todo_file:
            return self.parse_file(todo_file)
        return [] 
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
    
    def parse_file(self, file_path: str) -> List[TodoItem]:
        """解析TODO.md文件"""
        path = Path(file_path)
        if not path.exists():
            return []
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.parse_content(content)
        except (IOError, UnicodeDecodeError) as e:
            print(f"Warning: Could not read TODO file {file_path}: {e}")
            return []
    
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
                # 处理之前积累的内容
                if current_stack and current_content_lines:
                    current_stack[-1].content = '\n'.join(current_content_lines).strip()
                    current_content_lines = []
                
                # 解析新标题
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                # 查找紧跟标题的属性行
                attributes = {}
                j = i + 1
                attribute_lines = []
                
                # 收集紧跟标题的属性行（直到遇到空行、下一个标题或内容）
                while j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line:  # 空行，停止收集属性
                        break
                    if re.match(r'^#{1,6}\s+', next_line):  # 下一个标题，停止收集
                        break
                    if '=' in next_line and not next_line.startswith('#'):
                        attribute_lines.append(lines[j])
                        j += 1
                    else:
                        break
                
                # 解析属性
                if attribute_lines:
                    attributes = self._parse_attributes(attribute_lines)
                    i = j - 1  # 调整索引，因为for循环会+1
                
                # 创建新的TODO项目
                todo_item = TodoItem(title=title, level=level, attributes=attributes)
                
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
        
        # 处理最后的内容
        if current_stack and current_content_lines:
            current_stack[-1].content = '\n'.join(current_content_lines).strip()
        
        return self.root_items
    
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
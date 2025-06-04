#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TODO解析器的单元测试
测试TODO.md文件的解析功能，包括属性支持、层级结构、状态管理等
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# 添加buddy模块到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from buddy.ui.todo_parser import TodoParser, TodoItem


class TestTodoItem(unittest.TestCase):
    """测试TodoItem类"""
    
    def test_basic_creation(self):
        """测试基本的TodoItem创建"""
        item = TodoItem("测试任务", "任务描述", level=1)
        self.assertEqual(item.title, "测试任务")
        self.assertEqual(item.content, "任务描述")
        self.assertEqual(item.level, 1)
        self.assertEqual(len(item.children), 0)
        self.assertEqual(len(item.attributes), 0)
    
    def test_attributes_creation(self):
        """测试带属性的TodoItem创建"""
        attributes = {"state": "done", "priority": "high"}
        item = TodoItem("测试任务", attributes=attributes)
        self.assertEqual(item.attributes, attributes)
        self.assertTrue(item.is_done)
        self.assertEqual(item.get_attribute("priority"), "high")
        self.assertEqual(item.get_attribute("nonexistent", "default"), "default")
    
    def test_display_title(self):
        """测试显示标题功能"""
        # 普通任务
        item = TodoItem("普通任务")
        self.assertEqual(item.display_title, "普通任务")
        
        # 完成的任务 - 不再添加✅图标
        item_done = TodoItem("完成任务", attributes={"state": "done"})
        self.assertEqual(item_done.display_title, "完成任务")
        
        # 进行中的任务
        item_going = TodoItem("进行中任务", attributes={"state": "going"})
        self.assertEqual(item_going.display_title, "进行中任务")
    
    def test_is_done_property(self):
        """测试is_done属性"""
        # 未完成任务
        item = TodoItem("未完成任务")
        self.assertFalse(item.is_done)
        
        # 完成任务（小写）
        item_done = TodoItem("完成任务", attributes={"state": "done"})
        self.assertTrue(item_done.is_done)
        
        # 完成任务（大写）
        item_done_upper = TodoItem("完成任务", attributes={"state": "DONE"})
        self.assertTrue(item_done_upper.is_done)
        
        # 其他状态
        item_other = TodoItem("其他状态", attributes={"state": "pending"})
        self.assertFalse(item_other.is_done)
    
    def test_attribute_methods(self):
        """测试属性操作方法"""
        item = TodoItem("测试任务")
        
        # 设置属性
        item.set_attribute("priority", "high")
        self.assertEqual(item.get_attribute("priority"), "high")
        
        # 覆盖属性
        item.set_attribute("priority", "low")
        self.assertEqual(item.get_attribute("priority"), "low")
    
    def test_children_management(self):
        """测试子项目管理"""
        parent = TodoItem("父任务")
        child1 = TodoItem("子任务1")
        child2 = TodoItem("子任务2")
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        self.assertEqual(len(parent.children), 2)
        self.assertEqual(child1.parent, parent)
        self.assertEqual(child2.parent, parent)
    
    def test_to_dict(self):
        """测试字典转换"""
        attributes = {"state": "done", "priority": "high"}
        item = TodoItem("测试任务", "任务描述", level=2, attributes=attributes)
        
        result = item.to_dict()
        
        self.assertEqual(result["title"], "测试任务")
        self.assertEqual(result["display_title"], "测试任务")
        self.assertEqual(result["content"], "任务描述")
        self.assertEqual(result["level"], 2)
        self.assertEqual(result["attributes"], attributes)
        self.assertTrue(result["is_done"])
        self.assertEqual(result["children"], [])

    def test_mark_as_done_undone(self):
        """测试标记任务完成和未完成"""
        item = TodoItem("测试任务")
        
        # 初始状态应该是未完成
        self.assertFalse(item.is_done)
        
        # 标记为完成
        item.mark_as_done()
        self.assertTrue(item.is_done)
        self.assertEqual(item.attributes["state"], "done")
        
        # 标记为未完成
        item.mark_as_undone()
        self.assertFalse(item.is_done)
        self.assertNotIn("state", item.attributes)
    
    def test_to_markdown(self):
        """测试转换为markdown格式"""
        # 简单任务
        item = TodoItem("简单任务", level=1)
        expected = "# 简单任务"
        self.assertEqual(item.to_markdown(), expected)
        
        # 带属性的任务
        item_with_attrs = TodoItem("任务", level=2, attributes={"state": "done", "priority": "high"})
        result = item_with_attrs.to_markdown()
        self.assertIn("## 任务", result)
        self.assertIn("state=done", result)
        self.assertIn("priority=high", result)
        
        # 带内容的任务
        item_with_content = TodoItem("任务", content="任务描述", level=1)
        result = item_with_content.to_markdown()
        self.assertIn("# 任务", result)
        self.assertIn("任务描述", result)
        
        # 带属性和内容的任务
        item_complex = TodoItem("复杂任务", content="详细描述", level=1, attributes={"state": "going"})
        result = item_complex.to_markdown()
        lines = result.split('\n')
        self.assertEqual(lines[0], "# 复杂任务")
        self.assertEqual(lines[1], "state=going")
        self.assertEqual(lines[2], "")  # 空行分隔
        self.assertEqual(lines[3], "详细描述")

    def test_insert_content_with_children(self):
        """测试双击有子任务的TODO项目时返回完整任务树"""
        # 创建一个带子任务的TODO项目
        parent = TodoItem("主任务", "主任务描述", level=1)
        child1 = TodoItem("子任务1", "子任务1描述", level=2)
        child2 = TodoItem("子任务2", level=2, attributes={"state": "done"})
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        # 验证有子任务的情况下应该返回完整markdown
        result = parent.to_markdown()
        
        # 检查结果包含主任务和所有子任务
        self.assertIn("# 主任务", result)
        self.assertIn("主任务描述", result)
        self.assertIn("## 子任务1", result)
        self.assertIn("子任务1描述", result)
        self.assertIn("## 子任务2", result)
        self.assertIn("state=done", result)
        
        # 验证没有子任务的情况下按原来逻辑处理
        single_task = TodoItem("单独任务", "单独任务内容")
        self.assertEqual(len(single_task.children), 0)  # 确认没有子任务


class TestTodoParser(unittest.TestCase):
    """测试TodoParser类"""
    
    def setUp(self):
        """测试前准备"""
        self.parser = TodoParser()
    
    def test_parse_simple_content(self):
        """测试解析简单内容"""
        content = """# 第一个任务
这是第一个任务的描述

## 第二个任务
这是第二个任务的描述"""
        
        todos = self.parser.parse_content(content)
        
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].title, "第一个任务")
        self.assertEqual(todos[0].level, 1)
        self.assertEqual(todos[0].content, "这是第一个任务的描述")
        
        self.assertEqual(len(todos[0].children), 1)
        self.assertEqual(todos[0].children[0].title, "第二个任务")
        self.assertEqual(todos[0].children[0].level, 2)
        self.assertEqual(todos[0].children[0].content, "这是第二个任务的描述")
    
    def test_parse_with_attributes(self):
        """测试解析带属性的内容"""
        content = """# 任务一
state=done
priority=high

这是任务一的描述

# 任务二
state=going
assigned_to=张三

这是任务二的描述"""
        
        todos = self.parser.parse_content(content)
        
        self.assertEqual(len(todos), 2)
        
        # 检查第一个任务
        task1 = todos[0]
        self.assertEqual(task1.title, "任务一")
        self.assertEqual(task1.attributes["state"], "done")
        self.assertEqual(task1.attributes["priority"], "high")
        self.assertTrue(task1.is_done)
        self.assertEqual(task1.content, "这是任务一的描述")
        
        # 检查第二个任务
        task2 = todos[1]
        self.assertEqual(task2.title, "任务二")
        self.assertEqual(task2.attributes["state"], "going")
        self.assertEqual(task2.attributes["assigned_to"], "张三")
        self.assertFalse(task2.is_done)
        self.assertEqual(task2.content, "这是任务二的描述")
    
    def test_parse_nested_structure(self):
        """测试解析嵌套结构"""
        content = """# 主任务
state=going

主任务描述

## 子任务1
state=done

子任务1描述

### 子子任务
state=pending

子子任务描述

## 子任务2
state=going

子任务2描述"""
        
        todos = self.parser.parse_content(content)
        
        self.assertEqual(len(todos), 1)
        
        main_task = todos[0]
        self.assertEqual(main_task.title, "主任务")
        self.assertEqual(main_task.level, 1)
        self.assertEqual(len(main_task.children), 2)
        
        # 检查子任务1
        subtask1 = main_task.children[0]
        self.assertEqual(subtask1.title, "子任务1")
        self.assertEqual(subtask1.level, 2)
        self.assertTrue(subtask1.is_done)
        self.assertEqual(len(subtask1.children), 1)
        
        # 检查子子任务
        subsubtask = subtask1.children[0]
        self.assertEqual(subsubtask.title, "子子任务")
        self.assertEqual(subsubtask.level, 3)
        self.assertEqual(subsubtask.attributes["state"], "pending")
        
        # 检查子任务2
        subtask2 = main_task.children[1]
        self.assertEqual(subtask2.title, "子任务2")
        self.assertEqual(subtask2.level, 2)
        self.assertEqual(subtask2.attributes["state"], "going")
    
    def test_parse_attributes_formats(self):
        """测试不同的属性格式"""
        content = """# 任务测试
key1=value1
key2 = value2
key3= value3
key4 =value4
key_with_underscore=test
keyWithCamelCase=test

任务描述"""
        
        todos = self.parser.parse_content(content)
        
        self.assertEqual(len(todos), 1)
        task = todos[0]
        
        self.assertEqual(task.attributes["key1"], "value1")
        self.assertEqual(task.attributes["key2"], "value2")
        self.assertEqual(task.attributes["key3"], "value3")
        self.assertEqual(task.attributes["key4"], "value4")
        self.assertEqual(task.attributes["key_with_underscore"], "test")
        self.assertEqual(task.attributes["keyWithCamelCase"], "test")
    
    def test_parse_empty_content(self):
        """测试解析空内容"""
        content = ""
        todos = self.parser.parse_content(content)
        self.assertEqual(len(todos), 0)
    
    def test_parse_no_attributes(self):
        """测试解析无属性的任务"""
        content = """# 简单任务
任务描述"""
        
        todos = self.parser.parse_content(content)
        
        self.assertEqual(len(todos), 1)
        task = todos[0]
        self.assertEqual(task.title, "简单任务")
        self.assertEqual(len(task.attributes), 0)
        self.assertFalse(task.is_done)
    
    def test_parse_mixed_content(self):
        """测试解析混合内容（有些有属性，有些没有）"""
        content = """# 任务A
state=done

任务A描述

# 任务B
任务B描述

# 任务C
priority=low
state=pending

任务C描述"""
        
        todos = self.parser.parse_content(content)
        
        self.assertEqual(len(todos), 3)
        
        # 任务A - 有属性
        self.assertTrue(todos[0].is_done)
        self.assertEqual(len(todos[0].attributes), 1)
        
        # 任务B - 无属性
        self.assertFalse(todos[1].is_done)
        self.assertEqual(len(todos[1].attributes), 0)
        
        # 任务C - 有多个属性
        self.assertFalse(todos[2].is_done)
        self.assertEqual(len(todos[2].attributes), 2)
        self.assertEqual(todos[2].attributes["priority"], "low")
    
    def test_parse_file_operations(self):
        """测试文件操作"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("""# 测试任务
state=done
priority=high

这是一个测试任务""")
            temp_file = f.name
        
        try:
            # 测试解析文件
            todos = self.parser.parse_file(temp_file)
            
            self.assertEqual(len(todos), 1)
            task = todos[0]
            self.assertEqual(task.title, "测试任务")
            self.assertTrue(task.is_done)
            self.assertEqual(task.attributes["priority"], "high")
            
        finally:
            # 清理临时文件
            os.unlink(temp_file)
    
    def test_parse_nonexistent_file(self):
        """测试解析不存在的文件"""
        todos = self.parser.parse_file("nonexistent_file.md")
        self.assertEqual(len(todos), 0)
    
    def test_find_todo_file(self):
        """测试查找TODO文件"""
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建TODO.md文件
            todo_file = Path(temp_dir) / "TODO.md"
            todo_file.write_text("# 测试任务", encoding='utf-8')
            
            # 测试查找
            found_file = self.parser.find_todo_file(temp_dir)
            self.assertEqual(found_file, str(todo_file))
            
            # 测试不存在的目录
            found_file = self.parser.find_todo_file("nonexistent_dir")
            self.assertIsNone(found_file)
    
    def test_load_project_todos(self):
        """测试加载项目TODO"""
        # 创建临时目录和TODO文件
        with tempfile.TemporaryDirectory() as temp_dir:
            todo_file = Path(temp_dir) / "TODO.md"
            todo_file.write_text("""# 项目任务
state=going

项目任务描述""", encoding='utf-8')
            
            # 测试加载
            todos = self.parser.load_project_todos(temp_dir)
            
            self.assertEqual(len(todos), 1)
            self.assertEqual(todos[0].title, "项目任务")
            self.assertEqual(todos[0].attributes["state"], "going")


class TestTodoParserIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_real_todo_structure(self):
        """测试真实的TODO结构"""
        content = """# TODO展示
## TODO支持属性
TODO 支持属性， 紧接着标题的赋值预计， 例如：
state=going
abc=123

## 完成的任务加个✅
state=done
完成的任务加个✅在前面(state=done 的)

## TODO没有内容时，就替换标题
TODO没有内容时， 双击时就插入标题

# 优化answer_box.py
### Style Sheet 模块
实现一个 Style Sheet 模块，

## 引入QML
state=done
使用 QML 拆分逻辑和布局
如果需要，可以参考：
https://doc.qt.io/qtforpython-6/tutorials/qmlapp/qmlapplication.html

## 引入.qss
引入 .qss 拆分样式和布局
如果需要可以参考：
https://doc.qt.io/qt-6/stylesheet.html

# 初始化引导
引导设置 Cursor User Rules"""
        
        parser = TodoParser()
        todos = parser.parse_content(content)
        
        # 验证顶级结构
        self.assertEqual(len(todos), 3)
        self.assertEqual(todos[0].title, "TODO展示")
        self.assertEqual(todos[1].title, "优化answer_box.py")
        self.assertEqual(todos[2].title, "初始化引导")
        
        # 验证TODO展示的子任务
        todo_display = todos[0]
        self.assertEqual(len(todo_display.children), 3)
        
        # 验证属性支持子任务
        attr_task = todo_display.children[0]
        self.assertEqual(attr_task.title, "TODO支持属性")
        self.assertEqual(attr_task.attributes.get("state"), "going")
        self.assertEqual(attr_task.attributes.get("abc"), "123")
        
        # 验证完成的任务
        done_task = todo_display.children[1]
        self.assertEqual(done_task.title, "完成的任务加个✅")
        self.assertTrue(done_task.is_done)
        self.assertEqual(done_task.display_title, "完成的任务加个✅")
        
        # 验证QML任务
        qml_task = todos[1].children[1]  # 优化answer_box.py -> 引入QML
        self.assertEqual(qml_task.title, "引入QML")
        self.assertTrue(qml_task.is_done)

    def test_real_todo_structure2(self):
        """测试真实的TODO结构"""
        content = """
# 数据统计
添加数据统计功能，参考：
``` python
from amplitude import Amplitude
amplitude = Amplitude("19f4e9af0ddd8891fab01dd53202af2f")
from amplitude import BaseEvent

amplitude.track(
    BaseEvent(
        event_type="Sign Up",
        device_id="<ENTER DEVICE ID>",
        event_properties={
            "source": "notification"
        }
    )
)
```
"""
        parser = TodoParser()
        todos = parser.parse_content(content)

        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0].title, "数据统计")
        self.assertTrue(todos[0].content.startswith("添加数据统计功能，参考："))

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2) 
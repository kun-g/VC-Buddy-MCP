#!/usr/bin/env python3
"""FastMCP Server runner for Vibe Coding Buddy."""
from fastmcp import FastMCP
import subprocess
import json
import os

mcp = FastMCP(
    name="Vibe Coding Buddy",
    version="0.1.0",
    instructions="This is a test server for Vibe Coding Buddy.",
)

@mcp.tool()
def ask_for_feedback(
    summary: str,
    project_directory: str = None,
) -> str:
    """
    向用户请求交互式反馈的工具。
    
    **使用场景**：
    1. 当LLM需要用户确认或澄清需求时
    2. 当LLM完成了某个任务，需要用户验证结果时
    3. 当LLM需要用户提供额外信息来继续工作时
    4. 当LLM遇到多个选项需要用户选择时
    5. 当LLM完成一个阶段性工作，需要用户反馈下一步计划时
    
    **LLM调用指导**：
    - 在summary参数中简洁明确地描述你需要反馈的内容
    - 避免在一次调用中询问多个无关的问题
    - 使用清晰的语言，让用户容易理解你的请求
    - 如果用户的反馈为空，表示用户满意当前结果，可以继续下一步
    - 根据用户反馈调整你的后续行为
    - project_directory用于指定项目目录，便于后续操作
    
    **示例用法**：
    - ask_for_feedback("我已经重构了配置管理系统，请确认是否还需要其他改进", "/path/to/project")
    - ask_for_feedback("我找到了两种解决方案，A方案更简单，B方案更灵活，您倾向于哪种？")
    - ask_for_feedback("代码修改完成，请测试功能是否正常", project_directory)
    
    Args:
        summary: 简洁的反馈请求描述，会显示给用户
        project_directory: 项目目录路径，可选参数
        
    Returns:
        用户的反馈内容，JSON格式的字符串，包含result字段
    """
    print("ask_for_feedback", summary, "project_directory:", project_directory)
    
    # 准备传递给answer_box的数据
    input_data = {"summary": summary}
    if project_directory:
        input_data["project_directory"] = project_directory
    
    # 启动 ui/answer_box.py,获取 stdout
    process = subprocess.Popen(
        # ["python", "buddy/ui/answer_box.py"], 
        ["python", "buddy/ui/answer_box_qml.py"], 
        stdout=subprocess.PIPE, 
        stdin=subprocess.PIPE, 
        text=True,
        cwd=project_directory if project_directory and os.path.exists(project_directory) else None
    )
    process.stdin.write(json.dumps(input_data, ensure_ascii=False))
    process.stdin.flush()
    stdout, _ = process.communicate()
    return stdout or '{"result": ""}'

if __name__ == "__main__":
    mcp.run(transport="stdio")
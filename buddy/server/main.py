#!/usr/bin/env python3
"""FastMCP Server runner for Vibe Coding Buddy."""
from fastmcp import FastMCP
import subprocess
import json
import os
import sys

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
    - 使用清晰的语言，在summary参数中简洁明确地描述你需要反馈的内容
    - summary 过长时，要分多行显示
    - 如果用户的反馈为空，表示用户满意当前结果，可以继续下一步
    - 根据用户反馈调整你的后续行为
    - project_directory用于指定项目目录， 要符合当前操作系统路径格式

    Returns:
        用户的反馈内容，JSON格式的字符串，包含result字段
    """
    # 准备传递给answer_box的数据
    input_data = {"summary": summary, "project_directory": project_directory}
    
    # 使用上下文管理器确保子进程正确清理
    try:
        with subprocess.Popen(
            [sys.executable, "buddy/ui/answer_box_qml.py"], 
            stdout=subprocess.PIPE, 
            stdin=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            line_buffering=True  # 明确指定行缓冲
        ) as process:
            # 写入数据并关闭stdin
            input_json = json.dumps(input_data, ensure_ascii=False)
            stdout, stderr = process.communicate(input=input_json)
            
            # 检查子进程是否正常退出
            if process.returncode != 0:
                print(f"子进程异常退出 (code: {process.returncode}): {stderr}", file=sys.stderr)
                return '{"result": ""}'
            
            return stdout or '{"result": ""}'
            
    except Exception as e:
        print(f"启动子进程时出错: {e}", file=sys.stderr)
        return '{"result": ""}'

if __name__ == "__main__":
    mcp.run(transport="stdio")

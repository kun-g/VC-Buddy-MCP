#!/usr/bin/env python3
"""FastMCP Server runner for Vibe Coding Buddy."""
from fastmcp import FastMCP
import subprocess
import json
import os
import sys
from pathlib import Path

# 导入版本获取模块
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.version import get_app_version

from urllib.parse import unquote

mcp = FastMCP(
    name="Vibe Coding Buddy",
    version=get_app_version(),
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
    # URL解码project_directory以处理编码的路径
    if project_directory:
        project_directory = unquote(project_directory)
    
    # 准备传递给answer_box的数据
    input_data = {"summary": summary, "project_directory": project_directory}
    
    # 获取当前脚本所在目录，确保正确的工作目录
    current_dir = Path(__file__).parent.parent.parent  # 从buddy/server/main.py回到根目录
    ui_script = current_dir / "buddy" / "ui" / "answer_box_qml.py"
    
    # 确保UI脚本存在
    if not ui_script.exists():
        return json.dumps({"result": f"UI脚本不存在: {ui_script}"}, ensure_ascii=False)
    
    try:
        # 在Windows系统上设置编码环境变量
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # 启动 ui/answer_box.py,获取 stdout
        process = subprocess.Popen(
            [sys.executable, str(ui_script)], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE, 
            text=True,
            encoding='utf-8',
            env=env,  # 设置环境变量
            cwd=str(current_dir),  # 设置正确的工作目录
        )
        
        # 发送输入数据
        input_json = json.dumps(input_data, ensure_ascii=False)
        print(f"DEBUG: 发送给UI的数据: {input_json}", file=sys.stderr)
        
        # 增加超时时间到10分钟，给用户足够时间输入
        try:
            stdout, stderr = process.communicate(input=input_json, timeout=600)  # 10分钟超时
        except subprocess.TimeoutExpired:
            print("DEBUG: UI进程超时，用户可能没有及时响应", file=sys.stderr)
            process.kill()
            return json.dumps({"result": "UI界面超时关闭"}, ensure_ascii=False)
        
        # 如果有错误输出，记录它
        if stderr:
            print(f"UI进程错误输出: {stderr}", file=sys.stderr)
        
        print(f"DEBUG: UI进程返回数据: {stdout}", file=sys.stderr)
        
        # 处理返回结果
        if stdout and stdout.strip():
            # 从输出中提取JSON部分（可能混合了其他日志信息）
            lines = stdout.strip().split('\n')
            
            # 查找包含JSON的行
            for line in lines:
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        # 验证是否为有效JSON并直接返回
                        json.loads(line)  # 验证JSON有效性
                        print(f"DEBUG: 返回UI的JSON: {line}", file=sys.stderr)
                        return line
                    except json.JSONDecodeError:
                        continue
            
            # 如果没有找到有效JSON，说明UI出错了
            print(f"DEBUG: UI未返回有效JSON，原始输出: {stdout}", file=sys.stderr)
            return json.dumps({"result": f"UI返回格式错误: {stdout.strip()}"}, ensure_ascii=False)
        else:
            return json.dumps({"result": ""}, ensure_ascii=False)
            
    except Exception as e:
        return json.dumps({"result": f"启动UI时出错: {str(e)}"}, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run(transport="stdio")

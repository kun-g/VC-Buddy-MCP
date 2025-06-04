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
from pathlib import Path

# 导入DeepSeek相关模块
sys.path.append(str(Path(__file__).parent.parent))
try:
    from core.deepseek_client import DeepSeekClient, DeepSeekService, DeepSeekMessage
    from ui.config import ConfigManager
except ImportError as e:
    print(f"Warning: Could not import DeepSeek modules: {e}")

mcp = FastMCP(
    name="Vibe Coding Buddy",
    version=get_app_version(),
    instructions="This is a test server for Vibe Coding Buddy.",
)

def _get_deepseek_client(project_directory: str = None) -> DeepSeekClient:
    """获取DeepSeek客户端实例"""
    config = ConfigManager(project_directory=project_directory)
    api_key = config.deepseek_api_key
    
    if not api_key:
        raise Exception("DeepSeek API密钥未配置。请在配置文件中设置deepseek.api_key或设置DEEPSEEK_API_KEY环境变量。")
    
    return DeepSeekClient(
        api_key=api_key,
        base_url=config.deepseek_api_url
    )

def _deepseek_summarize(content: str, project_directory: str = None) -> str:
    """使用DeepSeek对内容进行总结"""
    try:
        client = _get_deepseek_client(project_directory)
        
        system_prompt = """你是一个专业的内容总结助手。请对用户提供的内容进行简洁、准确的总结。
总结要求：
1. 提取核心要点
2. 保持逻辑清晰
3. 语言简洁明了
4. 突出重要信息
请用中文回复。"""
        
        response = client.simple_chat(
            user_input=f"请总结以下内容：\n\n{content}",
            system_prompt=system_prompt
        )
        
        return response
        
    except Exception as e:
        return f"DeepSeek总结失败: {str(e)}"

@mcp.tool()
def deepseek_summarize(
    content: str,
    project_directory: str = None,
) -> str:
    """
    使用DeepSeek对用户输入的内容进行智能总结。
    
    这个工具专门用于处理用户输入的文本内容，提取关键信息并生成简洁的总结。
    适用于长文本的压缩、要点提取、内容整理等场景。
    
    Args:
        content: 需要总结的文本内容
        project_directory: 项目目录路径，用于获取项目特定的配置，可选参数
        
    Returns:
        DeepSeek生成的总结内容
    """
    # URL解码project_directory以处理编码的路径
    if project_directory:
        project_directory = unquote(project_directory)
    
    return _deepseek_summarize(content, project_directory)

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
            try:
                # 从输出中提取JSON部分（可能混合了其他日志信息）
                lines = stdout.strip().split('\n')
                json_line = None
                
                # 查找包含JSON的行
                for line in lines:
                    line = line.strip()
                    if line.startswith('{') and line.endswith('}'):
                        try:
                            # 验证是否为有效JSON
                            json.loads(line)
                            json_line = line
                            break
                        except json.JSONDecodeError:
                            continue
                
                if json_line:
                    # 解析用户反馈
                    feedback_data = json.loads(json_line)
                    user_feedback = feedback_data.get("result", "")
                    
                    print(f"DEBUG: 解析到的用户反馈: {user_feedback}", file=sys.stderr)
                    
                    # 直接返回用户反馈，不进行自动总结
                    return json.dumps({
                        "result": user_feedback
                    }, ensure_ascii=False)
                else:
                    # 没有找到有效的JSON行，说明是普通字符串输入
                    user_feedback = stdout.strip()
                    print(f"DEBUG: 用户直接输入字符串: {user_feedback}", file=sys.stderr)
                    
                    # 直接返回用户反馈，不进行自动总结
                    return json.dumps({
                        "result": user_feedback
                    }, ensure_ascii=False)
                    
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON解析失败: {e}, 原始内容: {stdout}", file=sys.stderr)
                # 如果解析失败，直接将内容作为用户反馈处理
                user_feedback = stdout.strip()
                
                return json.dumps({
                    "result": user_feedback
                }, ensure_ascii=False)
        else:
            return json.dumps({"result": ""}, ensure_ascii=False)
            
    except Exception as e:
        return json.dumps({"result": f"启动UI时出错: {str(e)}"}, ensure_ascii=False)

if __name__ == "__main__":
    mcp.run(transport="stdio")

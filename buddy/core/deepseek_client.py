"""DeepSeek API客户端模块"""
import json
import requests
from typing import Optional, Dict, Any, List, Generator
from dataclasses import dataclass
import time


@dataclass
class DeepSeekMessage:
    """DeepSeek消息数据类"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class DeepSeekResponse:
    """DeepSeek响应数据类"""
    content: str
    usage: Dict[str, int]
    model: str
    finish_reason: str


class DeepSeekClient:
    """DeepSeek API客户端"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com"):
        """
        初始化DeepSeek客户端
        
        Args:
            api_key: DeepSeek API密钥
            base_url: API基础URL，默认为官方地址
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def chat_completion(
        self,
        messages: List[DeepSeekMessage],
        model: str = "deepseek-chat",
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        system_prompt: Optional[str] = None
    ) -> DeepSeekResponse:
        """
        发送聊天完成请求
        
        Args:
            messages: 消息列表
            model: 使用的模型名称
            temperature: 温度参数，控制随机性
            max_tokens: 最大token数量
            stream: 是否使用流式响应
            system_prompt: 系统提示词，如果提供会自动添加到消息开头
            
        Returns:
            DeepSeek响应对象
        """
        # 构建消息列表
        formatted_messages = []
        
        # 如果提供了系统提示词，添加到消息开头
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # 添加用户消息
        for msg in messages:
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # 构建请求数据
        data = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 解析响应
            choice = result["choices"][0]
            return DeepSeekResponse(
                content=choice["message"]["content"],
                usage=result.get("usage", {}),
                model=result["model"],
                finish_reason=choice["finish_reason"]
            )
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"DeepSeek API请求失败: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"DeepSeek API响应格式错误: {str(e)}")
    
    def chat_completion_stream(
        self,
        messages: List[DeepSeekMessage],
        model: str = "deepseek-chat",
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        流式聊天完成请求
        
        Args:
            messages: 消息列表
            model: 使用的模型名称
            temperature: 温度参数
            max_tokens: 最大token数量
            system_prompt: 系统提示词
            
        Yields:
            流式响应的文本片段
        """
        # 构建消息列表
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        for msg in messages:
            formatted_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # 构建请求数据
        data = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "stream": True
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=data,
                stream=True,
                timeout=60
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # 移除 'data: ' 前缀
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.RequestException as e:
            raise Exception(f"DeepSeek流式API请求失败: {str(e)}")
    
    def simple_chat(
        self,
        user_input: str,
        system_prompt: Optional[str] = None,
        model: str = "deepseek-chat",
        temperature: float = 1.0
    ) -> str:
        """
        简单的聊天接口
        
        Args:
            user_input: 用户输入
            system_prompt: 系统提示词
            model: 模型名称
            temperature: 温度参数
            
        Returns:
            AI的回复内容
        """
        messages = [DeepSeekMessage(role="user", content=user_input)]
        response = self.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature
        )
        return response.content
    
    def test_connection(self) -> bool:
        """
        测试API连接是否正常
        
        Returns:
            连接是否成功
        """
        try:
            response = self.simple_chat("Hello", system_prompt="Please reply with 'Hi'")
            return bool(response)
        except Exception:
            return False


class DeepSeekService:
    """DeepSeek服务类，提供高级功能"""
    
    def __init__(self, client: DeepSeekClient):
        self.client = client
    
    def code_review(self, code: str, language: str = "python") -> str:
        """
        代码审查功能
        
        Args:
            code: 要审查的代码
            language: 编程语言
            
        Returns:
            代码审查结果
        """
        system_prompt = f"""你是一个专业的{language}代码审查专家。请仔细审查以下代码，并提供：
1. 代码质量评估
2. 潜在问题和bug
3. 性能优化建议
4. 最佳实践建议
5. 安全性考虑

请用中文回复，并保持专业和建设性的语调。"""
        
        user_input = f"请审查以下{language}代码：\n\n```{language}\n{code}\n```"
        
        return self.client.simple_chat(
            user_input=user_input,
            system_prompt=system_prompt
        )
    
    def code_explanation(self, code: str, language: str = "python") -> str:
        """
        代码解释功能
        
        Args:
            code: 要解释的代码
            language: 编程语言
            
        Returns:
            代码解释结果
        """
        system_prompt = f"""你是一个专业的{language}编程导师。请详细解释以下代码的功能、逻辑和实现方式。
请用中文回复，使用通俗易懂的语言，适合不同水平的开发者理解。"""
        
        user_input = f"请解释以下{language}代码：\n\n```{language}\n{code}\n```"
        
        return self.client.simple_chat(
            user_input=user_input,
            system_prompt=system_prompt
        )
    
    def code_generation(self, requirement: str, language: str = "python") -> str:
        """
        代码生成功能
        
        Args:
            requirement: 需求描述
            language: 目标编程语言
            
        Returns:
            生成的代码
        """
        system_prompt = f"""你是一个专业的{language}开发专家。请根据用户需求生成高质量的{language}代码。
要求：
1. 代码要规范、清晰、可读性强
2. 包含必要的注释
3. 遵循{language}的最佳实践
4. 考虑错误处理和边界情况
5. 如果需要，提供使用示例

请用中文注释，代码部分使用标准的{language}语法。"""
        
        user_input = f"请生成{language}代码来实现以下需求：\n\n{requirement}"
        
        return self.client.simple_chat(
            user_input=user_input,
            system_prompt=system_prompt
        )
    
    def bug_fix(self, code: str, error_message: str, language: str = "python") -> str:
        """
        Bug修复功能
        
        Args:
            code: 有问题的代码
            error_message: 错误信息
            language: 编程语言
            
        Returns:
            修复建议和修复后的代码
        """
        system_prompt = f"""你是一个专业的{language}调试专家。请分析代码中的问题并提供修复方案。
请提供：
1. 问题分析
2. 修复方案
3. 修复后的完整代码
4. 预防类似问题的建议

请用中文回复。"""
        
        user_input = f"""以下{language}代码出现了错误：

错误信息：
{error_message}

代码：
```{language}
{code}
```

请帮助分析和修复这个问题。"""
        
        return self.client.simple_chat(
            user_input=user_input,
            system_prompt=system_prompt
        ) 
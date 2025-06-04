"""提示词管理器模块"""
import os
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class PromptManager:
    """提示词管理器，负责加载和管理各种提示词文件"""
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        初始化提示词管理器
        
        Args:
            prompts_dir: 提示词目录路径，默认为buddy/prompts
        """
        if prompts_dir is None:
            # 默认使用buddy/prompts目录
            current_dir = Path(__file__).parent
            self.prompts_dir = current_dir.parent / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
        
        # 提示词缓存
        self._cache: Dict[str, str] = {}
    
    def load_prompt(self, prompt_name: str, use_cache: bool = True) -> Optional[str]:
        """
        加载指定的提示词文件
        
        Args:
            prompt_name: 提示词文件名（不包含.md扩展名）
            use_cache: 是否使用缓存
            
        Returns:
            提示词内容，如果文件不存在返回None
        """
        # 检查缓存
        if use_cache and prompt_name in self._cache:
            return self._cache[prompt_name]
        
        # 构建文件路径
        prompt_file = self.prompts_dir / f"{prompt_name}.md"
        
        try:
            if not prompt_file.exists():
                logger.warning(f"提示词文件不存在: {prompt_file}")
                return None
            
            # 读取文件内容
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 存储到缓存
            if use_cache:
                self._cache[prompt_name] = content
            
            logger.debug(f"成功加载提示词: {prompt_name}")
            return content
            
        except Exception as e:
            logger.error(f"加载提示词文件失败 {prompt_file}: {e}")
            return None
    
    def get_deepseek_prompt(self) -> str:
        """
        获取DeepSeek需求总结提示词
        
        Returns:
            DeepSeek提示词内容，如果加载失败返回默认提示词
        """
        prompt = self.load_prompt("deepseek")
        
        if prompt is None:
            # 返回默认提示词作为后备
            logger.warning("使用默认DeepSeek提示词")
            return self._get_default_deepseek_prompt()
        
        return prompt
    
    def _get_default_deepseek_prompt(self) -> str:
        """返回默认的DeepSeek提示词"""
        return """你是一个专业的内容总结助手。请对用户提供的内容进行简洁、准确的总结。
总结要求：
1. 提取核心要点
2. 保持逻辑清晰
3. 语言简洁明了
4. 突出重要信息
请用中文回复。"""
    
    def refresh_cache(self):
        """清空缓存，强制重新加载提示词"""
        self._cache.clear()
        logger.info("提示词缓存已清空")
    
    def list_available_prompts(self) -> list[str]:
        """
        列出所有可用的提示词文件
        
        Returns:
            提示词文件名列表（不包含.md扩展名）
        """
        try:
            if not self.prompts_dir.exists():
                return []
            
            prompt_files = []
            for file_path in self.prompts_dir.glob("*.md"):
                prompt_files.append(file_path.stem)
            
            return sorted(prompt_files)
            
        except Exception as e:
            logger.error(f"列出提示词文件失败: {e}")
            return []


# 全局提示词管理器实例
_global_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager() -> PromptManager:
    """获取全局提示词管理器实例"""
    global _global_prompt_manager
    if _global_prompt_manager is None:
        _global_prompt_manager = PromptManager()
    return _global_prompt_manager


def get_deepseek_prompt() -> str:
    """便捷函数：获取DeepSeek提示词"""
    return get_prompt_manager().get_deepseek_prompt() 
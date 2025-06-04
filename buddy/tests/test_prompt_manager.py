"""提示词管理器测试模块"""
import pytest
import tempfile
import os
from pathlib import Path
from buddy.core.prompt_manager import PromptManager, get_prompt_manager, get_deepseek_prompt


class TestPromptManager:
    """提示词管理器测试类"""
    
    def test_load_existing_prompt(self):
        """测试加载存在的提示词文件"""
        # 创建临时目录和文件
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir)
            test_file = prompts_dir / "test.md"
            test_content = "这是一个测试提示词"
            
            # 写入测试内容
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # 创建提示词管理器
            manager = PromptManager(prompts_dir=str(prompts_dir))
            
            # 测试加载
            result = manager.load_prompt("test")
            assert result == test_content
    
    def test_load_nonexistent_prompt(self):
        """测试加载不存在的提示词文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = PromptManager(prompts_dir=temp_dir)
            result = manager.load_prompt("nonexistent")
            assert result is None
    
    def test_cache_functionality(self):
        """测试缓存功能"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir)
            test_file = prompts_dir / "cache_test.md"
            original_content = "原始内容"
            modified_content = "修改后的内容"
            
            # 写入原始内容
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            manager = PromptManager(prompts_dir=str(prompts_dir))
            
            # 第一次加载（应该读取文件并缓存）
            result1 = manager.load_prompt("cache_test", use_cache=True)
            assert result1 == original_content
            
            # 修改文件内容
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            # 第二次加载（应该使用缓存，不读取文件）
            result2 = manager.load_prompt("cache_test", use_cache=True)
            assert result2 == original_content  # 应该是缓存的内容
            
            # 不使用缓存的加载（应该读取新内容）
            result3 = manager.load_prompt("cache_test", use_cache=False)
            assert result3 == modified_content
    
    def test_refresh_cache(self):
        """测试刷新缓存功能"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir)
            test_file = prompts_dir / "refresh_test.md"
            original_content = "原始内容"
            modified_content = "修改后的内容"
            
            # 写入原始内容并加载
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            manager = PromptManager(prompts_dir=str(prompts_dir))
            result1 = manager.load_prompt("refresh_test")
            assert result1 == original_content
            
            # 修改文件内容
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            # 刷新缓存
            manager.refresh_cache()
            
            # 重新加载（应该读取新内容）
            result2 = manager.load_prompt("refresh_test")
            assert result2 == modified_content
    
    def test_list_available_prompts(self):
        """测试列出可用提示词"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir)
            
            # 创建几个测试文件
            (prompts_dir / "prompt1.md").write_text("内容1", encoding='utf-8')
            (prompts_dir / "prompt2.md").write_text("内容2", encoding='utf-8')
            (prompts_dir / "not_md.txt").write_text("非MD文件", encoding='utf-8')
            
            manager = PromptManager(prompts_dir=str(prompts_dir))
            prompts = manager.list_available_prompts()
            
            assert sorted(prompts) == ["prompt1", "prompt2"]
    
    def test_get_deepseek_prompt_with_file(self):
        """测试通过文件获取DeepSeek提示词"""
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir)
            deepseek_file = prompts_dir / "deepseek.md"
            test_content = "自定义DeepSeek提示词"
            
            # 写入测试内容
            with open(deepseek_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            manager = PromptManager(prompts_dir=str(prompts_dir))
            result = manager.get_deepseek_prompt()
            
            assert result == test_content
    
    def test_get_deepseek_prompt_fallback(self):
        """测试DeepSeek提示词的后备机制"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 空目录，没有deepseek.md文件
            manager = PromptManager(prompts_dir=temp_dir)
            result = manager.get_deepseek_prompt()
            
            # 应该返回默认提示词
            assert "专业的内容总结助手" in result


def test_global_prompt_manager():
    """测试全局提示词管理器"""
    manager1 = get_prompt_manager()
    manager2 = get_prompt_manager()
    
    # 应该是同一个实例
    assert manager1 is manager2


def test_global_deepseek_prompt():
    """测试全局DeepSeek提示词获取函数"""
    prompt = get_deepseek_prompt()
    
    # 应该能获取到提示词（无论是从文件还是默认值）
    assert prompt is not None
    assert len(prompt) > 0
    assert isinstance(prompt, str) 
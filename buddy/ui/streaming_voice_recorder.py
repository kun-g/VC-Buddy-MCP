import os
import tempfile
import threading
import time
import wave
import io
from pathlib import Path
from typing import Optional, List, Set

import pyaudio
from PySide6.QtCore import QObject, Signal, QTimer

# 导入配置管理器和统计功能
try:
    from .config import ConfigManager
    from ..core.analytics import track_voice_action
except ImportError:
    # 如果作为脚本直接运行，需要添加路径
    import sys
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir.parent))  # 添加buddy目录到路径
    from ui.config import ConfigManager
    from core.analytics import track_voice_action

# 尝试导入OpenAI客户端
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not available. Voice transcription will be disabled.")


class StreamingVoiceRecorder(QObject):
    """流式语音录制器 - 支持实时语音识别和自定义结束语"""
    
    # 信号定义
    recording_started = Signal()
    recording_stopped = Signal()
    transcription_chunk_ready = Signal(str)  # 实时转写结果片段
    final_transcription_ready = Signal(str)  # 最终完整转写结果
    error_occurred = Signal(str)  # 错误信息
    stop_command_detected = Signal(str)  # 检测到停止命令
    send_command_detected = Signal(str)  # 检测到发送命令
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        super().__init__()
        
        # 配置管理器
        self.config_manager = config_manager
        
        # 录音参数
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        
        # 流式处理参数
        self.chunk_duration = 2.0  # 每个音频块的时长（秒）
        self.chunk_frames = int(self.sample_rate * self.chunk_duration)
        
        # 录音状态
        self.is_recording = False
        self.audio_data = []
        self.audio_stream = None
        self.pyaudio_instance = None
        
        # 流式转写相关
        self.current_chunk_data = []
        self.transcription_buffer = ""
        self.processing_thread = None
        
        # 自定义命令配置
        self.stop_commands = self._load_stop_commands()
        self.send_commands = self._load_send_commands()
        
        # 初始化OpenAI客户端
        self.openai_client = None
        self._init_openai_client()
        
        # 创建处理定时器
        self.process_timer = QTimer()
        self.process_timer.timeout.connect(self._process_audio_chunk)
        
    def _load_stop_commands(self) -> Set[str]:
        """加载停止录音的命令"""
        default_commands = {
            "我说完了", "说完了", "结束", "停止录音", "停止", 
            "finish", "done", "stop", "end"
        }
        
        if self.config_manager:
            custom_commands = self.config_manager.get("voice.stop_commands", [])
            if custom_commands:
                default_commands.update(custom_commands)
        
        return default_commands
    
    def _load_send_commands(self) -> Set[str]:
        """加载直接发送的命令"""
        default_commands = {
            "开工吧", "发送", "提交", "执行", "开始干活", "开始工作",
            "send", "submit", "go", "execute", "let's go"
        }
        
        if self.config_manager:
            custom_commands = self.config_manager.get("voice.send_commands", [])
            if custom_commands:
                default_commands.update(custom_commands)
        
        return default_commands
    
    def _init_openai_client(self):
        """初始化OpenAI客户端"""
        if not OPENAI_AVAILABLE:
            return
        
        try:
            if self.config_manager:
                api_key = self.config_manager.get("openai.api_key")
                api_url = self.config_manager.get("openai.api_url", "https://api.openai.com/v1")
            else:
                # 从环境变量获取
                api_key = os.getenv("OPENAI_API_KEY")
                api_url = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1")
            
            if api_key:
                # 确保API URL以/v1结尾
                if api_url and not api_url.endswith('/v1'):
                    if not api_url.endswith('/'):
                        api_url += '/v1'
                    else:
                        api_url += 'v1'
                
                self.openai_client = OpenAI(
                    api_key=api_key,
                    base_url=api_url
                )
                print(f"OpenAI client initialized for streaming with URL: {api_url}")
            else:
                print("Warning: OpenAI API key not found. Streaming voice transcription will be disabled.")
                
        except Exception as e:
            print(f"Error initializing OpenAI client for streaming: {e}")
            self.openai_client = None
    
    def start_recording(self):
        """开始流式录音"""
        if self.is_recording:
            return
        
        print("DEBUG: 开始初始化流式录音...")
        
        try:
            # 安全地初始化PyAudio
            self._safe_init_pyaudio()
            
            # 创建音频流
            self.audio_stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            print("DEBUG: 音频流创建成功")
            
            # 重置状态
            self.audio_data = []
            self.current_chunk_data = []
            self.transcription_buffer = ""
            self.is_recording = True
            
            # 发送录音开始信号
            self.recording_started.emit()
            print("DEBUG: 录音开始信号已发送")
            
            # 启动录音线程
            recording_thread = threading.Thread(target=self._record_audio_stream, daemon=True)
            recording_thread.start()
            print("DEBUG: 录音线程已启动")
            
            # 启动处理定时器
            self.process_timer.start(int(self.chunk_duration * 1000))  # 转换为毫秒
            print(f"DEBUG: 处理定时器已启动，间隔: {self.chunk_duration}秒")
            
            track_voice_action("streaming_recording_started")
            print("DEBUG: 流式录音启动完成")
            
        except Exception as e:
            print(f"DEBUG: 启动流式录音时发生异常: {e}")
            print(f"DEBUG: 异常类型: {type(e)}")
            import traceback
            traceback.print_exc()
            self._safe_cleanup_resources()
            self.error_occurred.emit(f"开始流式录音失败: {str(e)}")
    
    def _safe_init_pyaudio(self):
        """安全地初始化PyAudio"""
        try:
            if self.pyaudio_instance:
                self._safe_cleanup_resources()
            
            self.pyaudio_instance = pyaudio.PyAudio()
            print(f"DEBUG: PyAudio初始化成功，版本: {pyaudio.get_portaudio_version_text()}")
            
            # 检查可用的音频设备
            device_count = self.pyaudio_instance.get_device_count()
            print(f"DEBUG: 检测到 {device_count} 个音频设备")
            
            # 找到默认输入设备
            default_input = self.pyaudio_instance.get_default_input_device_info()
            print(f"DEBUG: 默认输入设备: {default_input['name']}")
            
        except Exception as e:
            print(f"DEBUG: PyAudio初始化失败: {e}")
            import traceback
            traceback.print_exc()
            self._safe_cleanup_resources()
            raise
    
    def _safe_cleanup_resources(self):
        """安全地清理资源"""
        try:
            # 停止处理定时器
            if hasattr(self, 'process_timer') and self.process_timer:
                try:
                    self.process_timer.stop()
                    print("DEBUG: 处理定时器已停止")
                except:
                    pass
            
            # 停止音频流
            if self.audio_stream:
                try:
                    if hasattr(self.audio_stream, '_is_output') and not self.audio_stream._is_output:
                        self.audio_stream.stop_stream()
                except:
                    pass
                try:
                    self.audio_stream.close()
                except:
                    pass
                finally:
                    self.audio_stream = None
                    print("DEBUG: 音频流已关闭")
            
            # 终止PyAudio
            if self.pyaudio_instance:
                try:
                    self.pyaudio_instance.terminate()
                except:
                    pass
                finally:
                    self.pyaudio_instance = None
                    print("DEBUG: PyAudio实例已终止")
            
            print("DEBUG: 资源清理完成")
        except Exception as e:
            print(f"DEBUG: 清理资源时出错: {e}")

    def _record_audio_stream(self):
        """录音线程函数"""
        print("DEBUG: 录音线程开始运行")
        self._recording_active = True
        
        try:
            while self.is_recording and self.audio_stream:
                try:
                    data = self.audio_stream.read(self.chunk_size)
                    if data:
                        self.audio_data.append(data)
                        self.current_chunk_data.append(data)
                    
                    # 每1000个chunk打印一次状态
                    if len(self.audio_data) % 1000 == 0:
                        print(f"DEBUG: 已录制 {len(self.audio_data)} 个音频块")
                        
                except OSError as e:
                    # 处理缓冲区溢出等PyAudio错误
                    if "Input overflowed" in str(e) or "overflow" in str(e).lower():
                        print("DEBUG: 音频缓冲区溢出，继续录音")
                        time.sleep(0.01)
                        continue
                    else:
                        print(f"DEBUG: PyAudio OSError: {e}")
                        time.sleep(0.01)
                except Exception as e:
                    print(f"DEBUG: 录音数据读取失败: {e}")
                    # 不立即退出，尝试继续录音
                    time.sleep(0.01)
                    
        except Exception as e:
            print(f"DEBUG: 录音线程异常: {e}")
            print(f"DEBUG: 异常类型: {type(e)}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"录音过程中出错: {str(e)}")
        finally:
            self._recording_active = False
            print("DEBUG: 录音线程结束")
    
    def _process_audio_chunk(self):
        """定时处理音频块"""
        if not self.current_chunk_data or not self.is_recording:
            return
        
        print(f"DEBUG: 开始处理音频块，当前块大小: {len(self.current_chunk_data)}")
        
        # 复制当前块数据
        chunk_data = self.current_chunk_data.copy()
        self.current_chunk_data = []
        
        # 在新线程中处理转写
        processing_thread = threading.Thread(
            target=self._transcribe_chunk, 
            args=(chunk_data,), 
            daemon=True
        )
        processing_thread.start()
        print("DEBUG: 转写线程已启动")
    
    def _process_final_chunk(self):
        """处理最后一个音频块"""
        if not self.current_chunk_data:
            return
        
        chunk_data = self.current_chunk_data.copy()
        self.current_chunk_data = []
        
        # 同步处理最后一块
        self._transcribe_chunk(chunk_data, is_final=True)
    
    def _transcribe_chunk(self, chunk_data: List[bytes], is_final: bool = False):
        """转写音频块"""
        if not self.openai_client or not chunk_data:
            print("DEBUG: 转写跳过 - 没有OpenAI客户端或音频数据")
            return
        
        print(f"DEBUG: 开始转写音频块，数据块数量: {len(chunk_data)}")
        
        audio_buffer = None
        try:
            # 将音频数据转换为WAV格式
            audio_buffer = io.BytesIO()
            with wave.open(audio_buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16位音频 = 2字节
                wf.setframerate(self.sample_rate)
                
                # 合并音频数据
                combined_data = b''.join(chunk_data)
                if len(combined_data) == 0:
                    print("DEBUG: 音频数据为空，跳过转写")
                    return
                
                wf.writeframes(combined_data)
            
            audio_buffer.seek(0)
            audio_size = len(audio_buffer.getvalue())
            print(f"DEBUG: 音频缓冲区大小: {audio_size} 字节")
            
            # 验证音频数据最小长度和质量
            if audio_size < 1000:  # 少于1KB的音频数据可能无法转写
                print("DEBUG: 音频数据太小，跳过转写")
                return
            
            # 检查音频质量 - 计算音频能量
            audio_data = audio_buffer.getvalue()
            if self._is_audio_too_quiet(audio_data):
                print("DEBUG: 音频太安静，可能是静音，跳过转写")
                return
            
            # 给BytesIO对象设置名称，避免API调用问题
            audio_buffer.name = "chunk.wav"
            
            # 调用OpenAI Whisper API
            print("DEBUG: 开始调用OpenAI API...")
            response = None
            try:
                response = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_buffer,
                    response_format="text",
                    language="zh",  # 指定中文
                    temperature=0.0,  # 降低随机性，减少幻觉
                    prompt=""  # 空提示，避免引导生成特定内容
                )
                print(f"DEBUG: API调用成功，响应类型: {type(response)}")
                print(f"DEBUG: API响应内容: {response}")
            except Exception as api_error:
                print(f"DEBUG: API调用失败: {api_error}")
                import traceback
                traceback.print_exc()
                
                # 不在流式转写中显示每个块的错误，只记录日志
                error_str = str(api_error).lower()
                if "not found" in error_str or "404" in error_str:
                    print("DEBUG: API不支持Whisper")
                elif "401" in error_str or "unauthorized" in error_str:
                    print("DEBUG: API认证失败")
                elif "connection" in error_str or "timeout" in error_str:
                    print("DEBUG: 网络连接问题")
                else:
                    print(f"DEBUG: 其他API错误: {api_error}")
                return
            
            # 处理响应
            transcription = ""
            try:
                if isinstance(response, str):
                    transcription = response.strip()
                elif hasattr(response, 'text'):
                    transcription = response.text.strip()
                elif isinstance(response, dict) and 'text' in response:
                    transcription = response['text'].strip()
                else:
                    transcription = str(response).strip()
                    
            except Exception as parse_error:
                print(f"DEBUG: 解析响应失败: {parse_error}")
                return
            
            print(f"DEBUG: 转写结果: '{transcription}'")
            
            if transcription:
                # 添加到缓冲区
                self.transcription_buffer += " " + transcription
                print(f"DEBUG: 当前缓冲区内容: '{self.transcription_buffer}'")
                
                # 发送实时转写片段
                try:
                    self.transcription_chunk_ready.emit(transcription)
                    print("DEBUG: 转写片段信号已发送")
                except Exception as signal_error:
                    print(f"DEBUG: 发送信号失败: {signal_error}")
                
                # 检查是否包含停止或发送命令
                try:
                    self._check_commands(transcription)
                except Exception as cmd_error:
                    print(f"DEBUG: 命令检查失败: {cmd_error}")
            else:
                print("DEBUG: 转写结果为空")
                
        except Exception as e:
            print(f"DEBUG: 转写音频块时发生未预期异常: {e}")
            import traceback
            traceback.print_exc()
            # 在流式转写中，单个块的错误不应该终止整个录音过程
            # self.error_occurred.emit(f"转写音频块时出错: {str(e)}")
        finally:
            # 确保清理资源
            if audio_buffer:
                try:
                    audio_buffer.close()
                except:
                    pass
    
    def _check_commands(self, text: str):
        """检查文本中是否包含命令"""
        text_lower = text.lower().strip()
        print(f"DEBUG: 检查命令，文本: '{text_lower}'")
        
        # 检查停止命令
        for cmd in self.stop_commands:
            if cmd.lower() in text_lower:
                print(f"DEBUG: 检测到停止命令: '{cmd}'")
                self.stop_command_detected.emit(cmd)
                # 自动停止录音
                if self.is_recording:
                    self.stop_recording()
                return
        
        # 检查发送命令
        for cmd in self.send_commands:
            if cmd.lower() in text_lower:
                print(f"DEBUG: 检测到发送命令: '{cmd}'")
                self.send_command_detected.emit(cmd)
                # 自动停止录音并发送
                if self.is_recording:
                    self.stop_recording()
                return
        
        print("DEBUG: 未检测到任何命令")
    
    def update_stop_commands(self, commands: List[str]):
        """更新停止命令列表"""
        self.stop_commands = set(commands)
        if self.config_manager:
            self.config_manager.set("voice.stop_commands", commands)
    
    def update_send_commands(self, commands: List[str]):
        """更新发送命令列表"""
        self.send_commands = set(commands)
        if self.config_manager:
            self.config_manager.set("voice.send_commands", commands)
    
    def get_current_transcription(self) -> str:
        """获取当前转写结果"""
        return self.transcription_buffer.strip()
    
    def clear_transcription_buffer(self):
        """清空转写缓冲区"""
        self.transcription_buffer = ""
    
    def cleanup(self):
        """清理资源"""
        if self.is_recording:
            self.stop_recording()
        
        # 停止定时器
        if self.process_timer:
            self.process_timer.stop()
    
    def stop_recording(self):
        """停止录音"""
        if not self.is_recording:
            return
        
        print("DEBUG: 开始停止流式录音...")
        self.is_recording = False
        
        try:
            # 停止处理定时器
            if self.process_timer:
                self.process_timer.stop()
                print("DEBUG: 处理定时器已停止")
            
            # 处理最后一个音频块
            if self.current_chunk_data:
                print("DEBUG: 处理最后一个音频块")
                self._process_final_chunk()
            
            # 停止音频流
            if self.audio_stream:
                try:
                    self.audio_stream.stop_stream()
                    self.audio_stream.close()
                    print("DEBUG: 音频流已关闭")
                except Exception as e:
                    print(f"DEBUG: 关闭音频流时出错: {e}")
                finally:
                    self.audio_stream = None
            
            # 终止PyAudio
            if self.pyaudio_instance:
                try:
                    self.pyaudio_instance.terminate()
                    print("DEBUG: PyAudio实例已终止")
                except Exception as e:
                    print(f"DEBUG: 终止PyAudio时出错: {e}")
                finally:
                    self.pyaudio_instance = None
            
            # 发送录音停止信号
            try:
                self.recording_stopped.emit()
                print("DEBUG: 录音停止信号已发送")
            except Exception as e:
                print(f"DEBUG: 发送停止信号时出错: {e}")
            
            # 发送最终转写结果
            if self.transcription_buffer.strip():
                try:
                    self.final_transcription_ready.emit(self.transcription_buffer.strip())
                    print("DEBUG: 最终转写结果已发送")
                except Exception as e:
                    print(f"DEBUG: 发送最终结果时出错: {e}")
            
            track_voice_action("streaming_recording_stopped")
            print("DEBUG: 流式录音停止完成")
            
        except Exception as e:
            print(f"DEBUG: 停止录音时发生未预期异常: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.error_occurred.emit(f"停止录音失败: {str(e)}")
            except:
                pass
    
    def _recording_active(self):
        """检查录音线程是否正在运行"""
        return hasattr(self, '_recording_active') and self._recording_active 

    def _is_audio_too_quiet(self, audio_data: bytes) -> bool:
        """检查音频是否太安静"""
        import struct
        
        try:
            # 跳过WAV头部（44字节）
            if len(audio_data) < 44:
                return True
            
            audio_samples = audio_data[44:]  # 跳过WAV头部
            
            # 将字节数据转换为16位整数数组
            if len(audio_samples) < 2:
                return True
                
            samples = struct.unpack(f'<{len(audio_samples)//2}h', audio_samples)
            
            # 计算平均绝对值（简单的能量指标）
            avg_amplitude = sum(abs(sample) for sample in samples) / len(samples)
            
            # 设置阈值，低于此值认为是静音或太安静
            silence_threshold = 200  # 可以根据实际情况调整
            
            is_quiet = avg_amplitude < silence_threshold
            if is_quiet:
                print(f"DEBUG: 音频能量太低: {avg_amplitude:.2f} < {silence_threshold}")
            else:
                print(f"DEBUG: 音频能量正常: {avg_amplitude:.2f}")
                
            return is_quiet
            
        except Exception as e:
            print(f"DEBUG: 音频质量检测失败: {e}")
            # 如果检测失败，不跳过转写
            return False
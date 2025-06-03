import os
import tempfile
import threading
import time
import wave
from pathlib import Path
from typing import Optional, Callable

import pyaudio
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QPushButton, QMessageBox

# 导入配置管理器和统计功能
try:
    from .config import ConfigManager
    from ..core.analytics import track_voice_action, track_button_clicked
except ImportError:
    # 如果作为脚本直接运行，需要添加路径
    import sys
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir.parent))  # 添加buddy目录到路径
    from ui.config import ConfigManager
    from core.analytics import track_voice_action, track_button_clicked

# 尝试导入OpenAI客户端
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not available. Voice transcription will be disabled.")


class VoiceRecorder(QObject):
    """语音录制器"""
    
    # 信号定义
    recording_started = Signal()
    recording_stopped = Signal()
    transcription_ready = Signal(str)  # 转写结果
    error_occurred = Signal(str)  # 错误信息
    audio_saved = Signal(str)  # 音频文件保存完成，传递文件路径
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        super().__init__()
        
        # 配置管理器
        self.config_manager = config_manager
        
        # 录音参数
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        
        # 录音状态
        self.is_recording = False
        self.audio_data = []
        self.audio_stream = None
        self.pyaudio_instance = None
        
        # 最后录制的音频文件路径
        self.last_audio_file = None
        
        # 延迟初始化OpenAI客户端
        self.openai_client = None
        self._openai_initialized = False
    
    def _init_openai_client(self):
        """延迟初始化OpenAI客户端"""
        if self._openai_initialized or not OPENAI_AVAILABLE:
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
                # 确保API URL以/v1结尾（某些第三方服务器需要）
                if api_url and not api_url.endswith('/v1'):
                    if not api_url.endswith('/'):
                        api_url += '/v1'
                    else:
                        api_url += 'v1'
                
                self.openai_client = OpenAI(
                    api_key=api_key,
                    base_url=api_url
                )
                print(f"OpenAI client initialized with URL: {api_url}")
            else:
                print("Warning: OpenAI API key not found. Voice transcription will be disabled.")
                
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}")
            self.openai_client = None
        finally:
            self._openai_initialized = True
    
    def update_api_config(self, api_key: str, api_url: str = None):
        """更新API配置"""
        try:
            # 重置初始化标志，下次转写时重新初始化
            self._openai_initialized = False
            self.openai_client = None
            
            # 如果立即需要初始化，可以调用初始化方法
            if api_key:  # 只有在提供了API key时才初始化
                self._init_openai_client()
        except Exception as e:
            self.error_occurred.emit(f"更新API配置失败: {str(e)}")
    
    def update_api_key(self, api_key: str):
        """更新API密钥"""
        self.update_api_config(api_key)
    
    def start_recording(self):
        """开始录音"""
        if self.is_recording:
            return
        
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
            
            # 重置音频数据
            self.audio_data = []
            self.is_recording = True
            
            # 发送录音开始信号
            self.recording_started.emit()
            
            # 在新线程中录音，设置为守护线程
            recording_thread = threading.Thread(target=self._record_audio, daemon=True)
            recording_thread.start()
            
        except Exception as e:
            print(f"DEBUG: 开始录音失败: {e}")
            import traceback
            traceback.print_exc()
            self._safe_cleanup_resources()
            self.error_occurred.emit(f"开始录音失败: {str(e)}")
    
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
            self._safe_cleanup_resources()
            raise
    
    def _safe_cleanup_resources(self):
        """安全地清理资源"""
        try:
            # 停止音频流
            if self.audio_stream:
                try:
                    if not self.audio_stream._is_output:  # 检查是否为输入流
                        self.audio_stream.stop_stream()
                except:
                    pass
                try:
                    self.audio_stream.close()
                except:
                    pass
                finally:
                    self.audio_stream = None
            
            # 终止PyAudio
            if self.pyaudio_instance:
                try:
                    self.pyaudio_instance.terminate()
                except:
                    pass
                finally:
                    self.pyaudio_instance = None
            
            print("DEBUG: 资源清理完成")
        except Exception as e:
            print(f"DEBUG: 清理资源时出错: {e}")

    def stop_recording(self):
        """停止录音"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        try:
            # 等待录音线程结束（最多等待2秒）
            start_time = time.time()
            while hasattr(self, '_recording_active') and self._recording_active:
                if time.time() - start_time > 2.0:
                    print("DEBUG: 录音线程超时，强制停止")
                    break
                time.sleep(0.1)
            
            # 安全地清理资源
            self._safe_cleanup_resources()
            
            # 发送录音停止信号
            self.recording_stopped.emit()
            
            # 保存音频文件
            if self.audio_data:
                self._save_audio_file()
            else:
                self.error_occurred.emit("没有录制到音频数据")
            
        except Exception as e:
            print(f"DEBUG: 停止录音失败: {e}")
            import traceback
            traceback.print_exc()
            self._safe_cleanup_resources()
            self.error_occurred.emit(f"停止录音失败: {str(e)}")

    def _record_audio(self):
        """录音线程函数"""
        self._recording_active = True
        try:
            while self.is_recording and self.audio_stream:
                try:
                    data = self.audio_stream.read(self.chunk_size)
                    if data:
                        self.audio_data.append(data)
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
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"录音过程中出错: {str(e)}")
        finally:
            self._recording_active = False
            print("DEBUG: 录音线程结束")
    
    def _save_audio_file(self):
        """保存音频文件"""
        if not self.audio_data:
            self.error_occurred.emit("没有录音数据可保存")
            return
        
        try:
            # 创建临时文件
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file.close()
            
            # 保存为WAV文件
            with wave.open(temp_file.name, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16位音频 = 2字节
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.audio_data))
            
            self.last_audio_file = temp_file.name
            self.audio_saved.emit(temp_file.name)
            
            # 添加统计
            track_voice_action("audio_saved")
            
            # 自动开始转写
            self._start_transcription()
            
        except Exception as e:
            self.error_occurred.emit(f"保存音频文件失败: {str(e)}")
    
    def play_last_recording(self):
        """播放最后录制的音频"""
        if not self.last_audio_file or not os.path.exists(self.last_audio_file):
            self.error_occurred.emit("没有找到录音文件")
            return
        
        track_voice_action("playback_started")
        
        # 在新线程中播放音频，设置为守护线程
        play_thread = threading.Thread(target=self._play_audio_file, args=(self.last_audio_file,), daemon=True)
        play_thread.start()
    
    def _play_audio_file(self, file_path: str):
        """播放音频文件"""
        audio_output = None
        stream = None
        
        try:
            # 读取音频文件
            with wave.open(file_path, 'rb') as wf:
                # 创建音频输出流
                audio_output = pyaudio.PyAudio()
                stream = audio_output.open(
                    format=audio_output.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                # 播放音频数据
                chunk_size = 1024
                data = wf.readframes(chunk_size)
                while data:
                    stream.write(data)
                    data = wf.readframes(chunk_size)
                
        except Exception as e:
            self.error_occurred.emit(f"播放音频失败: {str(e)}")
        finally:
            # 确保清理资源
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except:
                    pass
            if audio_output:
                try:
                    audio_output.terminate()
                except:
                    pass
    
    def _start_transcription(self):
        """开始转写音频"""
        # 延迟初始化OpenAI客户端
        if not self._openai_initialized:
            self._init_openai_client()
        
        if not self.openai_client:
            self.error_occurred.emit("OpenAI API 未配置，无法进行语音转写")
            return
        
        track_voice_action("transcription_started")
        
        # 在新线程中进行转写，设置为守护线程防止程序卡死
        transcription_thread = threading.Thread(target=self._transcribe_audio, daemon=True)
        transcription_thread.start()
    
    def _transcribe_audio(self):
        """转写音频"""
        try:
            if not self.last_audio_file or not os.path.exists(self.last_audio_file):
                self.error_occurred.emit("音频文件不存在，无法进行转写")
                return
            
            print(f"DEBUG: 开始转写音频文件: {self.last_audio_file}")
            print(f"DEBUG: 使用API URL: {self.openai_client.base_url}")
            
            # 验证音频文件完整性
            try:
                with wave.open(self.last_audio_file, 'rb') as test_wf:
                    frames = test_wf.getnframes()
                    if frames == 0:
                        self.error_occurred.emit("音频文件为空，无法进行转写")
                        return
                    print(f"DEBUG: 音频文件验证成功，帧数: {frames}")
            except Exception as e:
                self.error_occurred.emit(f"音频文件损坏或格式错误: {str(e)}")
                return
            
            # 调用 OpenAI Whisper API
            transcript = None
            try:
                with open(self.last_audio_file, 'rb') as audio_file:
                    print("DEBUG: 开始调用 OpenAI API...")
                    
                    # 创建一个新的文件对象，避免文件句柄问题
                    audio_data = audio_file.read()
                    
                    # 使用BytesIO创建临时文件对象
                    import io
                    audio_buffer = io.BytesIO(audio_data)
                    audio_buffer.name = "audio.wav"  # 给BytesIO对象一个名称
                    
                    transcript = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_buffer,
                        language="zh"  # 指定中文
                    )
                    print(f"DEBUG: API调用成功，响应类型: {type(transcript)}")
                    print(f"DEBUG: API响应内容: {transcript}")
                    
            except Exception as api_error:
                print(f"DEBUG: Whisper API调用异常: {api_error}")
                import traceback
                traceback.print_exc()
                
                # 检查是否是第三方API服务器不支持Whisper的问题
                error_str = str(api_error).lower()
                if "not found" in error_str or "404" in error_str:
                    self.error_occurred.emit(f"第三方API服务器不支持Whisper音频转写功能。\n请使用支持Whisper API的服务器或联系管理员。\n错误详情: {str(api_error)}")
                elif "401" in error_str or "unauthorized" in error_str:
                    self.error_occurred.emit(f"API密钥无效或权限不足: {str(api_error)}")
                elif "403" in error_str or "forbidden" in error_str:
                    self.error_occurred.emit(f"API访问被拒绝: {str(api_error)}")
                elif "connection" in error_str or "timeout" in error_str:
                    self.error_occurred.emit(f"网络连接问题: {str(api_error)}")
                elif "openai" in error_str:
                    self.error_occurred.emit(f"OpenAI客户端错误: {str(api_error)}")
                else:
                    self.error_occurred.emit(f"API调用失败: {str(api_error)}")
                
                track_voice_action("transcription_error")
                return
            
            # 处理不同格式的响应
            transcription_text = ""
            try:
                if hasattr(transcript, 'text'):
                    # 标准OpenAI API响应对象
                    transcription_text = transcript.text
                    print(f"DEBUG: 使用 .text 属性获取转写结果")
                elif isinstance(transcript, str):
                    # 某些API服务器可能直接返回字符串
                    transcription_text = transcript
                    print(f"DEBUG: API直接返回字符串")
                elif isinstance(transcript, dict) and 'text' in transcript:
                    # 字典格式响应
                    transcription_text = transcript['text']
                    print(f"DEBUG: 使用字典['text']获取转写结果")
                else:
                    # 检查是否是HTML响应（表示API调用错误）
                    transcript_str = str(transcript)
                    if '<html' in transcript_str.lower() or '<!doctype html' in transcript_str.lower():
                        self.error_occurred.emit("API返回HTML页面，可能是endpoint错误或API不支持Whisper格式")
                        return
                    else:
                        # 尝试转换为字符串
                        transcription_text = transcript_str
                        print(f"DEBUG: 转换为字符串: {transcription_text[:100]}...")
            except Exception as parse_error:
                print(f"DEBUG: 解析响应时出错: {parse_error}")
                self.error_occurred.emit(f"解析API响应失败: {str(parse_error)}")
                track_voice_action("transcription_parse_error")
                return
            
            print(f"DEBUG: 最终转写结果: {transcription_text}")
            
            # 发送转写结果
            if transcription_text and transcription_text.strip():
                self.transcription_ready.emit(transcription_text.strip())
                track_voice_action("transcription_completed")
                print("DEBUG: 转写结果已发送")
            else:
                self.error_occurred.emit("语音转写结果为空")
                track_voice_action("transcription_empty")
            
        except Exception as e:
            print(f"DEBUG: 转写过程发生未预期异常: {e}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(f"语音转写失败: {str(e)}")
            track_voice_action("transcription_unexpected_error")
        finally:
            # 确保清理临时资源
            try:
                if hasattr(self, 'last_audio_file') and self.last_audio_file:
                    print(f"DEBUG: 保留音频文件用于调试: {self.last_audio_file}")
                    # 暂时不删除文件，用于调试
                    # os.unlink(self.last_audio_file)
            except Exception:
                pass
    
    def cleanup(self):
        """清理临时文件"""
        if self.last_audio_file and os.path.exists(self.last_audio_file):
            try:
                os.unlink(self.last_audio_file)
            except Exception:
                pass  # 忽略删除文件的错误


class VoiceButton(QPushButton):
    """语音录制按钮"""
    
    def __init__(self, parent=None, config_manager: Optional[ConfigManager] = None):
        super().__init__("🎤", parent)
        self.setToolTip("点击开始录音，再次点击停止录音")
        self.setFixedSize(40, 40)
        
        # 创建录音器
        self.recorder = VoiceRecorder(config_manager)
        
        # 连接信号
        self.recorder.recording_started.connect(self._on_recording_started)
        self.recorder.recording_stopped.connect(self._on_recording_stopped)
        self.recorder.error_occurred.connect(self._on_error)
        
        # 连接按钮点击事件
        self.clicked.connect(self._toggle_recording)
        
        # 样式
        self.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #999;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton[recording="true"] {
                background-color: #ff4444;
                border-color: #cc0000;
                color: white;
            }
        """)
    
    def _toggle_recording(self):
        """切换录音状态"""
        if self.recorder.is_recording:
            track_voice_action("stop_recording")
            track_button_clicked("voice_stop", "voice_panel")
            self.recorder.stop_recording()
        else:
            track_voice_action("start_recording")
            track_button_clicked("voice_start", "voice_panel")
            self.recorder.start_recording()
    
    def _on_recording_started(self):
        """录音开始时的处理"""
        self.setText("⏹️")
        self.setToolTip("点击停止录音")
        self.setProperty("recording", "true")
        self.style().unpolish(self)
        self.style().polish(self)
    
    def _on_recording_stopped(self):
        """录音停止时的处理"""
        self.setText("🎤")
        self.setToolTip("点击开始录音，再次点击停止录音")
        self.setProperty("recording", "false")
        self.style().unpolish(self)
        self.style().polish(self)
    
    def _on_error(self, error_message: str):
        """错误处理"""
        track_voice_action("error")
        QMessageBox.warning(self, "语音录制错误", error_message)
        self._on_recording_stopped()  # 重置按钮状态
    
    def connect_transcription_ready(self, callback: Callable[[str], None]):
        """连接转写完成的回调函数"""
        self.recorder.transcription_ready.connect(callback)


class PlayButton(QPushButton):
    """播放录音按钮"""
    
    def __init__(self, voice_recorder: VoiceRecorder, parent=None):
        super().__init__("🔊", parent)
        self.setToolTip("播放最后录制的音频")
        self.setFixedSize(40, 40)
        self.setEnabled(False)  # 初始状态禁用
        
        self.voice_recorder = voice_recorder
        
        # 连接信号
        self.voice_recorder.audio_saved.connect(self._on_audio_saved)
        self.voice_recorder.error_occurred.connect(self._on_error)
        
        # 连接按钮点击事件
        self.clicked.connect(self._play_audio)
        
        # 样式
        self.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover:enabled {
                background-color: #e0e0e0;
                border-color: #999;
            }
            QPushButton:pressed:enabled {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                border-color: #ddd;
                color: #ccc;
            }
        """)
    
    def _play_audio(self):
        """播放音频"""
        track_voice_action("play_recording")
        track_button_clicked("voice_play", "voice_panel")
        self.voice_recorder.play_last_recording()
    
    def _on_audio_saved(self, file_path: str):
        """音频保存完成，启用播放按钮"""
        self.setEnabled(True)
        self.setToolTip("播放最后录制的音频")
    
    def _on_error(self, error_message: str):
        """错误处理"""
        if "播放音频失败" in error_message or "没有找到录音文件" in error_message:
            QMessageBox.warning(self, "播放错误", error_message) 
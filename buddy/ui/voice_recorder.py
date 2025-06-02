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
        
        # 初始化OpenAI客户端
        self.openai_client = None
        self._init_openai_client()
    
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
    
    def update_api_config(self, api_key: str, api_url: str = None):
        """更新API配置"""
        try:
            self.openai_client = OpenAI(
                api_key=api_key,
                base_url=api_url or "https://api.openai.com/v1"
            )
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
            # 初始化PyAudio
            self.pyaudio_instance = pyaudio.PyAudio()
            
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
            
            # 在新线程中录音
            recording_thread = threading.Thread(target=self._record_audio)
            recording_thread.start()
            
        except Exception as e:
            self.error_occurred.emit(f"开始录音失败: {str(e)}")
    
    def stop_recording(self):
        """停止录音"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        try:
            # 停止音频流
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
            
            # 终止PyAudio
            if self.pyaudio_instance:
                self.pyaudio_instance.terminate()
                self.pyaudio_instance = None
            
            # 发送录音停止信号
            self.recording_stopped.emit()
            
            # 保存音频文件
            self._save_audio_file()
            
        except Exception as e:
            self.error_occurred.emit(f"停止录音失败: {str(e)}")
    
    def _record_audio(self):
        """录音线程函数"""
        while self.is_recording and self.audio_stream:
            try:
                data = self.audio_stream.read(self.chunk_size, exception_on_overflow=False)
                self.audio_data.append(data)
            except Exception as e:
                self.error_occurred.emit(f"录音过程中出错: {str(e)}")
                break
    
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
                wf.setsampwidth(pyaudio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(self.audio_data))
            
            self.last_audio_file = temp_file.name
            self.audio_saved.emit(temp_file.name)
            
            # 自动开始转写
            self._start_transcription()
            
        except Exception as e:
            self.error_occurred.emit(f"保存音频文件失败: {str(e)}")
    
    def play_last_recording(self):
        """播放最后录制的音频"""
        if not self.last_audio_file or not os.path.exists(self.last_audio_file):
            self.error_occurred.emit("没有找到录音文件")
            return
        
        # 在新线程中播放音频
        play_thread = threading.Thread(target=self._play_audio_file, args=(self.last_audio_file,))
        play_thread.start()
    
    def _play_audio_file(self, file_path: str):
        """播放音频文件"""
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
                
                # 清理资源
                stream.stop_stream()
                stream.close()
                audio_output.terminate()
                
        except Exception as e:
            self.error_occurred.emit(f"播放音频失败: {str(e)}")
    
    def _start_transcription(self):
        """开始转写音频"""
        if not self.openai_client:
            self.error_occurred.emit("OpenAI API 未配置，无法进行语音转写")
            return
        
        # 在新线程中进行转写
        transcription_thread = threading.Thread(target=self._transcribe_audio)
        transcription_thread.start()
    
    def _transcribe_audio(self):
        """转写音频"""
        try:
            if not self.last_audio_file or not os.path.exists(self.last_audio_file):
                self.error_occurred.emit("音频文件不存在，无法进行转写")
                return
            
            # 调用 OpenAI Whisper API
            with open(self.last_audio_file, 'rb') as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="zh"  # 指定中文
                )
            
            # 发送转写结果
            self.transcription_ready.emit(transcript.text)
            
        except Exception as e:
            self.error_occurred.emit(f"语音转写失败: {str(e)}")
    
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
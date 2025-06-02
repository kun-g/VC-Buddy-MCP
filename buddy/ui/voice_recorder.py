import os
import tempfile
import threading
import wave
from typing import Optional, Callable
import pyaudio
import openai
from PySide6.QtCore import QObject, Signal, QThread
from PySide6.QtWidgets import QPushButton, QMessageBox


class VoiceRecorder(QObject):
    """语音录制器"""
    
    # 信号定义
    recording_started = Signal()
    recording_stopped = Signal()
    transcription_ready = Signal(str)  # 转写结果
    error_occurred = Signal(str)  # 错误信息
    audio_saved = Signal(str)  # 音频文件保存完成，传递文件路径
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.audio_data = []
        self.stream = None
        self.audio = None
        self.last_audio_file = None  # 保存最后录制的音频文件路径
        
        # 音频参数
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        
        # OpenAI 客户端
        self.openai_client = None
        self._init_openai_client()
    
    def _init_openai_client(self):
        """初始化 OpenAI 客户端"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.openai_client = openai.OpenAI(api_key=api_key)
        else:
            print("Warning: OPENAI_API_KEY not found in environment variables")
    
    def start_recording(self):
        """开始录音"""
        if self.is_recording:
            return
        
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            self.is_recording = True
            self.audio_data = []
            
            # 在新线程中录音
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.start()
            
            self.recording_started.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"录音启动失败: {str(e)}")
    
    def stop_recording(self):
        """停止录音"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        # 等待录音线程结束
        if hasattr(self, 'recording_thread'):
            self.recording_thread.join()
        
        # 清理资源
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        
        self.recording_stopped.emit()
        
        # 保存音频文件
        if self.audio_data:
            self._save_audio_file()
            self._start_transcription()
    
    def _record_audio(self):
        """录音线程函数"""
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.audio_data.append(data)
            except Exception as e:
                self.error_occurred.emit(f"录音过程中出错: {str(e)}")
                break
    
    def _save_audio_file(self):
        """保存音频文件"""
        try:
            # 创建临时文件保存录音
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            self.last_audio_file = temp_file.name
            temp_file.close()
            
            # 写入 WAV 文件
            with wave.open(self.last_audio_file, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.audio_data))
            
            self.audio_saved.emit(self.last_audio_file)
            
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
    
    def __init__(self, parent=None):
        super().__init__("🎤", parent)
        self.setToolTip("点击开始录音，再次点击停止录音")
        self.setFixedSize(40, 40)
        
        # 创建录音器
        self.recorder = VoiceRecorder()
        
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
            self.recorder.stop_recording()
        else:
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
        self.voice_recorder.play_last_recording()
    
    def _on_audio_saved(self, file_path: str):
        """音频保存完成，启用播放按钮"""
        self.setEnabled(True)
        self.setToolTip("播放最后录制的音频")
    
    def _on_error(self, error_message: str):
        """错误处理"""
        if "播放音频失败" in error_message or "没有找到录音文件" in error_message:
            QMessageBox.warning(self, "播放错误", error_message) 
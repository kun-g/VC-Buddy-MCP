# 语音录制器测试工具

## 概述

本工具是一个完整的语音录制器测试界面，支持录音、播放录音和语音转写功能。语音转写使用 OpenAI 的 Whisper API。

## 功能特性

- 🎤 **一键录音**: 点击麦克风按钮开始/停止录音
- 🔊 **播放录音**: 点击喇叭按钮播放最后录制的音频
- 🗣️ **语音转写**: 自动将录音转换为文字（支持中文）
- 📝 **结果显示**: 实时显示转写结果
- ⚡ **状态提示**: 显示录音、播放和转写的状态
- 🔍 **智能检查**: 启动时自动检查依赖和设备状态

## 文件结构

```
tools/
├── voice_recorder_test.py     # 语音录制器测试工具（主程序）
└── README_VOICE_RECORDER.md   # 本说明文档

buddy/ui/
└── voice_recorder.py          # 核心语音录制模块
```

## 依赖要求

### Python 包
- `PySide6` - GUI 框架
- `pyaudio` - 音频录制和播放
- `openai` - OpenAI API 客户端（可选，仅语音转写需要）
- `wave` - 音频文件处理

### 系统依赖
在 macOS 上，你可能需要安装 PortAudio：
```bash
brew install portaudio
```

## 环境配置

### 1. 安装依赖
```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install PySide6 pyaudio openai
```

### 2. 设置 OpenAI API Key（可选）

```bash
export OPENAI_API_KEY='your-openai-api-key'
```

或在你的 shell 配置文件中添加：
```bash
echo 'export OPENAI_API_KEY="your-openai-api-key"' >> ~/.zshrc
source ~/.zshrc
```

**注意**: 录音和播放功能不需要 API Key，只有语音转写功能需要。

### 3. 麦克风和扬声器权限
确保你的应用有麦克风和扬声器访问权限。在 macOS 上首次运行时会弹出权限请求。

## 运行测试工具

### 推荐方法: 直接运行
```bash
# 在项目根目录运行
python tools/voice_recorder_test.py
```

### 或使用相对路径
```bash
cd tools
python voice_recorder_test.py
```

## 使用方法

1. **启动工具**: 运行测试脚本，终端会显示系统检查结果
2. **检查状态**: 工具会自动检查依赖、音频设备和 API Key 配置
3. **开始录音**: 点击麦克风按钮（🎤），按钮会变为停止按钮（⏹️）
4. **停止录音**: 再次点击按钮停止录音
5. **播放录音**: 录音完成后，点击喇叭按钮（🔊）播放刚才的录音
6. **查看结果**: 转写结果会自动显示在文本框中（需要 API Key）

## 界面说明

### 按钮布局
```
   🎤     🔊
  录音    播放
```

### 状态说明

- **准备就绪**: 可以开始录音
- **正在录音**: 录音进行中（红色），播放按钮被禁用
- **音频已保存，可以播放录音**: 录音结束，音频文件已保存（蓝色）
- **录音完成，正在转写**: 正在进行语音转写（橙色）
- **转写完成**: 语音转写完成（绿色）
- **错误**: 发生错误时显示错误信息（红色）

### 启动时检查项目

工具启动时会自动检查：
- ✅ 依赖包是否已安装
- ✅ 音频输入/输出设备是否可用
- ✅ OpenAI API Key 是否配置

## 注意事项

1. **网络连接**: 语音转写需要网络连接 OpenAI API（录音和播放不需要）
2. **API 费用**: 使用 Whisper API 会产生费用，请注意 API 使用量
3. **录音质量**: 建议在安静环境中录音以获得更好的转写效果
4. **语言支持**: 默认设置为中文转写，也支持其他语言
5. **临时文件**: 录音会保存为临时文件，应用关闭时会自动清理

## 故障排除

### 依赖问题
```bash
❌ 缺少以下依赖:
   - pyaudio
   - PySide6

安装方法:
   pip install pyaudio PySide6
```

### 音频设备问题
```bash
⚠️  未检测到可用的音频输入设备
```
- 检查麦克风是否连接
- 检查系统音频设置
- 重启应用或系统

### 录音失败
- 检查麦克风权限
- 确保没有其他应用占用麦克风
- 重启应用

### 播放失败
- 检查扬声器权限
- 确保音频设备正常工作
- 确保已经录制过音频（播放按钮初始状态为禁用）

### 转写失败
- 检查网络连接
- 验证 OpenAI API Key 是否正确
- 检查 API 配额是否足够

## 开发和集成

### 集成到其他项目

```python
import sys
import os

# 添加项目路径
project_root = "/path/to/VC-Buddy-MCP"
sys.path.insert(0, project_root)

from buddy.ui.voice_recorder import VoiceButton, PlayButton

# 创建语音按钮
voice_button = VoiceButton()

# 创建播放按钮
play_button = PlayButton(voice_button.recorder)

# 连接转写结果回调
voice_button.connect_transcription_ready(lambda text: print(f"转写结果: {text}"))

# 添加到你的界面布局中
layout.addWidget(voice_button)
layout.addWidget(play_button)
```

### 自定义配置

```python
from buddy.ui.voice_recorder import VoiceRecorder

recorder = VoiceRecorder()
# 修改音频参数
recorder.rate = 22050  # 采样率
recorder.channels = 2  # 立体声

# 播放最后录制的音频
recorder.play_last_recording()

# 清理临时文件
recorder.cleanup()
```

## API 文档

### VoiceRecorder 类
- `start_recording()`: 开始录音
- `stop_recording()`: 停止录音
- `play_last_recording()`: 播放最后录制的音频
- `cleanup()`: 清理临时文件
- `recording_started` 信号: 录音开始时发出
- `recording_stopped` 信号: 录音停止时发出
- `audio_saved(str)` 信号: 音频保存完成时发出，传递文件路径
- `transcription_ready(str)` 信号: 转写完成时发出
- `error_occurred(str)` 信号: 错误发生时发出

### VoiceButton 类
- 继承自 QPushButton
- 内置 VoiceRecorder 实例
- `connect_transcription_ready(callback)`: 连接转写结果回调

### PlayButton 类
- 继承自 QPushButton
- 播放录音按钮，需要传入 VoiceRecorder 实例
- 录音完成后自动启用，录音过程中自动禁用
- 自动处理播放相关的错误

## 测试流程

1. **基础测试**: 录音 → 播放 → 检查音质
2. **转写测试**: 录音 → 检查转写结果准确性  
3. **错误测试**: 断网状态下测试各功能
4. **权限测试**: 拒绝麦克风权限后的行为

## 许可证

本工具遵循项目的 MIT 许可证。 
# 🎤 流式语音输入功能使用指南

流式语音输入功能允许用户边说边输入，提供实时的语音转写体验，无需等待录音结束。

## ✨ 功能特性

### 🔄 实时转写
- **边说边输入**: 录音过程中实时显示转写结果
- **流式处理**: 每2秒处理一个音频块，提供即时反馈
- **缓冲管理**: 智能管理转写缓冲区，避免重复内容

### 🎯 智能命令检测
- **停止命令**: 说出配置的停止词汇自动结束录音
- **发送命令**: 说出配置的发送词汇自动发送内容
- **多语言支持**: 同时支持中文和英文命令

### ⚙️ 灵活配置
- **自定义命令**: 可通过设置界面配置个性化命令
- **即时生效**: 设置保存后立即在下次录音中生效

## 🚀 使用方法

### 1. 基础使用

1. **启动录音**: 点击 🎤 录音按钮开始流式录音
2. **实时转写**: 说话时转写结果会实时显示在输入框中
3. **结束录音**: 
   - 手动点击 ⏹️ 停止录音按钮
   - 或说出停止命令，如"我说完了"

### 2. 语音命令使用

#### 停止录音命令（默认）
- 中文: "我说完了"、"说完了"、"结束"、"停止录音"、"停止"
- 英文: "finish"、"done"、"stop"、"end"

#### 直接发送命令（默认）
- 中文: "开工吧"、"发送"、"提交"、"执行"、"开始干活"、"开始工作"
- 英文: "send"、"submit"、"go"、"execute"、"let's go"

### 3. 自定义语音命令

1. 点击 ⚙️ 语音设置按钮
2. 在"停止录音命令"选项卡中配置停止命令
3. 在"发送命令"选项卡中配置发送命令
4. 每行一个命令，支持中英文混合
5. 点击保存，设置立即生效

## 🛠️ 测试工具

### 独立测试工具
使用 `tools/streaming_voice_test.py` 测试流式语音功能：

```bash
cd VC-Buddy-MCP
python tools/streaming_voice_test.py
```

### 测试工具功能
- **实时转写显示**: 上方文本框显示实时转写进度
- **最终结果显示**: 下方文本框显示完整转写结果
- **命令检测提示**: 状态栏显示检测到的命令
- **设置管理**: 可在测试中调整语音命令设置

## 🔧 技术配置

### OpenAI API 配置
流式语音输入需要配置 OpenAI API：

1. 在设置中配置 API Key
2. 可选配置自定义 API URL（支持第三方服务）
3. 系统会自动验证配置有效性

### 音频参数
- **采样率**: 16kHz
- **声道**: 单声道
- **格式**: 16位PCM
- **处理块大小**: 2秒音频块

## 📱 界面集成

### QML界面支持
- **实时显示**: 转写片段自动追加到输入框
- **自动滚动**: 输入框自动滚动到最新内容
- **状态指示**: 录音状态清晰显示
- **命令反馈**: 检测到命令时提供即时反馈

### 设置界面
- **语音设置按钮**: 录音按钮下方的设置入口
- **分类管理**: 停止命令和发送命令分别管理
- **重置功能**: 一键恢复默认命令配置
- **即时验证**: 保存时验证配置有效性

## 🎯 使用场景

### 快速录入
- **会议记录**: 边开会边记录，实时转写
- **文档编写**: 口述文档内容，实时显示
- **代码注释**: 为代码添加语音注释

### 智能交互
- **任务创建**: 口述任务内容，说"发送"自动提交
- **快速回复**: 语音回复，自定义发送命令
- **多轮对话**: 连续语音输入，智能分段

## ⚠️ 注意事项

### 网络要求
- 需要稳定的网络连接调用 OpenAI API
- 转写延迟取决于网络状况和API响应速度

### 隐私保护
- 语音数据仅用于转写，不会存储
- 转写通过 OpenAI Whisper API 处理
- 遵循 OpenAI 隐私政策

### 最佳实践
- **清晰发音**: 确保发音清晰，提高识别准确度
- **环境安静**: 减少背景噪音干扰
- **命令分离**: 避免在句子中间说出命令词汇
- **适当停顿**: 说完一句话后稍作停顿，便于分段处理

## 🔧 故障排除

### 常见问题

#### 转写不准确
- 检查麦克风设置和音量
- 确保网络连接稳定
- 在安静环境中使用
- 说话速度适中，发音清晰

#### 命令不响应
- 检查语音设置中的命令配置
- 确保命令发音清晰准确
- 检查是否在句子中间说出了命令

#### API 错误
- 验证 OpenAI API Key 有效性
- 检查 API URL 配置是否正确
- 确认账户有足够的API调用额度

### 调试模式
在测试工具中可以看到详细的状态信息：
- 录音状态变化
- 转写进度显示
- 命令检测结果
- 错误信息提示

## 📈 性能优化

### 系统优化
- **多线程处理**: 录音和转写在独立线程中进行
- **内存管理**: 及时清理音频缓冲区
- **异步操作**: 不阻塞主界面响应

### 用户体验
- **即时反馈**: 实时显示转写进度
- **智能分段**: 自动处理音频分块
- **错误恢复**: 网络错误后自动重试 
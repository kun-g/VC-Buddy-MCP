# TODO展示

## 简化 TODO 列表
state=done

TODO 列表只展示标题就可以，属性和详情不用展示在列表里

# 分析统计功能

## 平台信息收集和分析 
state=done

实现了完整的平台信息收集，包括：
- 操作系统信息（macOS/Windows/Linux）
- 架构信息（x64/ARM64/Apple Silicon）  
- Python版本信息
- 系统语言和地区设置

## 语言和国家统计
state=done

将语言和国家信息作为用户属性（User Properties）收集：
- 自动检测系统语言代码（zh/en/ja等）
- 自动检测国家代码（CN/US/JP等）
- 支持跨平台locale检测
- 与设备ID一样作为用户标识信息

## IP地址收集
state=done

实现了安全的IP地址收集功能：
- 自动获取公网IP地址（用于地区统计）
- 收集本地IP和主机名信息
- 检测网络类型（公网/私网/本地）
- 所有信息匿名化处理，不关联个人身份

## 用户属性与事件属性分离
state=done

重构分析系统架构：
- 语言、国家、平台信息作为User Properties设置
- 事件属性只包含事件相关信息，减少重复数据
- 首次事件时自动设置用户属性
- 符合Amplitude最佳实践

# 文档维护

## 根据已完成任务更新文档
对于TODO项目根节点（#标记的），右键里有个更新文档按钮，可以根据整个节点下的已完成任务更新文档(PRD 等)

# 初始化引导
引导设置 Cursor User Rules

# 语音输入

### 支持流式语音输入
语音输入实现流式输入，边说边输入
你看一下 answer_box_qml.py 就知道了，有一个输入窗口
不需要语音输入的编辑功能，但是需要用户自定义结束语。比如「我说完了」就结束录音状态，「开工吧」，就直接把当前结果发送过去。

# 支持 SSE 模式

# 新手友好
make install 更智能一些，能根据系统安装额外的依赖
其他 make 不用每次都 install ，可以失败时

## 需要一个setup命令
需要一个命令来设置项目环境
比如npx vcbuddy setup .
就在当前目录设置cursor rule
测试一下没有

# 处理LLM 传入参数不合规范的情况
处理LLM 传入参数不合规范的情况:
1. 缺project_directory
2. 缺 summary
3. 不是 JSON
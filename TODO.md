# VC-Buddy 开发任务

## 配置管理系统
重构QSettings硬编码问题，实现灵活的配置管理

### 环境变量支持
支持通过环境变量覆盖配置
- VC_BUDDY_ORG: 组织名称
- VC_BUDDY_APP_NAME: 应用名称

### 项目配置
每个项目可以有独立的配置文件
位置：{project_directory}/.vc-buddy/config.json

## UI功能增强

### 窗口置顶
添加窗口置顶功能，可通过配置控制

### 快捷键支持
实现Ctrl+Enter快捷键触发发送功能

### TODO展示
如果项目目录有TODO.md文件，以树状结构展示任务

## MCP服务器

### ask_for_feedback工具
向用户请求交互式反馈的工具

#### 参数支持
- summary: 反馈请求描述
- project_directory: 项目目录路径

#### 使用场景
1. 需要用户确认或澄清需求时
2. 完成任务需要用户验证结果时
3. 需要用户提供额外信息时
4. 遇到多个选项需要用户选择时 
在 VC-Buddy-MCP 目录提交你修改的文件
# VC-Buddy 配置管理

## 概述

原先的硬编码问题：
```python
# 硬编码方式（不推荐）
settings = QSettings("MyCompany", "AnswerBoxApp")
```

现在采用了更灵活的配置管理方式，支持多种配置来源的优先级管理。

## 配置优先级

配置值的优先级从高到低：
1. **环境变量**
2. **配置文件**
3. **默认值**

## 环境变量

可以通过以下环境变量覆盖配置：

```bash
export VC_BUDDY_ORG="您的组织名"           # 组织名称
export VC_BUDDY_APP_NAME="您的应用名"      # 应用名称
export VC_BUDDY_DOMAIN="您的域名"          # 组织域名
export VC_BUDDY_CONFIG="/path/to/config.json"  # 自定义配置文件路径
```

## 配置文件位置

配置文件会按以下优先级查找：
1. `$VC_BUDDY_CONFIG` 环境变量指定的路径
2. `~/.vc-buddy/config.json`（用户主目录）
3. 如果都不存在，使用内置默认配置

## 配置文件格式

```json
{
  "app": {
    "organization_name": "VC-Buddy",
    "application_name": "AnswerBox", 
    "organization_domain": "vcbuddy.local"
  },
  "ui": {
    "window": {
      "default_width": 400,
      "default_height": 300,
      "remember_position": true
    }
  }
}
```

## 使用方法

### 基本用法
```python
from .config import config_manager

# 获取配置值
org_name = config_manager.organization_name
app_name = config_manager.application_name

# 获取嵌套配置
width = config_manager.get("ui.window.default_width", 300)

# 设置配置值
config_manager.set("ui.window.default_width", 500)
config_manager.save_config()
```

### QSettings 管理
```python
from .answer_box import SettingsManager

# 获取 QSettings 实例
settings = SettingsManager.get_settings()

# 保存窗口几何信息
SettingsManager.save_window_geometry(widget)

# 恢复窗口几何信息
SettingsManager.restore_window_geometry(widget)
```

## 优势

1. **灵活性**：支持环境变量、配置文件、默认值的多级覆盖
2. **可维护性**：配置集中管理，易于修改和扩展
3. **可移植性**：不同环境可以使用不同的配置
4. **用户友好**：用户可以通过配置文件自定义行为
5. **向后兼容**：如果没有配置文件，使用合理的默认值

## 示例场景

### 开发环境
```bash
export VC_BUDDY_ORG="Dev-Team"
export VC_BUDDY_APP_NAME="AnswerBox-Dev"
```

### 生产环境
```bash
export VC_BUDDY_ORG="Production-Company"
export VC_BUDDY_APP_NAME="AnswerBox"
export VC_BUDDY_CONFIG="/etc/vc-buddy/config.json"
```

### 用户自定义
用户可以在 `~/.vc-buddy/config.json` 中设置自己的首选项，如窗口大小、是否记住位置等。 
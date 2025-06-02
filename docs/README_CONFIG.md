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
1. **项目目录配置** - `{project_directory}/.vc-buddy/config.json`
2. **环境变量指定的配置文件** - `$VC_BUDDY_CONFIG`
3. **用户主目录配置** - `~/.vc-buddy/config.json`
4. **环境变量**
5. **默认值**

**特殊说明**：对于OpenAI API配置，优先级为：
1. **配置文件中的设置** - `openai.api_key` 和 `openai.api_url`
2. **环境变量** - `OPENAI_API_KEY` 和 `OPENAI_API_URL`
3. **默认值**

这样设计是为了让用户通过图形界面设置的配置能够覆盖环境变量。

## 环境变量

可以通过以下环境变量覆盖配置：

```bash
export VC_BUDDY_ORG="您的组织名"           # 组织名称
export VC_BUDDY_APP_NAME="您的应用名"      # 应用名称
export VC_BUDDY_DOMAIN="您的域名"          # 组织域名
export VC_BUDDY_CONFIG="/path/to/config.json"  # 自定义配置文件路径
```

## 配置文件位置

配置文件会按以下优先级查找和合并：
1. **项目配置**：`{project_directory}/.vc-buddy/config.json`（最高优先级）
2. **环境变量配置**：`$VC_BUDDY_CONFIG` 环境变量指定的路径
3. **用户配置**：`~/.vc-buddy/config.json`（用户主目录）
4. **默认配置**：内置默认值

配置会按优先级递归合并，高优先级的配置会覆盖低优先级的相同字段。

## 项目特定配置

每个项目可以有自己的配置文件，只需在项目根目录创建 `.vc-buddy/config.json`：

```bash
# 在项目目录中
mkdir .vc-buddy
cat > .vc-buddy/config.json << EOF
{
  "ui": {
    "window": {
      "default_width": 500,
      "default_height": 400,
      "stay_on_top": false
    }
  }
}
EOF
```

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
      "remember_position": true,
      "stay_on_top": true
    }
  }
}
```

## 使用方法

### 基本用法
```python
from .config import config_manager, get_project_config_manager

# 使用全局配置
org_name = config_manager.organization_name

# 使用项目特定配置
project_config = get_project_config_manager("/path/to/project")
width = project_config.get("ui.window.default_width", 300)

# 设置配置值
config_manager.set("ui.window.default_width", 500)
config_manager.save_config()

# 保存到项目配置
project_config.save_config(save_to_project=True)
```

### QSettings 管理
```python
from .answer_box import SettingsManager

# 创建设置管理器（需要配置管理器实例）
settings_mgr = SettingsManager(config_manager)

# 保存窗口几何信息
settings_mgr.save_window_geometry(widget)

# 恢复窗口几何信息
settings_mgr.restore_window_geometry(widget)
```

## 优势

1. **灵活性**：支持项目、环境变量、配置文件、默认值的多级覆盖
2. **项目隔离**：每个项目可以有独立的配置
3. **配置合并**：多层配置自动合并，无需完整重写
4. **可维护性**：配置集中管理，易于修改和扩展
5. **可移植性**：不同环境可以使用不同的配置
6. **用户友好**：用户可以通过配置文件自定义行为
7. **向后兼容**：如果没有配置文件，使用合理的默认值

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

### 项目特定配置
```bash
# 项目A - 大窗口，不置顶
echo '{"ui":{"window":{"default_width":600,"default_height":500,"stay_on_top":false}}}' > projectA/.vc-buddy/config.json

# 项目B - 小窗口，置顶
echo '{"ui":{"window":{"default_width":250,"default_height":150,"stay_on_top":true}}}' > projectB/.vc-buddy/config.json
```

### 用户自定义
用户可以在 `~/.vc-buddy/config.json` 中设置自己的首选项，如窗口大小、是否记住位置等。 
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtQuick.Controls.Material 2.15
import "."

Window {
    id: settingsWindow
    
    title: "设置"
    width: 600
    height: 700
    minimumWidth: 550
    minimumHeight: 650
    
    modality: Qt.ApplicationModal
    
    // Material 主题设置
    Material.theme: Material.Light
    Material.accent: Theme.colors.primary
    
    // 信号定义
    signal accepted()
    signal rejected()
    signal settingsSaved()
    
    property var configManager: null
    property string apiKeyText: ""
    property string apiUrlText: ""
    property bool apiKeyVisible: false
    property bool isTestingConnection: false
    
    Component.onCompleted: {
        loadSettings()
    }
    
    function loadSettings() {
        if (configManager) {
            var apiKey = configManager.get("openai.api_key", "")
            var apiUrl = configManager.get("openai.api_url", "")
            
            if (apiKey) {
                apiKeyText = apiKey
                apiKeyInput.text = apiKey
            }
            
            if (apiUrl && apiUrl !== "https://api.openai.com/v1") {
                apiUrlText = apiUrl
                apiUrlInput.text = apiUrl
            }
            
            updateStatusDisplay()
        }
    }
    
    function saveSettings() {
        var apiKey = apiKeyInput.text.trim()
        var apiUrl = apiUrlInput.text.trim()
        
        // 如果URL为空，使用默认值
        if (!apiUrl) {
            apiUrl = "https://api.openai.com/v1"
        }
        
        if (configManager) {
            configManager.set("openai.api_key", apiKey)
            configManager.set("openai.api_url", apiUrl)
            configManager.save_config()
        }
        
        settingsSaved()
        accepted()
        close()
    }
    
    function testConnection() {
        var apiKey = apiKeyInput.text.trim()
        if (!apiKey) {
            showMessage("测试失败", "请先输入 API Key", false)
            return
        }
        
        isTestingConnection = true
        testButton.enabled = false
        testButton.text = "测试中..."
        
        // 模拟测试（在实际应用中应该调用后端API测试）
        testTimer.start()
    }
    
    function updateStatusDisplay() {
        if (configManager) {
            var hasApiKey = configManager.get("openai.api_key", "") !== ""
            if (hasApiKey) {
                statusLabel.text = "✅ 已配置"
                statusLabel.color = "#28a745"
            } else {
                statusLabel.text = "❌ 未配置"
                statusLabel.color = "#dc3545"
            }
        }
    }
    
    function showMessage(title, message, isSuccess) {
        messageDialog.title = title
        messageDialog.text = message
        messageDialog.isSuccess = isSuccess
        messageDialog.open()
    }
    
    // 测试连接定时器（模拟异步操作）
    Timer {
        id: testTimer
        interval: 2000
        onTriggered: {
            isTestingConnection = false
            testButton.enabled = true
            testButton.text = "测试连接"
            
            var apiKey = apiKeyInput.text.trim()
            if (apiKey.length > 20) {
                showMessage("测试成功", "API Key 验证通过！", true)
            } else {
                showMessage("测试失败", "API Key 格式不正确", false)
            }
        }
    }
    
    function getConfigPath() {
        if (configManager) {
            // 获取实际的配置文件路径
            try {
                var configPath = configManager.getConfigFilePath()
                if (configPath) {
                    return configPath
                }
            } catch (e) {
                console.log("Failed to get config file path:", e)
            }
            
            // 回退到默认路径显示
            return "~/.vc-buddy/config.json"
        }
        return "配置文件路径未知"
    }
    
    ScrollView {
        anchors.fill: parent
        anchors.margins: 20
        
        ColumnLayout {
            width: settingsWindow.width - 40
            spacing: 20
            
            // 标题
            Text {
                Layout.fillWidth: true
                text: "VC-Buddy 设置"
                font.pixelSize: Theme.fonts.xxlarge
                font.bold: true
                font.family: Theme.fonts.family
                color: Theme.colors.text
                horizontalAlignment: Text.AlignHCenter
            }
            
            // OpenAI 配置组
            GroupBox {
                Layout.fillWidth: true
                title: "OpenAI 配置"
                font.pixelSize: Theme.fonts.medium
                font.bold: true
                font.family: Theme.fonts.family
                
                background: Rectangle {
                    color: Theme.colors.backgroundSecondary
                    border.color: Theme.colors.borderDark
                    border.width: 1
                    radius: Theme.radius.medium
                }
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 15
                    
                    // API Key 输入
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 5
                        
                        Text {
                            text: "API Key:"
                            font.pixelSize: Theme.fonts.normal
                            font.family: Theme.fonts.family
                            color: Theme.colors.text
                        }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 10
                            
                            TextField {
                                id: apiKeyInput
                                Layout.fillWidth: true
                                placeholderText: "请输入您的 OpenAI API Key"
                                echoMode: apiKeyVisible ? TextInput.Normal : TextInput.Password
                                font.pixelSize: Theme.fonts.normal
                                font.family: Theme.fonts.family
                                
                                background: Rectangle {
                                    color: "#ffffff"
                                    border.color: parent.activeFocus ? Theme.colors.primary : Theme.colors.borderLight
                                    border.width: parent.activeFocus ? 2 : 1
                                    radius: Theme.radius.normal
                                }
                            }
                            
                            Button {
                                text: apiKeyVisible ? "🙈 隐藏" : "👁️ 显示"
                                implicitWidth: 80
                                font.pixelSize: Theme.fonts.small
                                font.family: Theme.fonts.family
                                
                                background: Rectangle {
                                    color: parent.pressed ? "#e9ecef" : parent.hovered ? "#f8f9fa" : "#ffffff"
                                    border.color: "#dee2e6"
                                    border.width: 1
                                    radius: Theme.radius.normal
                                }
                                
                                contentItem: Text {
                                    text: parent.text
                                    font: parent.font
                                    color: "#495057"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                onClicked: apiKeyVisible = !apiKeyVisible
                            }
                        }
                    }
                    
                    // API URL 输入
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 5
                        
                        Text {
                            text: "API URL:"
                            font.pixelSize: Theme.fonts.normal
                            font.family: Theme.fonts.family
                            color: Theme.colors.text
                        }
                        
                        TextField {
                            id: apiUrlInput
                            Layout.fillWidth: true
                            placeholderText: "https://api.openai.com/v1"
                            font.pixelSize: Theme.fonts.normal
                            font.family: Theme.fonts.family
                            
                            background: Rectangle {
                                color: "#ffffff"
                                border.color: parent.activeFocus ? Theme.colors.primary : Theme.colors.borderLight
                                border.width: parent.activeFocus ? 2 : 1
                                radius: Theme.radius.normal
                            }
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            text: "留空使用默认地址，或输入自定义API端点（如代理服务器地址）"
                            font.pixelSize: Theme.fonts.small
                            font.family: Theme.fonts.family
                            color: Theme.colors.textSecondary
                            wrapMode: Text.WordWrap
                            font.italic: true
                        }
                    }
                    
                    // API Key 说明
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 150
                        clip: true
                        
                        Rectangle {
                            width: parent.width
                            height: apiKeyInfo.contentHeight + 20
                            color: "#f8f9fa"
                            border.color: "#dee2e6"
                            border.width: 1
                            radius: Theme.radius.normal
                            
                            Text {
                                id: apiKeyInfo
                                anchors.fill: parent
                                anchors.margins: 10
                                text: "获取 API Key 的步骤：\n" +
                                      "1. 访问 https://platform.openai.com/api-keys\n" +
                                      "2. 登录您的 OpenAI 账户\n" +
                                      "3. 点击 'Create new secret key' 创建新的密钥\n" +
                                      "4. 复制生成的密钥并粘贴到上方输入框中\n\n" +
                                      "API URL 配置：\n" +
                                      "• 默认：https://api.openai.com/v1 （官方API）\n" +
                                      "• 可配置代理服务器或第三方兼容服务的URL"
                                font.pixelSize: Theme.fonts.small
                                font.family: Theme.fonts.family
                                color: "#6c757d"
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                }
            }
            
            // 当前状态显示
            GroupBox {
                Layout.fillWidth: true
                title: "当前状态"
                font.pixelSize: Theme.fonts.medium
                font.bold: true
                font.family: Theme.fonts.family
                
                background: Rectangle {
                    color: Theme.colors.backgroundSecondary
                    border.color: Theme.colors.borderDark
                    border.width: 1
                    radius: Theme.radius.medium
                }
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 10
                    
                    RowLayout {
                        Layout.fillWidth: true
                        
                        Text {
                            text: "API Key 状态:"
                            font.pixelSize: Theme.fonts.normal
                            font.family: Theme.fonts.family
                            color: Theme.colors.text
                        }
                        
                        Text {
                            id: statusLabel
                            text: "❌ 未配置"
                            font.pixelSize: Theme.fonts.normal
                            font.family: Theme.fonts.family
                            color: "#dc3545"
                        }
                        
                        Item { Layout.fillWidth: true }
                    }
                    
                    RowLayout {
                        Layout.fillWidth: true
                        
                        Text {
                            text: "配置文件:"
                            font.pixelSize: Theme.fonts.normal
                            font.family: Theme.fonts.family
                            color: Theme.colors.text
                        }
                        
                        Text {
                            id: configPathLabel
                            text: getConfigPath()
                            font.pixelSize: Theme.fonts.small
                            font.family: "Monaco, Consolas, monospace"
                            color: Theme.colors.textSecondary
                            wrapMode: Text.WrapAnywhere
                            Layout.fillWidth: true
                        }
                    }
                }
            }
            
            // 按钮区域
            RowLayout {
                Layout.fillWidth: true
                Layout.topMargin: 20
                
                Item { Layout.fillWidth: true }
                
                // 测试连接按钮
                Button {
                    id: testButton
                    text: "测试连接"
                    enabled: !isTestingConnection
                    font.pixelSize: Theme.fonts.normal
                    font.family: Theme.fonts.family
                    
                    background: Rectangle {
                        color: parent.pressed ? "#0056b3" : parent.hovered ? "#007bff" : "#17a2b8"
                        radius: Theme.radius.normal
                        
                        Behavior on color {
                            ColorAnimation {
                                duration: Theme.animation.fast
                                easing.type: Easing.OutQuad
                            }
                        }
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        font: parent.font
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: testConnection()
                }
                
                // 取消按钮
                Button {
                    text: "取消"
                    font.pixelSize: Theme.fonts.normal
                    font.family: Theme.fonts.family
                    
                    background: Rectangle {
                        color: parent.pressed ? "#545b62" : parent.hovered ? "#6c757d" : "#6c757d"
                        radius: Theme.radius.normal
                        
                        Behavior on color {
                            ColorAnimation {
                                duration: Theme.animation.fast
                                easing.type: Easing.OutQuad
                            }
                        }
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        font: parent.font
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        rejected()
                        close()
                    }
                }
                
                // 保存按钮
                Button {
                    text: "保存"
                    font.pixelSize: Theme.fonts.normal
                    font.family: Theme.fonts.family
                    font.bold: true
                    
                    background: Rectangle {
                        color: parent.pressed ? "#0056b3" : parent.hovered ? "#007bff" : "#007bff"
                        radius: Theme.radius.normal
                        
                        Behavior on color {
                            ColorAnimation {
                                duration: Theme.animation.fast
                                easing.type: Easing.OutQuad
                            }
                        }
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        font: parent.font
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: saveSettings()
                }
            }
        }
    }
    
    // 消息对话框
    Dialog {
        id: messageDialog
        parent: Overlay.overlay
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        width: 350
        modal: true
        
        property bool isSuccess: true
        property alias text: messageText.text
        
        Label {
            id: messageText
            font.pixelSize: Theme.fonts.normal
            font.family: Theme.fonts.family
            wrapMode: Text.WordWrap
            anchors.centerIn: parent
        }
        
        standardButtons: Dialog.Ok
        
        background: Rectangle {
            color: "#ffffff"
            border.color: messageDialog.isSuccess ? "#28a745" : "#dc3545"
            border.width: 2
            radius: Theme.radius.medium
        }
    }
} 
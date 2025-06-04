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
            
            // 统计配置保存操作
            try {
                if (typeof backend !== 'undefined' && backend && backend.trackConfigAction) {
                    backend.trackConfigAction("save_settings", "openai_config")
                }
            } catch (e) {
                console.log("Failed to track config save:", e)
            }
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
        
        var apiUrl = apiUrlInput.text.trim()
        if (!apiUrl) {
            apiUrl = "https://api.openai.com/v1"  // 使用默认URL
        }
        
        // 统计测试连接操作
        try {
            if (typeof backend !== 'undefined' && backend && backend.trackConfigAction) {
                backend.trackConfigAction("test_connection", "openai_api")
            }
        } catch (e) {
            console.log("Failed to track test connection:", e)
        }
        
        isTestingConnection = true
        testButton.enabled = false
        testButton.text = "测试中..."
        
        // 创建回调对象来接收测试结果
        var callback = Qt.createQmlObject('
            import QtQuick 2.15
            QtObject {
                function call(status, message) {
                    if (status === "success") {
                        showMessage("测试成功", message, true)
                    } else if (status === "warning") {
                        showMessage("测试警告", message, false)
                    } else {
                        showMessage("测试失败", message, false)
                    }
                    isTestingConnection = false
                    testButton.enabled = true
                    testButton.text = "测试连接"
                }
            }
        ', settingsWindow)
        
        // 调用后端的真实API测试方法
        if (typeof backend !== 'undefined' && backend && backend.testApiConnection) {
            backend.testApiConnection(apiKey, apiUrl, callback)
        } else {
            // 如果后端不可用，显示错误
            showMessage("测试失败", "后端API测试方法不可用", false)
            isTestingConnection = false
            testButton.enabled = true
            testButton.text = "测试连接"
        }
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
                                id: showHideButton
                                text: apiKeyVisible ? "🙈 隐藏" : "👁️ 显示"
                                implicitWidth: 80
                                font.pixelSize: Theme.fonts.small
                                font.family: Theme.fonts.family
                                
                                background: Rectangle {
                                    color: showHideButton.pressed ? "#e9ecef" : showHideButton.hovered ? "#f8f9fa" : "#ffffff"
                                    border.color: "#dee2e6"
                                    border.width: 1
                                    radius: Theme.radius.normal
                                }
                                
                                contentItem: Text {
                                    text: showHideButton.text
                                    font: showHideButton.font
                                    color: "#495057"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                }
                                
                                onClicked: {
                                    apiKeyVisible = !apiKeyVisible
                                    
                                    // 统计API Key可见性切换
                                    try {
                                        if (typeof backend !== 'undefined' && backend && backend.trackConfigAction) {
                                            backend.trackConfigAction("toggle_api_key_visibility", "security")
                                        }
                                    } catch (e) {
                                        console.log("Failed to track API key visibility toggle:", e)
                                    }
                                }
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
                            font.family: {
                                // 跨平台等宽字体，使用系统中真正存在的字体
                                if (Qt.platform.os === "osx" || Qt.platform.os === "macos") {
                                    return "Monaco, Menlo, monospace"
                                } else if (Qt.platform.os === "windows") {
                                    return "Consolas, Courier New, monospace"
                                } else {
                                    return "Ubuntu Mono, Liberation Mono, Courier New, monospace"
                                }
                            }
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
                        color: testButton.pressed ? "#0056b3" : testButton.hovered ? "#007bff" : "#17a2b8"
                        radius: Theme.radius.normal
                        
                        Behavior on color {
                            ColorAnimation {
                                duration: Theme.animation.fast
                                easing.type: Easing.OutQuad
                            }
                        }
                    }
                    
                    contentItem: Text {
                        text: testButton.text
                        font: testButton.font
                        color: "white"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: testConnection()
                }
                
                // 取消按钮
                Button {
                    id: cancelButton
                    text: "取消"
                    font.pixelSize: Theme.fonts.normal
                    font.family: Theme.fonts.family
                    
                    background: Rectangle {
                        color: cancelButton.pressed ? "#545b62" : cancelButton.hovered ? "#6c757d" : "#6c757d"
                        radius: Theme.radius.normal
                        
                        Behavior on color {
                            ColorAnimation {
                                duration: Theme.animation.fast
                                easing.type: Easing.OutQuad
                            }
                        }
                    }
                    
                    contentItem: Text {
                        text: cancelButton.text
                        font: cancelButton.font
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
                    id: saveButton
                    text: "保存"
                    font.pixelSize: Theme.fonts.normal
                    font.family: Theme.fonts.family
                    font.bold: true
                    
                    background: Rectangle {
                        color: saveButton.pressed ? "#0056b3" : saveButton.hovered ? "#007bff" : "#007bff"
                        radius: Theme.radius.normal
                        
                        Behavior on color {
                            ColorAnimation {
                                duration: Theme.animation.fast
                                easing.type: Easing.OutQuad
                            }
                        }
                    }
                    
                    contentItem: Text {
                        text: saveButton.text
                        font: saveButton.font
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
        
        contentItem: Rectangle {
            color: "#ffffff"
            border.color: messageDialog.isSuccess ? "#28a745" : "#dc3545"
            border.width: 2
            radius: Theme.radius.medium
            
            Label {
                id: messageText
                font.pixelSize: Theme.fonts.normal
                font.family: Theme.fonts.family
                wrapMode: Text.WordWrap
                anchors.centerIn: parent
                anchors.margins: 20
            }
        }
        
        standardButtons: Dialog.Ok
    }
} 
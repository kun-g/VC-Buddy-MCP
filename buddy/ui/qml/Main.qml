import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls.Material 2.15
import QtQuick.Window 2.15
import "."

ApplicationWindow {
    id: window
    visible: true
    
    // 窗口尺寸和位置
    width: backend && backend.hasValidSavedGeometry() ? backend.savedWidth : (backend ? backend.defaultWidth : 400)
    height: backend && backend.hasValidSavedGeometry() ? backend.savedHeight : (backend ? backend.defaultHeight : 600)
    
    // Ctrl+R 录音快捷键
    Shortcut {
        sequence: "Ctrl+R"
        onActivated: {
            if (backend) {
                backend.toggleRecordingShortcut()
                // 统计快捷键使用
                backend.trackShortcutUsed("Ctrl+R", "toggle_recording")
            }
        }
    }
    
    // Ctrl+E 发送快捷键
    Shortcut {
        sequence: "Ctrl+E"
        onActivated: {
            sendButton.clicked()
            // 统计快捷键使用
            if (backend) {
                backend.trackShortcutUsed("Ctrl+E", "send_message")
            }
        }
    }
    
    // Ctrl+, 打开设置快捷键
    Shortcut {
        sequence: "Ctrl+,"
        onActivated: {
            if (backend) {
                backend.openSettings()
                // 统计快捷键使用
                backend.trackShortcutUsed("Ctrl+,", "open_settings")
            }
        }
    }
    
    // 窗口位置（如果有保存的位置）
    Component.onCompleted: {
        if (backend && backend.hasValidSavedGeometry()) {
            x = backend.savedX
            y = backend.savedY
            console.log("DEBUG: 恢复窗口位置:", x, y, width, height)
        } else {
            // 居中显示
            x = (Screen.width - width) / 2
            y = (Screen.height - height) / 2
            console.log("DEBUG: 居中显示窗口:", x, y, width, height)
        }
        
        // 连接语音设置信号
        if (backend) {
            backend.voiceSettingsRequested.connect(openVoiceSettingsDialog)
            backend.settingsRequested.connect(openSettingsDialog)
        }
    }
    
    title: backend ? backend.windowTitle : "Answer Box"
    
    // 窗口置顶设置
    flags: backend && backend.stayOnTop ? Qt.WindowStaysOnTopHint | Qt.Window : Qt.Window
    
    // Material 主题设置
    Material.theme: Material.Light
    Material.accent: Theme.colors.primary
    
    // 语音设置对话框
    property var voiceSettingsDialog: null
    
    // 主设置对话框
    property var settingsDialog: null
    
    function openVoiceSettingsDialog(configManager) {
        if (!voiceSettingsDialog) {
            var component = Qt.createComponent("VoiceSettingsDialog.qml")
            if (component.status === Component.Ready) {
                voiceSettingsDialog = component.createObject(window)
                voiceSettingsDialog.settingsSaved.connect(function(stopCommands, sendCommands) {
                    if (backend) {
                        backend.onVoiceSettingsSaved(stopCommands, sendCommands)
                    }
                })
            } else {
                console.error("Failed to create VoiceSettingsDialog:", component.errorString())
                return
            }
        }
        
        if (voiceSettingsDialog) {
            voiceSettingsDialog.configManager = configManager
            voiceSettingsDialog.loadSettings()
            voiceSettingsDialog.show()
        }
    }
    
    function openSettingsDialog(configManager) {
        if (!settingsDialog) {
            var component = Qt.createComponent("SettingsDialog.qml")
            if (component.status === Component.Ready) {
                settingsDialog = component.createObject(window)
                settingsDialog.settingsSaved.connect(function() {
                    console.log("Settings saved successfully")
                })
            } else {
                console.error("Failed to create SettingsDialog:", component.errorString())
                return
            }
        }
        
        if (settingsDialog) {
            settingsDialog.configManager = configManager
            settingsDialog.loadSettings()
            settingsDialog.show()
        }
    }
    
    // 主布局
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.medium
        spacing: Theme.spacing.medium
        
        // 主要内容区域 - 垂直分割器
        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Vertical
            
            // 摘要显示区域（可调整高度）
            Rectangle {
                SplitView.preferredHeight: 100
                SplitView.minimumHeight: 60
                SplitView.maximumHeight: 300
                color: Theme.colors.backgroundSecondary
                border.color: Theme.colors.borderDark
                border.width: 1
                radius: Theme.radius.medium
                
                ScrollView {
                    anchors.fill: parent
                    anchors.margins: Theme.spacing.normal
                    clip: true  // 防止内容溢出边界
                    
                    Text {
                        id: summaryText
                        width: parent.width
                        text: backend ? backend.summaryText : "Nothing here"
                        wrapMode: Text.WordWrap
                        font.pixelSize: Theme.fonts.normal
                        font.family: Theme.fonts.family
                        color: Theme.colors.text
                    }
                }
            }
            
            // 主内容区域 - 水平分割器
            SplitView {
                SplitView.fillHeight: true
                orientation: Qt.Horizontal
                
                // 左侧：TODO树状视图
                Rectangle {
                    SplitView.preferredWidth: 200
                    SplitView.minimumWidth: 150
                    color: Theme.colors.background
                    border.color: Theme.colors.borderDark
                    border.width: 1
                    radius: Theme.radius.medium
                    clip: true  // 确保所有内容都在边界内
                    
                    visible: backend && backend.hasTodos
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Theme.spacing.normal
                        spacing: Theme.spacing.small
                        
                        Text {
                            text: "📝 TODO 任务"
                            font.bold: true
                            font.pixelSize: Theme.fonts.medium
                            font.family: Theme.fonts.family
                            color: Theme.colors.text
                        }
                        
                        ScrollView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true  // 防止内容溢出边界
                            
                            ListView {
                                id: todoListView
                                model: backend ? backend.todoModel : null
                                clip: true  // 确保列表项不会溢出ListView边界
                                currentIndex: -1  // 默认不选中任何项目
                                
                                delegate: TodoItemDelegate {
                                    width: todoListView.width
                                    todoItem: model.todoItem
                                    isSelected: todoListView.currentIndex === model.index
                                    onItemClicked: {
                                        todoListView.currentIndex = model.index
                                        if (backend) backend.selectTodoItem(model.index)
                                    }
                                    onItemDoubleClicked: {
                                        if (backend) backend.insertTodoContent(model.index)
                                    }
                                    onMarkDone: {
                                        if (backend) backend.markTodoDone(model.index)
                                    }
                                    onMarkUndone: {
                                        if (backend) backend.markTodoUndone(model.index)
                                    }
                                    onDeleteTodo: {
                                        if (backend) backend.deleteTodoItem(model.index)
                                    }
                                }
                            }
                        }
                    }
                }
                
                // 右侧：详情和输入区域
                Rectangle {
                    SplitView.fillWidth: true
                    color: "transparent"
                    
                    ColumnLayout {
                        anchors.fill: parent
                        spacing: Theme.spacing.normal
                        
                        // TODO详情显示（仅在有TODO时显示）
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 150
                            color: Theme.colors.surface
                            border.color: Theme.colors.borderDark
                            border.width: 1
                            radius: Theme.radius.medium
                            clip: true  // 确保内容不会溢出边界
                            
                            visible: backend && backend.hasTodos
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: Theme.spacing.normal
                                spacing: Theme.spacing.small
                                
                                Text {
                                    text: backend && backend.selectedTodoTitle 
                                          ? backend.selectedTodoTitle
                                          : "📄 任务详情"
                                    font.bold: true
                                    font.pixelSize: Theme.fonts.medium
                                    font.family: Theme.fonts.family
                                    color: Theme.colors.text
                                }
                                
                                ScrollView {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    clip: true  // 防止内容溢出边界
                                    
                                    TextArea {
                                        id: todoDetailText
                                        width: parent.width
                                        text: backend ? backend.selectedTodoDetail : "选择一个任务查看详情"
                                        wrapMode: TextArea.Wrap
                                        textFormat: TextArea.RichText
                                        font.pixelSize: Theme.fonts.small
                                        font.family: Theme.fonts.family
                                        color: Theme.colors.textSecondary
                                        readOnly: true
                                        selectByMouse: true
                                        background: Rectangle {
                                            color: "transparent"
                                        }
                                    }
                                }
                            }
                        }
                        
                        // 输入区域
                        ColumnLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            spacing: Theme.spacing.small
                            
                            // 输入框容器
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: Theme.colors.background
                                border.color: Theme.colors.border
                                border.width: 1
                                radius: Theme.radius.normal
                                clip: true  // 防止内容溢出边界
                                
                                ScrollView {
                                    anchors.fill: parent
                                    anchors.margins: 2  // 给边框留出空间
                                    clip: true
                                    
                                    TextArea {
                                        id: inputArea
                                        wrapMode: TextArea.Wrap
                                        font.pixelSize: Theme.fonts.normal
                                        font.family: Theme.fonts.family
                                        selectByMouse: true
                                        color: Theme.colors.text
                                        
                                        // 设置内部边距，确保文本位置与占位符对齐
                                        leftPadding: 12
                                        topPadding: 12
                                        rightPadding: 12
                                        bottomPadding: 12
                                        
                                        // 移除内置的背景，使用外层Rectangle作为背景
                                        background: Item {}
                                        
                                        // Ctrl+Enter快捷键
                                        Keys.onPressed: function(event) {
                                            if ((event.key === Qt.Key_Return || event.key === Qt.Key_Enter) && 
                                                (event.modifiers & Qt.ControlModifier)) {
                                                sendButton.clicked()
                                                event.accepted = true
                                            }
                                        }
                                    }
                                }
                                
                                // 自定义占位符文本
                                Text {
                                    anchors.left: parent.left
                                    anchors.top: parent.top
                                    anchors.leftMargin: 12  // 与TextArea内部文本对齐
                                    anchors.topMargin: 12   // 与TextArea内部文本对齐
                                    text: "请输入您的反馈..."
                                    font.pixelSize: Theme.fonts.normal
                                    font.family: Theme.fonts.family
                                    color: Theme.colors.textSecondary
                                    opacity: 0.6
                                    visible: inputArea.text.length === 0 && !inputArea.activeFocus
                                    
                                    // 点击占位符文本时聚焦到输入框
                                    MouseArea {
                                        anchors.fill: parent
                                        onClicked: inputArea.forceActiveFocus()
                                    }
                                }
                            }
                            
                            // Commit复选框
                            CheckBox {
                                id: commitCheckbox
                                text: "📝 Commit - 要求先提交修改的文件"
                                font.pixelSize: Theme.fonts.small
                                font.family: Theme.fonts.family
                            }
                            
                            // 录音按钮
                            Button {
                                id: voiceButton
                                Layout.fillWidth: true
                                Layout.preferredHeight: 44  // 增加按钮高度
                            text: {
                                    if (backend && backend.isRecording) {
                                        return "⏹️ 停止录音 (Ctrl+R)"
                                    } else if (backend && backend.isTranscribing) {
                                        return "🔄 正在识别..."
                                    } else {
                                        return "🎤 录音 (Ctrl+R)"
                                    }
                                }
                                font.bold: true
                                font.pixelSize: Theme.fonts.normal
                                font.family: Theme.fonts.family
                                enabled: backend && !backend.isTranscribing  // 识别中禁用按钮
                                
                                background: Rectangle {
                                    color: {
                                        if (backend && backend.isRecording) {
                                            return voiceButton.pressed ? "#d32f2f" : 
                                                   voiceButton.hovered ? "#d32f2f" : "#f44336"
                                        } else if (backend && backend.isTranscribing) {
                                            return "#ff9800"  // 橙色表示正在识别
                                        } else {
                                            return voiceButton.pressed ? "#388e3c" : 
                                                   voiceButton.hovered ? "#388e3c" : "#4caf50"
                                        }
                                    }
                                    radius: Theme.radius.normal
                                    
                                    Behavior on color {
                                        ColorAnimation {
                                            duration: Theme.animation.fast
                                            easing.type: Easing.OutQuad
                                        }
                                    }
                                }
                                
                                contentItem: Text {
                                    text: voiceButton.text
                                    font: voiceButton.font
                                    opacity: enabled ? 1.0 : 0.3
                                    color: Theme.colors.textOnPrimary
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                
                                onClicked: {
                                    if (backend) backend.toggleRecording()
                                }
                            }
                            
                        // DeepSeek总结按钮
                        Button {
                            id: deepseekButton
                            Layout.fillWidth: true
                            Layout.preferredHeight: 44  // 增加按钮高度
                            text: backend && backend.isSummarizing ? "🤖 总结中..." : "🤖 DeepSeek总结"
                            font.pixelSize: Theme.fonts.normal
                            font.family: Theme.fonts.family
                            enabled: backend && inputArea.text.trim().length > 0 && !backend.isRecording && !backend.isSummarizing  // 有内容且不在录音和总结时才启用
                            
                            background: Rectangle {
                                color: deepseekButton.pressed ? "#5e35b1" : 
                                       deepseekButton.hovered ? "#7e57c2" : "#9c27b0"
                                border.color: "#7b1fa2"
                                border.width: 1
                                radius: Theme.radius.normal
                                opacity: deepseekButton.enabled ? 1.0 : 0.5
                                
                                Behavior on color {
                                    ColorAnimation {
                                        duration: Theme.animation.fast
                                        easing.type: Easing.OutQuad
                                    }
                                }
                                
                                Behavior on opacity {
                                    NumberAnimation {
                                        duration: Theme.animation.fast
                                        easing.type: Easing.OutQuad
                                    }
                                }
                            }
                            
                            contentItem: Item {
                                anchors.fill: parent
                                
                                Text {
                                    id: buttonText
                                    text: deepseekButton.text
                                    font: deepseekButton.font
                                    opacity: enabled ? 1.0 : 0.5
                                    color: Theme.colors.textOnPrimary
                                    anchors.centerIn: parent
                                    anchors.horizontalCenterOffset: (loadingIndicator.visible ? -10 : 0)
                                    elide: Text.ElideRight
                                    
                                    Behavior on anchors.horizontalCenterOffset {
                                        NumberAnimation {
                                            duration: Theme.animation.fast
                                            easing.type: Easing.OutQuad
                                        }
                                    }
                                }
                                
                                // 加载动画指示器
                                Rectangle {
                                    id: loadingIndicator
                                    width: 16
                                    height: 16
                                    radius: 8
                                    color: "transparent"
                                    border.color: Theme.colors.textOnPrimary
                                    border.width: 2
                                    visible: backend && backend.isSummarizing
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.left: buttonText.right
                                    anchors.leftMargin: 6
                                    
                                    Rectangle {
                                        width: 4
                                        height: 4
                                        radius: 2
                                        color: Theme.colors.textOnPrimary
                                        anchors.centerIn: parent
                                        
                                        SequentialAnimation on rotation {
                                            running: parent.visible
                                            loops: Animation.Infinite
                                            NumberAnimation { from: 0; to: 360; duration: 1000 }
                                        }
                                        
                                        SequentialAnimation on opacity {
                                            running: parent.visible
                                            loops: Animation.Infinite
                                            NumberAnimation { from: 0.3; to: 1.0; duration: 500 }
                                            NumberAnimation { from: 1.0; to: 0.3; duration: 500 }
                                        }
                                    }
                                }
                            }
                            
                            onClicked: {
                                if (backend && inputArea.text.trim().length > 0 && !backend.isSummarizing) {
                                    backend.startDeepSeekSummary(inputArea.text)
                                }
                            }
                        }
                        
                            // 语音设置按钮
                            Button {
                                id: voiceSettingsButton
                                Layout.fillWidth: true
                                text: "⚙️ 语音设置"
                                font.pixelSize: Theme.fonts.small
                                font.family: Theme.fonts.family
                                enabled: backend && !backend.isRecording  // 录音时禁用
                                visible: false  // 隐藏语音设置按钮
                                
                                background: Rectangle {
                                    color: voiceSettingsButton.pressed ? "#e9ecef" : 
                                           voiceSettingsButton.hovered ? "#f8f9fa" : "#ffffff"
                                    border.color: "#dee2e6"
                                    border.width: 1
                                    radius: Theme.radius.normal
                                    opacity: voiceSettingsButton.enabled ? 1.0 : 0.5
                                    
                                    Behavior on color {
                                        ColorAnimation {
                                            duration: Theme.animation.fast
                                            easing.type: Easing.OutQuad
                                        }
                                    }
                                }
                                
                                contentItem: Text {
                                    text: voiceSettingsButton.text
                                    font: voiceSettingsButton.font
                                    opacity: enabled ? 1.0 : 0.5
                                    color: "#495057"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                
                                onClicked: {
                                    if (backend) backend.openVoiceSettings()
                                }
                            }
                            
                            // 发送按钮
                            Button {
                                id: sendButton
                                Layout.fillWidth: true
                                Layout.preferredHeight: 48  // Send按钮稍微高一些，作为主要操作按钮
                            text: "📤 Send (Ctrl+E)"
                                font.bold: true
                                font.pixelSize: Theme.fonts.normal
                                font.family: Theme.fonts.family
                                
                                background: Rectangle {
                                    color: sendButton.pressed ? Theme.colors.primaryDark : 
                                           sendButton.hovered ? Theme.colors.primaryDark : Theme.colors.primary
                                    radius: Theme.radius.normal
                                    
                                    Behavior on color {
                                        ColorAnimation {
                                            duration: Theme.animation.fast
                                            easing.type: Easing.OutQuad
                                        }
                                    }
                                }
                                
                                contentItem: Text {
                                    text: sendButton.text
                                    font: sendButton.font
                                    opacity: enabled ? 1.0 : 0.3
                                    color: Theme.colors.textOnPrimary
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                
                                onClicked: {
                                    if (!backend) return
                                    
                                    var feedbackText = inputArea.text
                                    if (commitCheckbox.checked) {
                                        feedbackText = "请只 commit 你刚才修改的文件，按规范撰写 commit 信息。 注意⚠️：之后不要自己 commit\n\n接下来实现：\n" + feedbackText
                                        // 发送后自动取消Commit复选框的选中状态
                                        commitCheckbox.checked = false
                                    }
                                    backend.sendResponse(feedbackText)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    // 连接后端信号
    Connections {
        target: backend
        
        function onTodoContentInserted(content) {
            if (inputArea.text.trim() !== "") {
                inputArea.text += "\n\n" + content
            } else {
                inputArea.text = content
            }
            inputArea.forceActiveFocus()
            // 将光标移动到输入结果的末尾
            inputArea.cursorPosition = inputArea.length
        }
        
        function onVoiceTranscriptionReady(transcription) {
            if (transcription.trim() !== "") {
                if (inputArea.text.trim() !== "") {
                    inputArea.text += "\n\n" + transcription
                } else {
                    inputArea.text = transcription
                }
                inputArea.forceActiveFocus()
                // 将光标移动到输入结果的末尾
                inputArea.cursorPosition = inputArea.length
            }
        }
        
        function onVoiceTranscriptionChunkReady(chunk) {
            // 传统录音模式不支持实时转写片段，此方法保留但不执行任何操作
            console.log("传统录音模式收到转写片段（忽略）:", chunk)
        }
        
        function onVoiceCommandDetected(commandType, text) {
            if (commandType === "send") {
                // 检测到发送命令，自动点击发送按钮
                console.log("检测到发送命令:", text)
                // 延迟一下，确保转写完成
                sendDelayTimer.start()
            } else if (commandType === "stop") {
                console.log("检测到停止命令:", text)
                // 停止命令已经在后端处理了，这里可以显示提示
            }
        }
        
        function onVoiceErrorOccurred(errorMessage) {
            console.log("语音错误:", errorMessage)
            // 可以在这里添加错误提示UI
        }
        
        function onApiKeyMissingWarning() {
            // 显示API Key缺失警告对话框
            apiKeyWarningDialog.open()
        }
        
        function onDeepseekSummaryReady(summary) {
            // DeepSeek总结完成，更新输入框内容
            console.log("DeepSeek总结完成:", summary.length, "字符")
            inputArea.text = summary
            inputArea.forceActiveFocus()
            // 将光标移动到总结内容的末尾
            inputArea.cursorPosition = inputArea.length
        }
        
        function onDeepseekSummaryError(errorMessage) {
            // DeepSeek总结出错，显示错误信息
            console.log("DeepSeek总结错误:", errorMessage)
            // 可以在这里添加错误提示UI，比如短暂显示错误消息
            // 暂时在控制台显示错误
        }
    }
    
    // 添加延迟发送定时器
    Timer {
        id: sendDelayTimer
        interval: 500  // 500ms 延迟
        onTriggered: {
            if (backend) {
                var currentText = backend.getCurrentTranscription()
                if (currentText.trim() !== "") {
                    backend.sendResponse(currentText)
                }
            }
        }
    }
    
    // 保存窗口几何信息
    onXChanged: saveGeometry()
    onYChanged: saveGeometry()
    onWidthChanged: saveGeometry()
    onHeightChanged: saveGeometry()
    
    // 窗口关闭时保存几何信息
    onClosing: {
        if (backend) {
            backend.saveWindowGeometry(x, y, width, height)
        }
    }
    
    function saveGeometry() {
        if (backend && visible) {
            // 使用定时器延迟保存，避免频繁调用
            saveTimer.restart()
        }
    }
    
    Timer {
        id: saveTimer
        interval: 500  // 500ms 延迟
        onTriggered: {
            if (backend) {
                backend.saveWindowGeometry(window.x, window.y, window.width, window.height)
            }
        }
    }
    
    // API Key 缺失警告对话框
    Dialog {
        id: apiKeyWarningDialog
        title: "⚠️ 需要配置 API Key"
        modal: true
        anchors.centerIn: parent
        width: Math.min(400, parent.width * 0.8)
        height: Math.min(200, parent.height * 0.6)
        
        background: Rectangle {
            color: Theme.colors.background
            border.color: Theme.colors.border
            border.width: 1
            radius: Theme.radius.medium
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Theme.spacing.normal
            spacing: Theme.spacing.normal
            
            Text {
                Layout.fillWidth: true
                text: "语音功能需要配置 OpenAI API Key 才能使用。\n\n请按 Ctrl+, 打开设置窗口配置 API Key。"
                wrapMode: Text.WordWrap
                font.pixelSize: Theme.fonts.normal
                font.family: Theme.fonts.family
                color: Theme.colors.text
                horizontalAlignment: Text.AlignHCenter
            }
            
            RowLayout {
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignCenter
                spacing: Theme.spacing.normal
                
                Button {
                    text: "📝 打开设置"
                    font.pixelSize: Theme.fonts.normal
                    font.family: Theme.fonts.family
                    
                    background: Rectangle {
                        color: parent.pressed ? Theme.colors.primaryDark : 
                               parent.hovered ? Theme.colors.primaryDark : Theme.colors.primary
                        radius: Theme.radius.normal
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        font: parent.font
                        color: Theme.colors.textOnPrimary
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        apiKeyWarningDialog.close()
                        if (backend) {
                            backend.openSettings()
                        }
                    }
                }
                
                Button {
                    text: "取消"
                    font.pixelSize: Theme.fonts.normal
                    font.family: Theme.fonts.family
                    
                    background: Rectangle {
                        color: parent.pressed ? "#e9ecef" : 
                               parent.hovered ? "#f8f9fa" : "#ffffff"
                        border.color: Theme.colors.border
                        border.width: 1
                        radius: Theme.radius.normal
                    }
                    
                    contentItem: Text {
                        text: parent.text
                        font: parent.font
                        color: Theme.colors.text
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    
                    onClicked: {
                        apiKeyWarningDialog.close()
                    }
                }
            }
        }
    }
} 
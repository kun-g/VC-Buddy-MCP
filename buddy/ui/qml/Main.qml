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
    }
    
    title: backend ? backend.windowTitle : "Answer Box"
    
    // 窗口置顶设置
    flags: backend && backend.stayOnTop ? Qt.WindowStaysOnTopHint | Qt.Window : Qt.Window
    
    // Material 主题设置
    Material.theme: Material.Light
    Material.accent: Theme.colors.primary
    
    // 主布局
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.medium
        spacing: Theme.spacing.medium
        
        // 摘要显示区域
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 100
            color: Theme.colors.backgroundSecondary
            border.color: Theme.colors.borderDark
            border.width: 1
            radius: Theme.radius.medium
            
            ScrollView {
                anchors.fill: parent
                anchors.margins: Theme.spacing.normal
                
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
        
        // 主内容区域 - 分割器
        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Horizontal
            
            // 左侧：TODO树状视图
            Rectangle {
                SplitView.preferredWidth: 200
                SplitView.minimumWidth: 150
                color: Theme.colors.background
                border.color: Theme.colors.borderDark
                border.width: 1
                radius: Theme.radius.medium
                
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
                        
                        ListView {
                            id: todoListView
                            model: backend ? backend.todoModel : null
                            
                            delegate: TodoItemDelegate {
                                width: todoListView.width
                                todoItem: model.todoItem
                                onItemClicked: {
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
                        
                        visible: backend && backend.hasTodos
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: Theme.spacing.normal
                            spacing: Theme.spacing.small
                            
                            Text {
                                text: "📄 任务详情:"
                                font.bold: true
                                font.pixelSize: Theme.fonts.medium
                                font.family: Theme.fonts.family
                                color: Theme.colors.text
                            }
                            
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
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
                        
                        Text {
                            text: "💬 反馈内容:"
                            font.bold: true
                            font.pixelSize: Theme.fonts.medium
                            font.family: Theme.fonts.family
                            color: Theme.colors.text
                        }
                        
                        ScrollView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            
                            TextArea {
                                id: inputArea
                                placeholderText: "请输入您的反馈..."
                                wrapMode: TextArea.Wrap
                                font.pixelSize: Theme.fonts.normal
                                font.family: Theme.fonts.family
                                selectByMouse: true
                                color: Theme.colors.text
                                
                                background: Rectangle {
                                    color: Theme.colors.background
                                    border.color: Theme.colors.border
                                    border.width: 1
                                    radius: Theme.radius.normal
                                }
                                
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
                        
                        // Commit复选框
                        CheckBox {
                            id: commitCheckbox
                            text: "📝 Commit - 要求先提交修改的文件"
                            font.pixelSize: Theme.fonts.small
                            font.family: Theme.fonts.family
                        }
                        
                        // 发送按钮
                        Button {
                            id: sendButton
                            Layout.fillWidth: true
                            text: "📤 Send (Ctrl+Enter)"
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
                                    feedbackText = "请 commit 你修改的文件，按规范撰写 commit 信息\n\n接下来实现：\n" + feedbackText
                                }
                                backend.sendResponse(feedbackText)
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
} 
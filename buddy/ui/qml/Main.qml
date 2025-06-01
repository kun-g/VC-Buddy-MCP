import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: window
    visible: true
    width: backend ? backend.defaultWidth : 400
    height: backend ? backend.defaultHeight : 600
    title: backend ? backend.windowTitle : "Answer Box"
    
    // 窗口置顶设置
    flags: backend && backend.stayOnTop ? Qt.WindowStaysOnTopHint | Qt.Window : Qt.Window
    
    property QtObject backend
    property string currentTime: "00:00:00"
    
    // 主布局
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 12
        
        // 摘要显示区域
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 100
            color: "#f0f0f0"
            border.color: "#d0d0d0"
            border.width: 1
            radius: 5
            
            ScrollView {
                anchors.fill: parent
                anchors.margins: 8
                
                Text {
                    id: summaryText
                    width: parent.width
                    text: backend ? backend.summaryText : "无任务摘要"
                    wrapMode: Text.WordWrap
                    font.pixelSize: 12
                    color: "#333"
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
                color: "white"
                border.color: "#d0d0d0"
                border.width: 1
                radius: 5
                
                visible: backend && backend.hasTodos
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 4
                    
                    Text {
                        text: "📝 TODO 任务"
                        font.bold: true
                        color: "#333"
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
                    spacing: 8
                    
                    // TODO详情显示（仅在有TODO时显示）
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 150
                        color: "#fafafa"
                        border.color: "#d0d0d0"
                        border.width: 1
                        radius: 5
                        
                        visible: backend && backend.hasTodos
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 8
                            spacing: 4
                            
                            Text {
                                text: "📄 任务详情:"
                                font.bold: true
                                color: "#333"
                            }
                            
                            ScrollView {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                
                                Text {
                                    id: todoDetailText
                                    width: parent.width
                                    text: backend ? backend.selectedTodoDetail : "选择一个任务查看详情"
                                    wrapMode: Text.WordWrap
                                    font.pixelSize: 11
                                    color: "#666"
                                }
                            }
                        }
                    }
                    
                    // 输入区域
                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 4
                        
                        Text {
                            text: "💬 反馈内容:"
                            font.bold: true
                            color: "#333"
                        }
                        
                        ScrollView {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            
                            TextArea {
                                id: inputArea
                                placeholderText: "请输入您的反馈..."
                                wrapMode: TextArea.Wrap
                                font.pixelSize: 12
                                selectByMouse: true
                                
                                background: Rectangle {
                                    color: "white"
                                    border.color: inputArea.activeFocus ? "#2196f3" : "#d0d0d0"
                                    border.width: inputArea.activeFocus ? 2 : 1
                                    radius: 5
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
                            font.pixelSize: 11
                            
                            indicator: Rectangle {
                                implicitWidth: 16
                                implicitHeight: 16
                                x: commitCheckbox.leftPadding
                                y: parent.height / 2 - height / 2
                                radius: 3
                                border.color: commitCheckbox.checked ? "#2196f3" : "#ccc"
                                border.width: 2
                                color: commitCheckbox.checked ? "#2196f3" : "white"
                                
                                Text {
                                    anchors.centerIn: parent
                                    text: "✓"
                                    color: "white"
                                    font.pixelSize: 10
                                    visible: commitCheckbox.checked
                                }
                            }
                        }
                        
                        // 发送按钮
                        Button {
                            id: sendButton
                            Layout.fillWidth: true
                            text: "📤 Send (Ctrl+Enter)"
                            font.bold: true
                            
                            background: Rectangle {
                                color: sendButton.pressed ? "#0d47a1" : (sendButton.hovered ? "#1976d2" : "#2196f3")
                                radius: 5
                                
                                Behavior on color {
                                    ColorAnimation { duration: 150 }
                                }
                            }
                            
                            contentItem: Text {
                                text: sendButton.text
                                font: sendButton.font
                                color: "white"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
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
} 
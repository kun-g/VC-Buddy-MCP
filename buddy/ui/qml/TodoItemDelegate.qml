import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "."

Item {
    id: root
    height: contentColumn.height + Theme.spacing.normal
    
    property var todoItem: modelData.todoItem
    property int indentLevel: todoItem ? todoItem.level - 1 : 0
    
    signal itemClicked()
    signal itemDoubleClicked()
    signal markDone()
    signal markUndone()
    
    Rectangle {
        anchors.fill: parent
        color: mouseArea.containsMouse ? Theme.colors.hover : "transparent"
        border.color: Theme.colors.borderLight
        border.width: 1
        radius: Theme.radius.small
        
        // 完成状态的背景色
        states: [
            State {
                name: "completed"
                when: todoItem && todoItem.is_done
                PropertyChanges {
                    target: root.children[0]  // Rectangle 组件
                    color: Theme.colors.todoCompleted
                    border.color: Theme.colors.todoCompletedBorder
                }
            }
        ]
        
        transitions: Transition {
            ColorAnimation {
                duration: Theme.animation.fast
                easing.type: Easing.OutQuad
            }
        }
        
        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            
            onClicked: function(mouse) {
                if (mouse.button === Qt.LeftButton) {
                    root.itemClicked()
                } else if (mouse.button === Qt.RightButton) {
                    contextMenu.popup()
                }
            }
            onDoubleClicked: root.itemDoubleClicked()
        }
        
        // 右键菜单
        Menu {
            id: contextMenu
            
            background: Rectangle {
                color: Theme.colors.background
                border.color: Theme.colors.border
                border.width: 1
                radius: Theme.radius.normal
            }
            
            MenuItem {
                text: todoItem && todoItem.is_done ? "❌ 标记为未完成" : "✅ 标记为完成"
                font.pixelSize: Theme.fonts.small
                font.family: Theme.fonts.family
                
                background: Rectangle {
                    color: parent.hovered ? Theme.colors.hover : "transparent"
                    radius: Theme.radius.small
                }
                
                onTriggered: {
                    if (todoItem && todoItem.is_done) {
                        root.markUndone()
                    } else {
                        root.markDone()
                    }
                }
            }
        }
        
        ColumnLayout {
            id: contentColumn
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: Theme.spacing.small
            anchors.leftMargin: Theme.spacing.small + (indentLevel * Theme.spacing.large)
            spacing: Theme.spacing.tiny
            
            // 标题行
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.small
                
                // 层级指示器
                Repeater {
                    model: indentLevel
                    Rectangle {
                        width: 2
                        height: Theme.spacing.large
                        color: Theme.colors.border
                    }
                }
                
                // 标题文本
                Text {
                    Layout.fillWidth: true
                    text: todoItem ? todoItem.display_title : "加载中..."
                    font.pixelSize: Theme.fonts.normal
                    font.family: Theme.fonts.family
                    font.bold: indentLevel === 0
                    color: Theme.colors.text
                    wrapMode: Text.WordWrap
                }
                
                // 完成状态指示器
                Rectangle {
                    width: Theme.spacing.normal
                    height: Theme.spacing.normal
                    radius: Theme.spacing.small
                    color: todoItem && todoItem.is_done ? Theme.colors.success : Theme.colors.disabled
                    visible: todoItem && todoItem.attributes && Object.keys(todoItem.attributes).length > 0
                    
                    Behavior on color {
                        ColorAnimation {
                            duration: Theme.animation.fast
                            easing.type: Easing.OutQuad
                        }
                    }
                }
            }
            
            // 属性显示
            Repeater {
                model: {
                    if (todoItem && todoItem.attributes) {
                        return Object.keys(todoItem.attributes)
                    }
                    return []
                }
                
                RowLayout {
                    Layout.fillWidth: true
                    Layout.leftMargin: indentLevel * Theme.spacing.large
                    spacing: Theme.spacing.small
                    
                    Text {
                        text: "📌"
                        font.pixelSize: Theme.fonts.small
                        color: Theme.colors.textSecondary
                    }
                    
                    Text {
                        text: modelData + ":"
                        font.pixelSize: Theme.fonts.small
                        font.family: Theme.fonts.family
                        font.bold: true
                        color: Theme.colors.textSecondary
                    }
                    
                    Text {
                        Layout.fillWidth: true
                        text: todoItem && todoItem.attributes ? todoItem.attributes[modelData] : ""
                        font.pixelSize: Theme.fonts.small
                        font.family: Theme.fonts.family
                        color: Theme.colors.textHint
                        wrapMode: Text.WordWrap
                    }
                }
            }
            
            // 内容预览（如果有的话）
            Text {
                Layout.fillWidth: true
                Layout.leftMargin: indentLevel * Theme.spacing.large
                text: {
                    if (todoItem && todoItem.content) {
                        var content = todoItem.content.toString()
                        return content.length > 100 ? content.substring(0, 100) + "..." : content
                    }
                    return ""
                }
                font.pixelSize: Theme.fonts.small
                font.family: Theme.fonts.family
                color: Theme.colors.textSecondary
                wrapMode: Text.WordWrap
                visible: todoItem && todoItem.content && todoItem.content.toString().trim() !== ""
            }
        }
    }
} 
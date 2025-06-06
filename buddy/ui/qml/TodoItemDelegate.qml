import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects
import "."

Item {
    id: root
    height: contentColumn.height + Theme.spacing.normal
    
    property var todoItem: null
    property int indentLevel: todoItem ? todoItem.level - 1 : 0
    property bool isSelected: false
    
    signal itemClicked()
    signal itemDoubleClicked()
    signal markDone()
    signal markUndone()
    signal deleteTodo()
    
    // 右键菜单 - 使用 Popup 替代 Menu
    Popup {
        id: contextMenu
        width: 160
        height: menuColumn.height + 16
        padding: 8
        
        background: Rectangle {
            color: Theme.colors.background
            border.color: Theme.colors.border
            border.width: 1
            radius: Theme.radius.normal
            
            // 添加阴影效果
            layer.enabled: true
            layer.effect: DropShadow {
                horizontalOffset: 0
                verticalOffset: 2
                radius: 8
                samples: 16
                color: "#20000000"
            }
        }
        
        Column {
            id: menuColumn
            width: parent.width - 16
            spacing: 2
            
            Rectangle {
                width: parent.width
                height: 24
                color: markMouseArea.containsMouse ? Theme.colors.hover : "transparent"
                radius: Theme.radius.small
                
                Text {
                    anchors.left: parent.left
                    anchors.leftMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    text: todoItem && todoItem.is_done ? "❌ 标记未完成" : "✅ 标记完成"
                    font.pixelSize: Theme.fonts.small
                    font.family: Theme.fonts.family
                    color: Theme.colors.text
                }
                
                MouseArea {
                    id: markMouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        console.log("DEBUG: 菜单项被触发，当前状态:", todoItem ? todoItem.is_done : "无数据")
                        contextMenu.close()
                        if (todoItem && todoItem.is_done) {
                            root.markUndone()
                        } else {
                            root.markDone()
                        }
                    }
                }
            }
            
            // 删除菜单项（仅对已完成的TODO显示）
            Rectangle {
                width: parent.width
                height: 24
                color: deleteMouseArea.containsMouse ? Theme.colors.hover : "transparent"
                radius: Theme.radius.small
                visible: todoItem && todoItem.is_done
                
                Text {
                    anchors.left: parent.left
                    anchors.leftMargin: 8
                    anchors.verticalCenter: parent.verticalCenter
                    text: "🗑️ 删除"
                    font.pixelSize: Theme.fonts.small
                    font.family: Theme.fonts.family
                    color: Theme.colors.error
                }
                
                MouseArea {
                    id: deleteMouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        console.log("DEBUG: 删除TODO项目")
                        contextMenu.close()
                        root.deleteTodo()
                    }
                }
            }
        }
    }
    
    Rectangle {
        id: backgroundRect
        anchors.fill: parent
        color: mouseArea.containsMouse ? Theme.colors.hover : "transparent"
        border.color: Theme.colors.borderLight
        border.width: 1
        radius: Theme.radius.small
        
        // 状态管理
        states: [
            State {
                name: "selected"
                when: isSelected
                PropertyChanges {
                    target: backgroundRect
                    color: Theme.colors.todoSelected
                    border.color: Theme.colors.todoSelectedBorder
                }
            },
            State {
                name: "completed"
                when: todoItem && todoItem.is_done && !isSelected
                PropertyChanges {
                    target: backgroundRect
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
                    console.log("DEBUG: 右键点击 TODO 项目，准备弹出菜单")
                    contextMenu.x = mouse.x
                    contextMenu.y = mouse.y
                    contextMenu.open()
                }
            }
            onDoubleClicked: root.itemDoubleClicked()
        }
        
        ColumnLayout {
            id: contentColumn
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: Theme.spacing.small
            anchors.leftMargin: Theme.spacing.small + (indentLevel * Theme.spacing.large)
            spacing: Theme.spacing.tiny
            
            // 标题行（简化版，只显示标题）
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
                
                // 完成状态指示器（简化版）
                Rectangle {
                    width: Theme.spacing.normal
                    height: Theme.spacing.normal
                    radius: Theme.spacing.small
                    color: todoItem && todoItem.is_done ? Theme.colors.success : Theme.colors.disabled
                    visible: todoItem
                    
                    Behavior on color {
                        ColorAnimation {
                            duration: Theme.animation.fast
                            easing.type: Easing.OutQuad
                        }
                    }
                }
            }
        }
    }
} 
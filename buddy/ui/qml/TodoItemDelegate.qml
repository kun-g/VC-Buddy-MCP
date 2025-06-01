import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    height: contentColumn.height + 8
    
    property var todoItem
    property int indentLevel: todoItem ? todoItem.level - 1 : 0
    
    signal itemClicked()
    signal itemDoubleClicked()
    
    Rectangle {
        anchors.fill: parent
        color: mouseArea.containsMouse ? "#f5f5f5" : "transparent"
        border.color: "#f0f0f0"
        border.width: 1
        radius: 3
        
        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            
            onClicked: root.itemClicked()
            onDoubleClicked: root.itemDoubleClicked()
        }
        
        ColumnLayout {
            id: contentColumn
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 4
            anchors.leftMargin: 4 + (indentLevel * 16)
            spacing: 2
            
            // 标题行
            RowLayout {
                Layout.fillWidth: true
                spacing: 4
                
                // 层级指示器
                Repeater {
                    model: indentLevel
                    Rectangle {
                        width: 2
                        height: 16
                        color: "#ddd"
                    }
                }
                
                // 标题文本
                Text {
                    Layout.fillWidth: true
                    text: todoItem ? todoItem.display_title : ""
                    font.pixelSize: 12
                    font.bold: indentLevel === 0
                    color: "#333"
                    wrapMode: Text.WordWrap
                }
                
                // 完成状态指示器
                Rectangle {
                    width: 8
                    height: 8
                    radius: 4
                    color: todoItem && todoItem.is_done ? "#4caf50" : "#ccc"
                    visible: todoItem && todoItem.attributes && Object.keys(todoItem.attributes).length > 0
                }
            }
            
            // 属性显示
            Repeater {
                model: todoItem && todoItem.attributes ? Object.keys(todoItem.attributes) : []
                
                RowLayout {
                    Layout.fillWidth: true
                    Layout.leftMargin: indentLevel * 16
                    spacing: 4
                    
                    Text {
                        text: "📌"
                        font.pixelSize: 10
                        color: "#666"
                    }
                    
                    Text {
                        text: modelData + ":"
                        font.pixelSize: 10
                        font.bold: true
                        color: "#666"
                    }
                    
                    Text {
                        Layout.fillWidth: true
                        text: todoItem.attributes[modelData]
                        font.pixelSize: 10
                        color: "#888"
                        wrapMode: Text.WordWrap
                    }
                }
            }
            
            // 内容预览（如果有的话）
            Text {
                Layout.fillWidth: true
                Layout.leftMargin: indentLevel * 16
                text: todoItem && todoItem.content ? todoItem.content.substring(0, 100) + (todoItem.content.length > 100 ? "..." : "") : ""
                font.pixelSize: 10
                color: "#666"
                wrapMode: Text.WordWrap
                visible: todoItem && todoItem.content && todoItem.content.trim() !== ""
            }
        }
    }
} 
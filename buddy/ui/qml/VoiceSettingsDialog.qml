import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtQuick.Controls.Material 2.15
import "."

Window {
    id: voiceSettingsWindow
    
    title: "语音设置"
    width: 500
    height: 600
    minimumWidth: 450
    minimumHeight: 550
    
    modality: Qt.ApplicationModal
    
    // Material 主题设置
    Material.theme: Material.Light
    Material.accent: Theme.colors.primary
    
    // 信号定义
    signal accepted()
    signal rejected()
    signal settingsSaved(var stopCommands, var sendCommands)
    
    property var configManager: null
    property string stopCommandsText: ""
    property string sendCommandsText: ""
    
    Component.onCompleted: {
        loadSettings()
    }
    
    function loadSettings() {
        if (configManager) {
            var stopCommands = configManager.get("voice.stop_commands", [])
            var sendCommands = configManager.get("voice.send_commands", [])
            
            if (stopCommands && stopCommands.length > 0) {
                stopCommandsText = stopCommands.join("\n")
            }
            if (sendCommands && sendCommands.length > 0) {
                sendCommandsText = sendCommands.join("\n")
            }
        }
    }
    
    function saveSettings() {
        var stopText = stopCommandsArea.text.trim()
        var sendText = sendCommandsArea.text.trim()
        
        var stopCommands = stopText ? stopText.split('\n').map(function(cmd) { 
            return cmd.trim() 
        }).filter(function(cmd) { 
            return cmd.length > 0 
        }) : []
        
        var sendCommands = sendText ? sendText.split('\n').map(function(cmd) { 
            return cmd.trim() 
        }).filter(function(cmd) { 
            return cmd.length > 0 
        }) : []
        
        if (stopCommands.length === 0 && sendCommands.length === 0) {
            warningDialog.open()
            return false
        }
        
        if (configManager) {
            configManager.set("voice.stop_commands", stopCommands)
            configManager.set("voice.send_commands", sendCommands)
            configManager.save_config()
        }
        
        settingsSaved(stopCommands, sendCommands)
        accepted()
        close()
        return true
    }
    
    function resetToDefaults() {
        stopCommandsArea.text = "我说完了\n说完了\n结束\n停止录音\n停止\nfinish\ndone\nstop\nend"
        sendCommandsArea.text = "开工吧\n发送\n提交\n执行\n开始干活\n开始工作\nsend\nsubmit\ngo\nexecute\nlet's go"
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 20
        
        // 标题
        Text {
            Layout.fillWidth: true
            text: "语音识别设置"
            font.pixelSize: Theme.fonts.xxlarge
            font.bold: true
            font.family: Theme.fonts.family
            color: Theme.colors.text
            horizontalAlignment: Text.AlignHCenter
        }
        
        // 说明文字
        Text {
            Layout.fillWidth: true
            text: "配置语音识别的自定义命令。支持中文和英文命令。\n录音时说出这些命令会触发相应的操作。"
            font.pixelSize: Theme.fonts.normal
            font.family: Theme.fonts.family
            color: Theme.colors.textSecondary
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
        }
        
        // 选项卡容器
        TabBar {
            id: tabBar
            Layout.fillWidth: true
            
            TabButton {
                text: "停止录音命令"
                font.pixelSize: Theme.fonts.normal
                font.family: Theme.fonts.family
            }
            
            TabButton {
                text: "发送命令"
                font.pixelSize: Theme.fonts.normal
                font.family: Theme.fonts.family
            }
        }
        
        // 选项卡内容
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex
            
            // 停止命令选项卡
            ColumnLayout {
                spacing: 10
                
                Text {
                    Layout.fillWidth: true
                    text: "说出以下任意命令将停止录音：\n每行一个命令，支持中英文混合"
                    font.pixelSize: Theme.fonts.small
                    font.family: Theme.fonts.family
                    color: Theme.colors.textSecondary
                    wrapMode: Text.WordWrap
                }
                
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    
                    TextArea {
                        id: stopCommandsArea
                        placeholderText: "我说完了\n说完了\n结束\n停止录音\n停止\nfinish\ndone\nstop\nend"
                        text: stopCommandsText
                        font.pixelSize: Theme.fonts.normal
                        font.family: Theme.fonts.family
                        color: Theme.colors.text
                        selectByMouse: true
                        
                        background: Rectangle {
                            color: Theme.colors.background
                            border.color: stopCommandsArea.activeFocus ? Theme.colors.primary : Theme.colors.border
                            border.width: 1
                            radius: Theme.radius.normal
                        }
                    }
                }
            }
            
            // 发送命令选项卡
            ColumnLayout {
                spacing: 10
                
                Text {
                    Layout.fillWidth: true
                    text: "说出以下任意命令将停止录音并自动发送：\n每行一个命令，支持中英文混合"
                    font.pixelSize: Theme.fonts.small
                    font.family: Theme.fonts.family
                    color: Theme.colors.textSecondary
                    wrapMode: Text.WordWrap
                }
                
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    
                    TextArea {
                        id: sendCommandsArea
                        placeholderText: "开工吧\n发送\n提交\n执行\n开始干活\n开始工作\nsend\nsubmit\ngo\nexecute\nlet's go"
                        text: sendCommandsText
                        font.pixelSize: Theme.fonts.normal
                        font.family: Theme.fonts.family
                        color: Theme.colors.text
                        selectByMouse: true
                        
                        background: Rectangle {
                            color: Theme.colors.background
                            border.color: sendCommandsArea.activeFocus ? Theme.colors.primary : Theme.colors.border
                            border.width: 1
                            radius: Theme.radius.normal
                        }
                    }
                }
            }
        }
        
        // 按钮区域
        RowLayout {
            Layout.fillWidth: true
            
            Item {
                Layout.fillWidth: true
            }
            
            // 重置按钮
            Button {
                text: "重置为默认"
                font.pixelSize: Theme.fonts.normal
                font.family: Theme.fonts.family
                
                background: Rectangle {
                    color: parent.pressed ? "#e9ecef" : parent.hovered ? "#f8f9fa" : "#ffffff"
                    border.color: "#dee2e6"
                    border.width: 1
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
                    color: "#495057"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                
                onClicked: resetConfirmDialog.open()
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
    
    // 警告对话框
    Dialog {
        id: warningDialog
        title: "警告"
        parent: Overlay.overlay
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        width: 300
        modal: true
        
        Label {
            text: "至少需要设置一个停止命令或发送命令！"
            font.pixelSize: Theme.fonts.normal
            font.family: Theme.fonts.family
            wrapMode: Text.WordWrap
        }
        
        standardButtons: Dialog.Ok
    }
    
    // 重置确认对话框
    Dialog {
        id: resetConfirmDialog
        title: "确认重置"
        parent: Overlay.overlay
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        width: 300
        modal: true
        
        Label {
            text: "确定要重置为默认的语音命令吗？"
            font.pixelSize: Theme.fonts.normal
            font.family: Theme.fonts.family
            wrapMode: Text.WordWrap
        }
        
        standardButtons: Dialog.Yes | Dialog.No
        
        onAccepted: resetToDefaults()
    }
} 
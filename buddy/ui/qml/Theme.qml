pragma Singleton
import QtQuick 2.15

QtObject {
    id: theme
    
    // 颜色方案
    readonly property QtObject colors: QtObject {
        // 主色调
        readonly property color primary: "#2196F3"
        readonly property color primaryDark: "#1976D2"
        readonly property color primaryLight: "#E3F2FD"
        
        // 背景色
        readonly property color background: "#FFFFFF"
        readonly property color backgroundSecondary: "#F5F5F5"
        readonly property color surface: "#FAFAFA"
        
        // 边框色
        readonly property color border: "#E0E0E0"
        readonly property color borderLight: "#F0F0F0"
        readonly property color borderDark: "#D0D0D0"
        
        // 文本色
        readonly property color text: "#212121"
        readonly property color textSecondary: "#757575"
        readonly property color textHint: "#9E9E9E"
        readonly property color textOnPrimary: "#FFFFFF"
        
        // 状态色
        readonly property color success: "#4CAF50"
        readonly property color warning: "#FF9800"
        readonly property color error: "#F44336"
        readonly property color info: "#2196F3"
        
        // 交互色
        readonly property color hover: "#F5F5F5"
        readonly property color pressed: "#E0E0E0"
        readonly property color selected: "#E3F2FD"
        readonly property color disabled: "#BDBDBD"
        
        // TODO 特定颜色
        readonly property color todoBackground: "#FFFFFF"
        readonly property color todoHover: "#F5F5F5"
        readonly property color todoCompleted: "#E8F5E8"
        readonly property color todoCompletedBorder: "#4CAF50"
    }
    
    // 字体
    readonly property QtObject fonts: QtObject {
        readonly property string family: "Segoe UI, Helvetica Neue, Arial, sans-serif"
        readonly property int small: 10
        readonly property int normal: 12
        readonly property int medium: 14
        readonly property int large: 16
        readonly property int xlarge: 18
        readonly property int xxlarge: 24
    }
    
    // 间距
    readonly property QtObject spacing: QtObject {
        readonly property int tiny: 2
        readonly property int small: 4
        readonly property int normal: 8
        readonly property int medium: 12
        readonly property int large: 16
        readonly property int xlarge: 24
        readonly property int xxlarge: 32
    }
    
    // 圆角
    readonly property QtObject radius: QtObject {
        readonly property int small: 3
        readonly property int normal: 4
        readonly property int medium: 5
        readonly property int large: 8
        readonly property int round: 50
    }
    
    // 阴影
    readonly property QtObject shadow: QtObject {
        readonly property color light: "#20000000"
        readonly property color normal: "#40000000"
        readonly property color dark: "#60000000"
    }
    
    // 动画
    readonly property QtObject animation: QtObject {
        readonly property int fast: 150
        readonly property int normal: 250
        readonly property int slow: 400
        readonly property string easing: "Quad"
    }
    
    // 尺寸
    readonly property QtObject sizes: QtObject {
        readonly property int buttonHeight: 32
        readonly property int inputHeight: 36
        readonly property int iconSize: 16
        readonly property int iconSizeMedium: 24
        readonly property int iconSizeLarge: 32
        readonly property int minTouchTarget: 44
    }
} 
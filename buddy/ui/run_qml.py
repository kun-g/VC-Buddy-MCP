#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QML版本的AnswerBox启动脚本
使用现代化的QML界面替代传统的QtWidgets
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from answer_box_qml import main

if __name__ == "__main__":
    sys.exit(main()) 
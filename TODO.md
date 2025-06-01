# TODO展示

## TODO支持属性
state=done

TODO 支持属性， 紧接着标题的赋值预计， 例如：
state=going
abc=123

## 完成的任务加个✅
state=done

## TODO没有内容时，就替换标题
state=done

TODO没有内容时， 双击时就插入标题

## 在 TODO 列表里右键完成的任务，在 TODO.md里这条前面加上✅
state=done

## BUG 完成状态不能正常显示
TODO加载时，不能正常显示完成状态。在 Answer Box 里操作的可以显示完成状态
我预期是这两种情况都能正常的显示完成状态。
补充一下，TODO Item 右键菜单表明完成状态是正确设置的

# 优化answer_box.py

## summary_display 要优化一下，以便阅读 AI 的工作总结

## Style Sheet 模块
实现一个 Style Sheet 模块，

## 引入QML
使用 QML 拆分逻辑和布局
如果需要，可以参考：
https://doc.qt.io/qtforpython-6/tutorials/qmlapp/qmlapplication.html

## 引入.qss
引入 .qss 拆分样式和布局
如果需要可以参考：
https://doc.qt.io/qt-6/stylesheet.html

# 初始化引导
引导设置 Cursor User Rules

# 单元测试

## 给 todo_parser.py 实现单元测试

# 语音输入
## 支持语音输入

# 支持 SSE 模式

# 设置许可证

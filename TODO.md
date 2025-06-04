# 文档维护

## 根据已完成任务更新文档
对于TODO项目根节点（#标记的），右键里有个更新文档按钮，可以根据整个节点下的已完成任务更新文档(PRD 等)

# 初始化引导
引导设置 Cursor User Rules

# 语音输入

## 支持流式语音输入
语音输入实现流式输入，边说边输入
你看一下 answer_box_qml.py 就知道了，有一个输入窗口
不需要语音输入的编辑功能，但是需要用户自定义结束语。比如「我说完了」就结束录音状态，「开工吧」，就直接把当前结果发送过去。

# 支持 SSE 模式

# 新手友好
make install 更智能一些，能根据系统安装额外的依赖
其他 make 不用每次都 install ，可以失败时

## 需要一个setup命令
需要一个命令来设置项目环境
比如npx vcbuddy setup .
就在当前目录设置cursor rule
测试一下没有

# Failed to track shortcut usage: attempted relative import with no known parent package

# 需要一个make 命令，走 main.py 以便测试完整流程

# TODO 完成状态的✅可以去掉了，那个绿色小点够清晰的
state=done

# TODO 双击时，如果有子任务，就把整个任务记录都贴到输入框（包括总任务）
state=done

# 输入框优化

## 输入框可以粘贴图片

## summary可以调高度
state=done

# 得搞个异常捕捉上报机制才行

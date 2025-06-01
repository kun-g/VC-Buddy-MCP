import sys
import json
from PySide6.QtWidgets import QApplication, QPushButton, QDialog, QLabel, QVBoxLayout, QTextEdit
from PySide6.QtCore import QSettings

app = QApplication(sys.argv)

# --- 主处理逻辑 ---
class AnswerBox(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Answer Box")
        self.setGeometry(100, 100, 300, 200)
        self._restore_geometry_or_center()

        summary = ""
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            summary += line
        summary = summary.strip()
        self.label = QLabel(summary)
        self.label.show()

        self.input = QTextEdit()
        self.input.show()

        self.button = QPushButton("Say Hello")
        self.button.clicked.connect(self.respond)
        self.button.show()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.show()

    def respond(self):
        response = {"result": f"{self.input.toPlainText()}"}
        sys.stdout.write(json.dumps(response, ensure_ascii=False))
        sys.stdout.flush()
        app.quit()

    def _restore_geometry_or_center(self):
        settings = QSettings("MyCompany", "AnswerBoxApp")
        pos = settings.value("pos", None)
        size = settings.value("size", None)
        if pos and size:
            self.move(pos)
            self.resize(size)
        else:
            screen = QApplication.primaryScreen()
            rect = screen.availableGeometry()
            self.move(
                rect.center() - self.rect().center()
            )

    def closeEvent(self, event):
        settings = QSettings("MyCompany", "AnswerBoxApp")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())
        return super().closeEvent(event)

answer_box = AnswerBox()
answer_box.show()

app.exec()

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import QProcess, QTextStream, Qt
from PyQt5.QtGui import QTextCursor

class TerminalWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.finished.connect(self.process_finished)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(False)
        self.text_edit.installEventFilter(self)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.setWindowTitle("Terminal in PyQt")
        self.resize(800, 600)

        # Start a shell (e.g., bash on Linux/macOS, cmd.exe on Windows)
        if sys.platform == "win32":
            self.process.start("cmd.exe")
        else:
            self.process.start("bash")

    def eventFilter(self, obj, event):
        if obj == self.text_edit and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return:
                self.send_command()
                return True
        return super().eventFilter(obj, event)

    def send_command(self):
        command = self.text_edit.textCursor().block().text()  # Get the current line
        self.process.write(command.encode() + b"\n")  # Send the command to the process
        self.text_edit.moveCursor(QTextCursor.End)  # Move cursor to the end

    def read_output(self):
        output = self.process.readAllStandardOutput().data().decode()
        self.text_append(output)

    def process_finished(self):
        self.text_append("\nProcess finished.")

    def text_append(self, text):
        self.text_edit.moveCursor(QTextCursor.End)
        self.text_edit.insertPlainText(text)
        self.text_edit.moveCursor(QTextCursor.End)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TerminalWidget()
    window.show()
    sys.exit(app.exec_())
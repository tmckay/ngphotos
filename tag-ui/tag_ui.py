"""
Display images and allow users to add tags to them
"""
import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog, QLineEdit, QPushButton


class TagUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ngphoto :: tags')

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.file_dialog = QFileDialog()

        #layout.addWidget(self.file_dialog)

        self.line_edit = QLineEdit()
        layout.addWidget(self.line_edit)

        button = QPushButton('Browse')
        layout.addWidget(button)

app = QApplication(sys.argv)

window = TagUI()
window.show()

app.exec()

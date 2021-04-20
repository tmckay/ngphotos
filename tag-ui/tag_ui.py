"""
Display images and allow users to add tags to them
"""
import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog, QLineEdit, QPushButton, QLabel
from PyQt6.QtGui import QPixmap


class TagUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ngphoto :: tags')

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel('ngphotos :: tags')
        layout.addWidget(title)

        self.instructions = QLabel('Select a directory to start tagging images:')
        layout.addWidget(self.instructions)

        self.line_edit = QLineEdit()
        layout.addWidget(self.line_edit)

        button = QPushButton('Browse')
        button.clicked.connect(self._open_file_dialog)
        layout.addWidget(button)

        label = QLabel()
        pixmap = QPixmap()
        pixmap.load('../kauai_waterfall.jpg')
        label.setPixmap(pixmap)
        layout.addWidget(label)

    def _open_file_dialog(self):
        directory = QFileDialog.getExistingDirectory()
        self.line_edit.setText(directory)

app = QApplication(sys.argv)

window = TagUI()
window.show()

app.exec()

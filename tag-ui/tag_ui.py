"""
Display images and allow users to add tags to them
"""
import os
import pathlib
import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog, QLineEdit, QPushButton, QLabel, QMainWindow
from PyQt6.QtGui import QPixmap


class TagUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ngphoto :: tags')

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.instructions = QLabel('Select a directory to start tagging images:')
        layout.addWidget(self.instructions)

        self.line_edit = QLineEdit()
        layout.addWidget(self.line_edit)

        button = QPushButton('Browse')
        button.clicked.connect(self._open_file_dialog)
        layout.addWidget(button)

        start = QPushButton('&Start Tagging')
        start.clicked.connect(self._get_image_files)
        layout.addWidget(start)

        self.error_message = QLabel()
        layout.addWidget(self.error_message)

        self.image_label = QLabel()
        self.pixmap = QPixmap()
        self.pixmap.load('../kauai_waterfall.jpg')
        self.image_label.setPixmap(self.pixmap)
        layout.addWidget(self.image_label)

        self._set_default_directory()

    def _open_file_dialog(self):
        directory = QFileDialog.getExistingDirectory()
        self.line_edit.setText(directory)

    def _set_default_directory(self):
        self.line_edit.setText(str(pathlib.Path.home()))

    def _get_image_files(self):
        # Clear error messages
        self.error_message.setText('')

        search_dir = self.line_edit.text()

        if not os.path.exists(search_dir):
            self.error_message.setText('Path does not exist')
            return

        if not os.path.isdir(search_dir):
            self.error_message.setText('Path is not a directory')
            return

        # TODO allow file extensions to be filterable
        extensions = ['.png', '.jpg', '.jpeg']

        for dirpath, dirs, files in os.walk(search_dir):
            for file_ in files:
                ext = os.path.splitext(file_)[1].lower()
                if ext in extensions:
                    full_path = os.path.join(dirpath, file_)
                    self.pixmap.load(full_path)
                    # TODO dynamically resize based on resolution
                    self.pixmap = self.pixmap.scaledToWidth(1000)
                    self.image_label.setPixmap(self.pixmap)
                    break
            break

app = QApplication(sys.argv)
app.setStyleSheet('''
    QWidget {
        font-size: 20px;
    }
    QLineEdit {
        font-size: 20px;
        padding: 2px; 
    }
''')

window = TagUI()
window.show()

app.exec()

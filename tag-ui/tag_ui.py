"""
Display images and allow users to add tags to them
"""
import os
import pathlib
import sqlite3
import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QFileDialog, QLineEdit, QPushButton, QLabel, QMainWindow
from PyQt6.QtGui import QPixmap


DB_PATH = os.path.expanduser('~/ngphotos.db')


class Backend:
    
    def __init__(self, db_path):
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS images
                            (path text, md5 text)''')
        self.con.commit()

    def add_image(self, path, md5):
        self.cur.execute(f'''INSERT INTO images VALUES ('{path}', '{md5}')''')
        self.con.commit()

    def close(self):
        self.con.close()


# TODO make this run in a separate process
def _image_generator(search_dir, extensions):
    for dirpath, dirs, files in os.walk(search_dir):
        for file_ in files:
            ext = os.path.splitext(file_)[1].lower()
            if ext in extensions:
                full_path = os.path.join(dirpath, file_)
                yield full_path


class TagUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ngphoto :: tags')

        self.all_images = None

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

        tag_instructions = QLabel('Add tags separated by spaces:')
        layout.addWidget(tag_instructions)

        self.tags = QLineEdit()
        layout.addWidget(self.tags)

        self._set_default_directory()

        self._init_backend()
        self.backend.create_table()

    def _init_backend(self):
        self.backend = Backend(DB_PATH)

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

        if not self.all_images:
            self.all_images = list(_image_generator(search_dir, extensions))
            self.image_idx = 0

        image_path = self.all_images[self.image_idx]
        self.pixmap.load(image_path)
        # TODO dynamically resize based on resolution
        self.pixmap = self.pixmap.scaledToWidth(1000)
        self.image_label.setPixmap(self.pixmap)
        self.backend.add_image(image_path, '123abc')

        self.image_idx += 1

    def closeEvent(self, event):
        self.backend.close()


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

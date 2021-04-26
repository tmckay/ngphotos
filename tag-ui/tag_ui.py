"""
Display images and allow users to add tags to them
"""
import multiprocessing as mp
from multiprocessing import Process, Queue
import os
import pathlib
import sqlite3
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget
)
from PyQt6.QtGui import QPixmap


DB_PATH = os.path.expanduser('~/ngphotos.db')


class FileScanner:
    def __init__(self, search_dir, extensions):
        print('init scanner')
        self.ctx = mp.get_context('spawn')
        self.queue = self.ctx.Queue()
        self.search_dir = search_dir
        self.extensions = extensions

    @staticmethod
    def _scan(search_dir, extensions, queue):
        for dirpath, dirs, files in os.walk(search_dir):
            for file_ in files:
                print(f'scanning {file_}')
                ext = os.path.splitext(file_)[1].lower()
                if ext in extensions:
                    full_path = os.path.join(dirpath, file_)
                    print(f'adding {full_path} to the queue')
                    queue.put(full_path)

    def start(self):
        print('start scanner')
        self.process = self.ctx.Process(target=self._scan, args=(self.search_dir, self.extensions, self.queue,), daemon=True)
        self.process.start()
        #self.process.join()


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


class TagUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ngphoto :: tags')

        self.all_images = None

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self._init_directory_selection_ui()
        self._init_tagging_ui()
        self._init_window_geometry_ui()

        self._set_default_directory()

        self._init_backend()
        self.backend.create_table()

    def _init_directory_selection_ui(self):
        self.instructions = QLabel('Select a directory to start tagging images:')
        self.layout.addWidget(self.instructions, 0, 0)

        self.line_edit = QLineEdit()
        self.layout.addWidget(self.line_edit, 0, 1)

        button = QPushButton('Browse')
        button.clicked.connect(self._open_file_dialog)
        self.layout.addWidget(button, 0, 2)

    def _init_tagging_ui(self):
        start = QPushButton('Start Tagging')
        start.clicked.connect(self._get_image_files)
        self.layout.addWidget(start, 1, 2)

        self.error_message = QLabel()
        self.layout.addWidget(self.error_message, 1, 1)

        self.image_label = QLabel()
        self.pixmap = QPixmap()
        self.pixmap.load('../kauai_waterfall.jpg')
        self.image_label.setPixmap(self.pixmap)
        self.layout.addWidget(self.image_label, 2, 0, 1, 3)

        tag_instructions = QLabel('Add tags separated by spaces:')
        self.layout.addWidget(tag_instructions, 3, 0)

        self.tags = QLineEdit()
        self.layout.addWidget(self.tags, 3, 1)

        save_and_next = QPushButton('Save and Next')
        save_and_next.clicked.connect(self._get_image_files)
        self.layout.addWidget(save_and_next, 3, 2)

    def _init_window_geometry_ui(self):
        self.width_label = QLabel()
        self.layout.addWidget(self.width_label, 4, 2)

        self.height_label = QLabel()
        self.layout.addWidget(self.height_label, 5, 2)

        self._set_width_text()
        self._set_height_text()

    def resizeEvent(self, event):
        self._set_width_text()
        self._set_height_text()

    def _set_width_text(self):
        width = str(self.frameGeometry().width())
        self.width_label.setText('width: ' + width + 'px')

    def _set_height_text(self):
        height = str(self.frameGeometry().height())
        self.height_label.setText('height: ' + height + 'px')

    def _init_backend(self):
        self.backend = Backend(DB_PATH)

    def _open_file_dialog(self):
        directory = QFileDialog.getExistingDirectory()
        self.line_edit.setText(directory)

    def _set_default_directory(self):
        self.line_edit.setText(str(pathlib.Path.home()))

    def _get_image_files(self):
        print('start _get_image_files')
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
            print('before creating scanner')
            scanner = FileScanner(search_dir, extensions)
            scanner.start()
            print('after creating scanner')
            self.all_images = scanner.queue
            self.image_idx = 0

        #image_path = self.all_images[self.image_idx]
        image_path = self.all_images.get()
        self.pixmap.load(image_path)
        # TODO dynamically resize based on resolution
        self.pixmap = self.pixmap.scaledToWidth(1000)
        self.image_label.setPixmap(self.pixmap)
        self.backend.add_image(image_path, '123abc')

        self.image_idx += 1

    def closeEvent(self, event):
        self.backend.close()


if __name__ == '__main__':
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

import multiprocessing as mp
from multiprocessing import Process, Queue
import os
import pathlib
import sys
import time

from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QMainWindow,
    QWidget
)

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QPixmap


class FileScanner:
    def __init__(self, search_dir, extensions):
        print('init scanner')
        self.ctx = mp.get_context('spawn')
        self.queue = self.ctx.Queue(1)
        self.search_dir = search_dir
        self.extensions = extensions

    @staticmethod
    def _scan(search_dir, extensions, queue):
        """Scans a directory"""
        print(f'scanning {search_dir}')
        for item in os.listdir(search_dir):
            path = os.path.join(search_dir, item)
            if os.path.isfile(path):
                ext = os.path.splitext(path)[1].lower()
                print(f'found extension {ext}')
                if ext in extensions:
                    print(f'adding {path}')
                    queue.put(path)

    def start(self):
        """Starts separate process"""
        print('start scanner')
        self.process = self.ctx.Process(target=self._scan, args=(self.search_dir, self.extensions, self.queue,), daemon=True)
        self.process.start()


class BrowseWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self._images = []

        self.main_window = main_window

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self._setup_input()

        self._update_images()

    def _setup_input(self):
        self.path_edit = QLineEdit()
        self.layout.addWidget(self.path_edit, 0, 0)
        self.layout.setAlignment(self.path_edit, Qt.Alignment.AlignTop)
        self.path_edit.setText(str(pathlib.Path.home()))
        self.path_edit.setAlignment(Qt.Alignment.AlignTop)
        self.path_edit.returnPressed.connect(self._update_images)

    def _remove_images(self):
        self._images.reverse()
        for img in self._images:
            #self.layout.removeWidget(img)
            img.hide()

    def _update_images(self):
        self._remove_images()

        self._start_scanning()

        self._load_images()

    def _start_scanning(self):
        self.scanner = FileScanner(self.path_edit.text(), ['.jpg', '.jpeg', '.png'])
        self.scanner.start()

    def _load_images(self):

        while self.scanner.queue.empty():
            time.sleep(0.1)

        idx = 0
        while not self.scanner.queue.empty():
            label = QLabel()
            pix = QPixmap()
            pix.load(self.scanner.queue.get())
            pix = pix.scaledToWidth(200)
            #pix = pix.scaled(
            #    QSize(200, 200),
            #    Qt.AspectRatioMode.KeepAspectRatio
            #)
            label.setPixmap(pix)
            #self.layout.addWidget(label, idx // 3 + 1, idx % 3) 
            self.layout.addWidget(label, idx // 3 + 1, idx % 3) 
            self.layout.setAlignment(label, Qt.Alignment.AlignTop)
            self._images.append(label)
            idx += 1


class Browse(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('ngphotos :: browse')

        self.statusBar().showMessage('Ready')

        central_widget = BrowseWidget(self)
        self.setCentralWidget(central_widget)

        self.resize(400, 200)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Browse()
    window.show()

    app.exec()

import multiprocessing as mp
from multiprocessing import Process, Queue
import os
import pathlib
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QMainWindow,
    QWidget
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction


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
        for item in os.listdir(search_dir):
            print(f'scanning {item}')
            path = os.path.join(search_dir, item)
            if os.path.isfile(path):
                ext = os.path.splitext(path)[1].lower()
                if ext in extensions:
                    queue.put(path)

    def start(self):
        """Starts separate process"""
        print('start scanner')
        self.process = self.ctx.Process(target=self._scan, args=(self.search_dir, self.extensions, self.queue,), daemon=True)
        self.process.start()


class BrowseWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.path_edit = QLineEdit()
        self.layout.addWidget(self.path_edit, 0, 0)
        self.layout.setAlignment(self.path_edit, Qt.Alignment.AlignTop)
        self.path_edit.setText(str(pathlib.Path.home()))
        self.path_edit.setAlignment(Qt.Alignment.AlignTop)

        self._start_scanning()

    def _start_scanning(self):
        self.scanner = FileScanner(self.path_edit.text(), ['jpg', 'jpeg', 'png'])
        self.scanner.start()

        #while not self.scanner.queue.empty():
        #    self.statusBar().showMessage(self.scanner.queue.get())


class Browse(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('ngphotos :: browse')

        self.statusBar().showMessage('Ready')

        central_widget = BrowseWidget()
        self.setCentralWidget(central_widget)

        self.resize(400, 200)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Browse()
    window.show()

    app.exec()

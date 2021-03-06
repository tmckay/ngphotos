import pathlib
import sys
import time

from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QWidget
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QGuiApplication

import scanner


class BrowseWidget(QWidget):
    """QWidget that provides an interface for browsing
       images on a local filesystem"""
    def __init__(self, main_window: QMainWindow):
        super().__init__()

        # Reference to window that contains this widget
        self._main_window = main_window
        self._images = []  # Stores each image widget

        screen_width = QGuiApplication.primaryScreen().size().width()
        screen_height = QGuiApplication.primaryScreen().size().height()
        self._main_window.statusBar().showMessage(
            f'Width: {screen_width}px // Height: {screen_height}px'
        )

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self._setup_input()

        self._update_images()

    def _setup_input(self):
        self.path_edit = QLineEdit()
        self.layout.addWidget(self.path_edit, 0, 0, 1, 3)
        self.layout.setAlignment(self.path_edit, Qt.Alignment.AlignTop)
        self.path_edit.setText(str(pathlib.Path.home()))
        self.path_edit.setAlignment(Qt.Alignment.AlignTop)

        self.path_edit.returnPressed.connect(self._update_path)

    def _update_path(self):
        self.scanner.clear_queue()
        self._update_images()
        self._main_window.resize(self._main_window.minimumSizeHint())

    def _remove_images(self):
        self._images.reverse()
        for img in self._images:
            img.hide()

    def _update_images(self):
        self._remove_images()

        started = self._start_scanning()

        if started:
            self._load_images()

    def _start_scanning(self):
        path = pathlib.Path(self.path_edit.text())

        if path.is_dir():
            self.scanner = scanner.FileScanner(
                str(path),
                ['.jpg', '.jpeg', '.png']
            )
            self.scanner.start()
            return True
        return False

    def _load_images(self):
        """Reads images from multiprocessing queue and
           inserts them into widget UI"""

        while self.scanner.queue.empty():
            time.sleep(0.1)

        idx = 0
        # TODO calculate number of pictures based on geometry
        while idx < 9 and not self.scanner.queue.empty():
            label = QLabel()
            pix = QPixmap()
            pix.load(self.scanner.queue.get())
            if pix.width() > pix.height():
                pix = pix.scaledToWidth(200)
            else:
                pix = pix.scaledToHeight(200)
            pix_width = pix.width()
            pix_height = pix.height()
            label.setToolTip(f'{pix_width}px x {pix_height}px')
            label.setPixmap(pix)
            row = idx // 3 + 1
            col = idx % 3
            self.layout.addWidget(label, row, col)
            self.layout.setAlignment(
                label,
                Qt.Alignment.AlignVCenter | Qt.Alignment.AlignCenter
            )
            cell_rect = self.layout.cellRect(row, col)
            cell_height = cell_rect.height()
            cell_width = cell_rect.width()
            print(
                f'Cell geometry: {row} x {col} - {cell_width} x {cell_height}'
            )
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

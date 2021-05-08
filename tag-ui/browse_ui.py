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


class BrowseWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.path_edit = QLineEdit()
        self.layout.addWidget(self.path_edit, 0, 0)
        self.path_edit.setText(str(pathlib.Path.home()))
        self.path_edit.setAlignment(Qt.Alignment.AlignTop)


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

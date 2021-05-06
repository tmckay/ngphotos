import sys

from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow
)

from PyQt6.QtCore import Qt


class Browse(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('ngphotos :: browse')

        label = QLabel('ngphotos')

        label.setAlignment(Qt.Alignment.AlignCenter)

        self.setCentralWidget(label)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Browse()
    window.show()

    app.exec()

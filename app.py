# python3
# author: fyl00
# source: https://github.com/fyl00/ExportXiamiList

from PyQt5.QtWidgets import QMainWindow, QApplication
from ui import Ui_MainWindow
import sys


class AppWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())

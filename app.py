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
        self._enbale_source_link()

    def _enbale_source_link(self):
        link_text = "源码：<a href='https://github.com/fyl00/ExportXiamiList'>GitHub</a>"
        self.ui.sourceLabel.setText(link_text)
        self.ui.sourceLabel.setOpenExternalLinks(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())

# python3
# author: fyl00
# source: https://github.com/fyl00/ExportXiamiList

from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
from ui import Ui_MainWindow
from XiamiList.xiami import XiamiHandle, XiamiLink
from XiamiList.tips import *
import sys
import logging


# 打印输出到 logTextEdit
class QtLogHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        record = self.format(record)
        if record:
            EmittingStream.stdout().write('%s\n' % record)


class EmittingStream(QObject):
    _stdout = None
    _stderr = None
    textWritten = pyqtSignal(str)

    def write(self, text):
        if not self.signalsBlocked():
            self.textWritten.emit(str(text))

    def flush(self):
        pass

    def fileno(self):
        return -1

    @staticmethod
    def stdout():
        if not EmittingStream._stdout:
            EmittingStream._stdout = EmittingStream()
            sys.stdout = EmittingStream._stdout
        return EmittingStream._stdout

    @staticmethod
    def stderr():
        if not EmittingStream._stderr:
            EmittingStream._stderr = EmittingStream()
            sys.stderr = EmittingStream._stderr
        return EmittingStream._stderr


# 后台抓取，防止界面未响应
class XiamiThread(QThread):

    finished = pyqtSignal(str)

    def __init__(self, url):
        QThread.__init__(self)
        self.url = url

    def run(self):
        XiamiHandle().get_list(self.url)
        self.finished.emit("DONE")


# 界面窗口
class AppWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._enbale_source_link()
        self.ui.startButton.clicked.connect(self.click_start_button)
        EmittingStream.stdout().textWritten.connect(self._logout)
        EmittingStream.stderr().textWritten.connect(self._logout)

        self.ui.linkLineEdit.setPlaceholderText("请输入歌单链接")
        self.ui.linkLineEdit.setFocus()

        self._logout(GET_LINK)

    def click_start_button(self):
        url = self.ui.linkLineEdit.text()
        if not self._check_url(url):
            return
        thread = XiamiThread(url)
        thread.finished.connect(self._task_finished)
        thread.start()
        self.ui.startButton.setDisabled(True)

    def _check_url(self, url):
        link = XiamiLink(url)
        if link.is_collect is None:
            title = "链接格式错误"
            QMessageBox.critical(self, title, LINK_ERROR_TIPS)
            return False
        return True

    def _task_finished(self, value):
        print(value)
        self.ui.startButton.setDisabled(False)

    def _enbale_source_link(self):
        link_text = "源码：<a href='https://github.com/fyl00/ExportXiamiList'>GitHub</a>"
        self.ui.sourceLabel.setText(link_text)
        self.ui.sourceLabel.setOpenExternalLinks(True)

    def _logout(self, outstr):
        cursor = self.ui.logTextEdit.textCursor()
        cursor.insertText(outstr)
        self.ui.logTextEdit.moveCursor(QTextCursor.End)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())

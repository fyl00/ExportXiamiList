# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'app.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(579, 573)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(9)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout")
        self.linkLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.linkLineEdit.setFont(font)
        self.linkLineEdit.setObjectName("linkLineEdit")
        self.verticalLayout.addWidget(self.linkLineEdit)
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setMinimumSize(QtCore.QSize(0, 30))
        self.startButton.setMaximumSize(QtCore.QSize(300, 50))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(False)
        self.startButton.setFont(font)
        self.startButton.setObjectName("startButton")
        self.verticalLayout.addWidget(self.startButton, 0, QtCore.Qt.AlignHCenter)
        self.logTextEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.logTextEdit.setObjectName("logTextEdit")
        self.verticalLayout.addWidget(self.logTextEdit)
        self.sourceLabel = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("华文细黑")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(True)
        font.setUnderline(False)
        font.setWeight(50)
        self.sourceLabel.setFont(font)
        self.sourceLabel.setScaledContents(True)
        self.sourceLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.sourceLabel.setWordWrap(False)
        self.sourceLabel.setIndent(5)
        self.sourceLabel.setOpenExternalLinks(False)
        self.sourceLabel.setObjectName("sourceLabel")
        self.verticalLayout.addWidget(self.sourceLabel)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "虾米歌单抓取工具"))
        self.startButton.setText(_translate("MainWindow", "START"))
        self.sourceLabel.setText(_translate("MainWindow", "源码：Github"))


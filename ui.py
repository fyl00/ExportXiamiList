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
        self.linkLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.linkLineEdit.setGeometry(QtCore.QRect(20, 20, 541, 31))
        self.linkLineEdit.setObjectName("linkLineEdit")
        self.logTextEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.logTextEdit.setGeometry(QtCore.QRect(20, 130, 541, 381))
        self.logTextEdit.setObjectName("logTextEdit")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(200, 70, 171, 31))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.sourceLabel = QtWidgets.QLabel(self.centralwidget)
        self.sourceLabel.setGeometry(QtCore.QRect(180, 540, 221, 20))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setItalic(True)
        font.setUnderline(True)
        self.sourceLabel.setFont(font)
        self.sourceLabel.setObjectName("sourceLabel")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "虾米歌单抓取工具"))
        self.pushButton.setText(_translate("MainWindow", "Start"))
        self.sourceLabel.setText(_translate("MainWindow", "https://github.com/fyl00/ExportXiamiList"))


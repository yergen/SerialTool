# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Administrator\Desktop\comTool\SerialTool\UserManual.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_helpForm(object):
    def setupUi(self, helpForm):
        helpForm.setObjectName("helpForm")
        helpForm.resize(546, 540)
        self.textEdit = QtWidgets.QTextEdit(helpForm)
        self.textEdit.setEnabled(True)
        self.textEdit.setGeometry(QtCore.QRect(0, 0, 541, 531))
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")

        self.retranslateUi(helpForm)
        QtCore.QMetaObject.connectSlotsByName(helpForm)

    def retranslateUi(self, helpForm):
        _translate = QtCore.QCoreApplication.translate
        helpForm.setWindowTitle(_translate("helpForm", "Form"))
        self.textEdit.setHtml(_translate("helpForm", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">软件使用说明</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">1.简介：本软件是一款针对琦星机械臂的串口控制软件，通过发送485命令来控制机械臂，同时显示接收的数据。</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">2.操作说明：</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">待补充...</p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    helpForm = QtWidgets.QWidget()
    ui = Ui_helpForm()
    ui.setupUi(helpForm)
    helpForm.show()
    sys.exit(app.exec_())


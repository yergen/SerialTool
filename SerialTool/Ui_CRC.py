# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Administrator\Desktop\comTool\SerialTool\CRC.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CRCForm(object):
    def setupUi(self, CRCForm):
        CRCForm.setObjectName("CRCForm")
        CRCForm.resize(400, 300)
        CRCForm.setAutoFillBackground(False)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(CRCForm)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(CRCForm)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.originalData = QtWidgets.QTextEdit(CRCForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.originalData.sizePolicy().hasHeightForWidth())
        self.originalData.setSizePolicy(sizePolicy)
        self.originalData.setMaximumSize(QtCore.QSize(16777215, 41))
        self.originalData.setObjectName("originalData")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.originalData)
        self.label_2 = QtWidgets.QLabel(CRCForm)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.CRCValue = QtWidgets.QTextEdit(CRCForm)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CRCValue.sizePolicy().hasHeightForWidth())
        self.CRCValue.setSizePolicy(sizePolicy)
        self.CRCValue.setMaximumSize(QtCore.QSize(16777215, 41))
        self.CRCValue.setReadOnly(True)
        self.CRCValue.setObjectName("CRCValue")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.CRCValue)
        self.verticalLayout.addLayout(self.formLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.generateCRC = QtWidgets.QPushButton(CRCForm)
        self.generateCRC.setObjectName("generateCRC")
        self.horizontalLayout.addWidget(self.generateCRC)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.clearAllData = QtWidgets.QPushButton(CRCForm)
        self.clearAllData.setObjectName("clearAllData")
        self.horizontalLayout.addWidget(self.clearAllData)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(CRCForm)
        QtCore.QMetaObject.connectSlotsByName(CRCForm)

    def retranslateUi(self, CRCForm):
        _translate = QtCore.QCoreApplication.translate
        CRCForm.setWindowTitle(_translate("CRCForm", "计算CRC"))
        self.label.setText(_translate("CRCForm", "原始数据："))
        self.label_2.setText(_translate("CRCForm", "CRC："))
        self.generateCRC.setText(_translate("CRCForm", "生成CRC"))
        self.clearAllData.setText(_translate("CRCForm", "清除"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CRCForm = QtWidgets.QWidget()
    ui = Ui_CRCForm()
    ui.setupUi(CRCForm)
    CRCForm.show()
    sys.exit(app.exec_())


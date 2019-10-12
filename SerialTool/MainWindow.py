# -*- coding: utf-8 -*-
import os
import sys
import threading
import serial
import time
import binascii, re
import serial.tools.list_ports

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QTimer
from pandas import Series

from Ui_SerialPort import Ui_MainWindow
from Ui_CRC import Ui_CRCForm
from Ui_UserManual import Ui_helpForm
from Ui_AdvancedSetting import Ui_AdvancedForm

from Robot import QxRobot

#import matplotlib.pyplot as plt

class MyWindow(QMainWindow, Ui_MainWindow):
    #自定义信号
    #1.出错信息
    errorSignal = pyqtSignal(str, str)
    #2.下拉菜单点击信号(由于下拉列表控件没有点击信号，需要更改点击事件产生comboBox点击事件)
    comboBoxClicked = pyqtSignal()
    #3.状态栏提示信息
    statusMessage = pyqtSignal(str)
    #4.数据文本更新
    updateReceiveData = pyqtSignal(str, str)
    #5.日志文本更新
    updateLogData = pyqtSignal(dict)
    #6.串口设置不使能
    serialSetSignal = pyqtSignal(bool)
    
    def __init__ (self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        
        self.debug = False #是否用于调试
        self.initVariable()
        self.initTool()
        self.initEvent()
        self.initRobotOperate()
        
    def initVariable(self):
        self.sendBuffer = [] #发送buffer
        self.sendDataEndFlag = 0
#        self.jointIDSet = set([b'\x07', b'\x08', b'\x09', b'\x10', b'\x11', b'\x12', b'\x13'])
        #N:无校验， O:奇校验， E:偶校验
        self.parityDic = {'0':'N',  '1':'O',  '2':'E' }    #校验位转换字典
        self.jointParamDic = {"位置": [6, 14, "位置(rad)", 'ref_pos'], "速度":[14, 20, "速度(rad/s)", 'ref_speed'], \
                                        "电流":[20, 24, "电流(A)", 'ref_current']}#[数据的起始位置,数据的终止位置,"标题",' 图例']
        self.receiveFramesCount = 0  #接收的帧数
        self.receiveBytesCount = 0    #接收的字节数
        self.sendFramesCount = 0     #发送帧数
        self.sendBytesCount = 0       #发送字节数
        
        self.showReceiveFlag = 1
        self.showSendFlag = 0
        self.showLogFlag = 0
        self.receiveDelayMs = 1
        self.sendPeriod = 8
        self.showDataPeriod = 100
        self.receiveShowList = []
        self.sendShowList = []
        
        self.DetectSerialPortFlag = False #是否检测过串口
        self.pathName = os.path.abspath(r'./') #打开和保存数据路径
        #self.tabWidget.setVisible(False) #隐藏图像显示Tab控件
        self.tabWidgetNormalSerial.setVisible(False)
        self.matplotlibWidgetJointParam.setVisible(True)#隐藏图像显示
        self.pushButtonDataVisualized.setEnabled(False)
        self.joint0 = []
        self.joint1 = []
        self.joint2 = []
        self.joint3 = []
        self.joint4 = []
        self.joint5 = []
        self.joint6 = []
        self.urControl = []
        self.jointDic = {"基座": self.joint0, "肩部":self.joint1, "肘部":self.joint2,"手腕1":self.joint3, "手腕2":self.joint4, "手腕3":self.joint5 }
        
        #为串口号下拉列表控件添加事件过滤器
        self.comboBoxSerialPort.installEventFilter(self)

    def initTool(self):
        self.com = serial.Serial()
        #self.detectSerialPortProcess()
        self.sendTimer = QTimer(self)
        self.dataDisplayTimer = QTimer(self)
        self.calCRCWindow = CalCRC()#生成CRC子窗口
        self.helpTextWindow = HelpText()
        self.advancedSettingWindow = AdvanceingSetting()
        self.Rb = QxRobot()
        
    def initEvent(self):
        #串口号检测
        self.comboBoxClicked.connect(self.portComboboxClicked)
        #打开或关闭串口
        self.pushButtonOpenSerialPort.clicked.connect(self.openCloseSerialProcess)
        #清空接收显示控件的数据
        self.pushButtonClearReceiveDisplay.clicked.connect(self.clearReceiveBuffer)
        #定时发送
        self.sendTimer.timeout.connect(self.sendRobotData)
        #定时显示日志100ms
        self.dataDisplayTimer.timeout.connect(self.updateDataDisplayTimer)
        #保存接收数据
        self.pushButtonSaveReceiveData.clicked.connect(self.saveReceiveData)
        #出现错误信号
        self.errorSignal.connect(self.errorSignalShow)
        #状态栏信息
        self.statusMessage.connect(self.updateStatusBar)
        #接收数据文本更新
        self.updateReceiveData.connect(self.updateDataShow)
        #日志数据更新
        self.updateLogData.connect(self.updateLogDataShow)
        #串口设置不使能
        self.serialSetSignal.connect(self.serialSetEnable)
        #串口使用模式选择
        self.pushButtonSreialMode.clicked.connect(lambda:self.serialModeSelect(self.pushButtonSreialMode.text()))
        #打开接收的数据用于图像显示
        self.pushButtonLoadSerialData.clicked.connect(self.loadSerialData)
        #显示图像
        self.pushButtonDataVisualized.clicked.connect(self.dataVisualized)
        #隐藏图像
        self.comboBoxJointId.currentTextChanged.connect(self.matplotlibWidget_visible)
        self.comboBoxParameter.currentTextChanged.connect(self.matplotlibWidget_visible)
        #打开CRC子窗口
        self.actionFile.triggered.connect(self.calCRCWindowShow)
        #打开帮助文档子窗口
        self.actionHelp.triggered.connect(self.helpTextShow)
        #打开高级设置子窗口
        self.actionAdvanced.triggered.connect(self.advancedSettingShow)
        self.advancedSettingWindow.SettingDataList.connect(self.settingData_slot)
        
    def initRobotOperate(self):
        self.robotOpen.clicked.connect(lambda:self.robotOpenSlot(self.robotOpen.text()))
        self.robotClose.clicked.connect(self.robotCloseSlot)
        self.joint0MoveL.pressed.connect(lambda:self.pressedJointMoveSlot(1))
        self.joint1MoveL.pressed.connect(lambda:self.pressedJointMoveSlot(2))
        self.joint2MoveL.pressed.connect(lambda:self.pressedJointMoveSlot(3))
        self.joint3MoveL.pressed.connect(lambda:self.pressedJointMoveSlot(4))
        self.joint4MoveL.pressed.connect(lambda:self.pressedJointMoveSlot(5))
        self.joint5MoveL.pressed.connect(lambda:self.pressedJointMoveSlot(6))
        self.joint0MoveR.pressed.connect(lambda:self.pressedJointMoveSlot(-1))
        self.joint1MoveR.pressed.connect(lambda:self.pressedJointMoveSlot(-2))
        self.joint2MoveR.pressed.connect(lambda:self.pressedJointMoveSlot(-3))
        self.joint3MoveR.pressed.connect(lambda:self.pressedJointMoveSlot(-4))
        self.joint4MoveR.pressed.connect(lambda:self.pressedJointMoveSlot(-5))
        self.joint5MoveR.pressed.connect(lambda:self.pressedJointMoveSlot(-6))
        self.joint0MoveL.released.connect(self.releaseJointMove)
        self.joint1MoveL.released.connect(self.releaseJointMove)
        self.joint2MoveL.released.connect(self.releaseJointMove)
        self.joint3MoveL.released.connect(self.releaseJointMove)
        self.joint4MoveL.released.connect(self.releaseJointMove)
        self.joint5MoveL.released.connect(self.releaseJointMove)
        self.joint0MoveR.released.connect(self.releaseJointMove)
        self.joint1MoveR.released.connect(self.releaseJointMove)
        self.joint2MoveR.released.connect(self.releaseJointMove)
        self.joint3MoveR.released.connect(self.releaseJointMove)
        self.joint4MoveR.released.connect(self.releaseJointMove)
        self.joint5MoveR.released.connect(self.releaseJointMove)
        self.startSingleRotate.clicked.connect(self.startSingleRotate_slot)
        self.stopSingleRotate.clicked.connect(self.stopSingleRotate_slot)
        
    #comboBox控件点击事件过滤
    def eventFilter(self, watched, event):
        if watched == self.comboBoxSerialPort and self.DetectSerialPortFlag == False:
            if event.type() == QEvent.MouseButtonPress:
                mouseEvent = QMouseEvent(event)
                if mouseEvent.buttons() == Qt.LeftButton:
                    self.comboBoxClicked.emit()
        #对于其他情况，会返回系统默认的时间处理方法
        return QMainWindow.eventFilter(self, watched, event)
        
    #关闭事件
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '关闭窗口',
                                     "确定关闭窗口吗?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.com.close()
            self.receiveDataStop = True
            event.accept()
        else:
            event.ignore()
        
    #错误信息显示
    def errorSignalShow(self, str1, str2):
        QMessageBox.information(self, str1, str2)
    
    #状态栏信息
    def updateStatusBar(self, str):
        if str != "":
            self.statusBar.showMessage(str)

    #更新所有可选数据显示
    def updateDataDisplayTimer(self):
        self.updateCounts()
        if self.showSendFlag and len(self.sendShowList) > 0:
            sendList = list(self.sendShowList)
            self.sendShowList.clear()
            for sendBytes in sendList:
                if self.checkBoxHex.isChecked():
                    strReceived = self.ascii2Hexstr(sendBytes)
                else:
                    strReceived = sendBytes.decode('utf-8', "ignore")
                self.updateReceiveData.emit(strReceived, 'red')
        if self.showReceiveFlag and len(self.receiveShowList) > 0:
            receiveList = []
            receiveList = list(self.receiveShowList) #list生成一个副本
            self.receiveShowList.clear()
            for receiveBytes in receiveList:
                if self.checkBoxHex.isChecked():
                    strReceived = self.ascii2Hexstr(receiveBytes)
                else:
                    strReceived = receiveBytes.decode('utf-8', "ignore")
                self.updateReceiveData.emit(strReceived, 'blue')
        if self.showLogFlag and len(self.Rb.errorLog):
            logList = []
            logList = list(self.Rb.errorLog)
            self.Rb.errorLog.clear()
            for logStrs in logList:
                self.updateLogData.emit(logStrs)
            
    #更新各种计数器
    def updateCounts(self):
        self.label_11.setText(str(self.receiveFramesCount))
        self.label_12.setText(str(self.receiveBytesCount))
        self.label_21.setText(str(self.sendFramesCount))
        self.label_22.setText(str(self.sendBytesCount))
        
    #更新发送或接受显示
    def updateDataShow(self, str, color):
        cursor = self.textEditReceiveData.textCursor()     
        cursor.insertHtml("<font color = {1}>{0}</font>".format(str, color))
        cursor.insertText('\n')
        cursor.movePosition(QTextCursor.End)
        self.textEditReceiveData.setTextCursor(cursor)
    #更新错误日志显示
    def updateLogDataShow(self, strs):
        cursor = self.textEditRobotLog.textCursor()     
        cursor.insertText("{0}, C:{1},A:{2}\n".format(
                str(strs["time"]),strs["code"], strs["mes"] ))
        cursor.movePosition(QTextCursor.End)
        self.textEditRobotLog.setTextCursor(cursor)  
        
    #串口号检测   
    def portComboboxClicked(self):
        self.detectSerialPort()
        
    def detectSerialPort(self):
        if not self.DetectSerialPortFlag:
            self.DetectSerialPortFlag = True
            mythread = threading.Thread(target = self.detectSerialPortProcess, name='Thread-detectPort')
            mythread.setDaemon(True)
            mythread.start()
            
    #串口检测处理函数
    def detectSerialPortProcess(self):
        while(1):
            curText = self.comboBoxSerialPort.currentText()
            port_list = self.findSerialPort()
            if len(port_list)>0:
                self.comboBoxSerialPort.clear()
                for list in port_list:
                    self.comboBoxSerialPort.addItem(str(list[0]))
                index = self.comboBoxSerialPort.findText(curText)
                if index >0:
                    self.comboBoxSerialPort.setCurrentIndex(index)
                else:
                    self.comboBoxSerialPort.setCurrentIndex(0)
                break
            time.sleep(1000)
        self.DetectSerialPortFlag = False
        
    #查找串口
    def findSerialPort(self):
        return list(serial.tools.list_ports.comports())
        
    #打开或关闭串口
    def openCloseSerial(self):
        mythread = threading.Thread(target = self.openCloseSerialProcess, name='Thrad-MainA')
        mythread.setDaemon(True)
        mythread.start()
        
    #打开关闭串口处理函数
    def openCloseSerialProcess(self):
        try:
            if self.com.is_open: 
                self.receiveDataStop = True
                self.com.close()
                self.serialSetSignal.emit(False)
                self.statusMessage.emit("串口已关闭")
            else:
                try:
                    self.com.port = self.comboBoxSerialPort.currentText()
                    self.com.baudrate = int(self.comboBoxBaudRate.currentText())
                    self.com.bytesize = int(self.comboBoxDataBits.currentText())
                    self.com.parity = self.parityDic[self.comboBoxParityBits.currentText()]
                    self.com.stopbits = float(self.comboBoxStopBits.currentText())
                    self.com.timeout = None
                    if self.checkBoxRTS.isChecked():
                        self.com.rts = True
                    else:
                        self.com.rts = False
                    if self.checkBoxDTR.isChecked():
                        self.com.dtr = True
                    else:
                        self.com.dtr = False
                        
                    self.com.open()
                    self.serialSetSignal.emit(True)
                    self.statusMessage.emit("串口已打开")
                    
                    mythread = threading.Thread(target = self.receiveData, name = 'ThreadA-Child1')
                    mythread.setDaemon(True)
                    mythread.start()
                    #开启定时器8ms发送一次
                    self.sendTimer.start(8)
                    self.dataDisplayTimer.start(self.showDataPeriod)
                except Exception as e: 
                    self.receiveDataStop = True
                    self.com.close()
                    self.serialSetSignal.emit(False)
                    self.sendBuffer = [] #清空发送缓存
                    self.errorSignal.emit("串口打开失败", str(e))
                    self.statusMessage.emit("串口打开失败")
        except Exception:
            pass 
    #串口配置使能控制
    def serialSetEnable(self, isDisabled):
        if isDisabled:
            self.pushButtonOpenSerialPort.setText("关闭串口")
            self.pushButtonOpenSerialPort.setStyleSheet("\
            #pushButtonOpenSerialPort{background-color:red}")
            self.comboBoxSerialPort.setDisabled(True)
            self.comboBoxBaudRate.setDisabled(True)
            self.comboBoxDataBits.setDisabled(True)
            self.comboBoxParityBits.setDisabled(True)
            self.comboBoxStopBits.setDisabled(True)
        else:
            self.sendTimer.stop()#停止定时器发送
            self.dataDisplayTimer.stop()
            self.pushButtonOpenSerialPort.setText("打开串口")
            self.pushButtonOpenSerialPort.setStyleSheet("\
            #pushButtonOpenSerialPort{background-color:green}")
            self.comboBoxSerialPort.setDisabled(False)
            self.comboBoxBaudRate.setDisabled(False)
            self.comboBoxDataBits.setDisabled(False)
            self.comboBoxParityBits.setDisabled(False)
            self.comboBoxStopBits.setDisabled(False)
    #串口使用模式选择
    def serialModeSelect(self, text):
        if text == "普通串口模式":
            self.pushButtonSreialMode.setText("机械臂模式")
            self.tabWidgetRobotMode.setVisible(True)
            self.tabWidgetNormalSerial.setVisible(False)
        else:
            self.pushButtonSreialMode.setText("普通串口模式")
            self.tabWidgetRobotMode.setVisible(False)
            self.tabWidgetNormalSerial.setVisible(True)
    #接收数据
    def receiveData(self):
        self.receiveDataStop = False
        self.jointHead = True
        currentBytes = b''
        while(not self.receiveDataStop):
            try:
                if  self.jointHead:
                    if self.com.in_waiting > 2:
#                        if self.sendDataEndFlag == 1:
#                            currentBytes = b''
#                            self.sendDataEndFlag = 0
                        currentByte = self.com.read(self.com.in_waiting)
                        self.receiveShowList.append(currentByte)
                        self.receiveBytesCount += self.jointLength #计算接收的字节总数
                        self.receiveFramesCount += 1 #计算接收的帧总数
#                        length = self.com.read(1)#读取某个关节数据的第一个字节(数据长度)
#                        if length == b'\x00':#处理阿猫串口偶尔发0x00情况
#                            continue
#                        ID = self.com.read(1)
##                        if ID not in self.jointIDSet:
##                           continue 
#                        self.jointLength = int.from_bytes(length, byteorder='big', signed=False)#字节流转十进制数
#                        self.jointID = int.from_bytes(ID, byteorder='big', signed=False)#字节流转十进制数
#                        currentBytes  = length
#                        currentBytes += ID
#                        self.jointHead = False   
#                else: 
#                    if self.com.in_waiting >= self.jointLength -2:
#                        currentBytes += self.com.read(self.jointLength - 2)
#                        self.receiveBytesCount += self.jointLength #计算接收的字节总数
#                        self.receiveFramesCount += 1 #计算接收的帧总数
#                        if self.pushButtonSreialMode.text() == "机械臂模式":
#                            pass
#                            #self.Rb.dataProcess(currentBytes)#接收数据处理
#                            
#                        self.receiveShowList.append(currentBytes)
##                        print(self.receiveShowList)
##                        self.updateReceiveData.emit(strReceived, 'rec')
##                        self.updateReceiveData.emit('\n', 'rec')
#                        self.jointHead = True 
                #time.sleep(self.receiveDelayMs/1000)
            except Exception as e:
                print("receive error!")
                self.openCloseSerialProcess()#关闭串口
                self.comboBoxSerialPort.clear()
                self.detectSerialPort()
                print(e)  
                
    #发送机械臂数据
    def sendRobotData(self):
        try:
            if self.com.is_open and len(self.sendBuffer ) == 7:
                    #self.com.flushInput() #丢弃接收缓存区的所有数据
                    
                    sendData= self.Rb.dataPack(self.sendBuffer)
                    self.com.write(sendData)
                    #self.jointHead = True
                    #self.sendDataEndFlag = 1
                    
                    self.sendFramesCount += 1
                    self.sendBytesCount += len(sendData)
#                    self.label_21.setText(str(self.sendFramesCount))
#                    self.label_22.setText(str(self.sendBytesCount))
                    
#                    if self.checkBoxShowSend.isChecked():
#                        currentSendData= self.hex2string(sendData)
#                        self.updateReceiveData.emit(currentSendData, 'send')
#                        self.updateReceiveData.emit('\n', 'send')
        except Exception as e:
            self.openCloseSerialProcess()#关闭串口
            self.comboBoxSerialPort.clear()
            self.detectSerialPort()
            print(e)
        
    #以Ascii编码的的文字以十六进制表示         
    def ascii2Hexstr(self, str):
        strHex = binascii.b2a_hex(str).upper()
        return re.sub(r"(?<=\w)(?=(?:\w\w)+$)", " ", strHex.decode())+" "
    
    
    #十六进制字符串转换为十六进制
    def string2hex(self, str):
        data_list = str.split(' ')
        data = "".join(data_list)
        try:
            data = bytes.fromhex(data)
        except Exception:
            return -1
        return data
                    
    #无符号的十六进制字符串转有符号的十进制数
    def uhex2oct(self, str):
        num = int(str, 16)
        temp = 2**(len(str)*4)
        if num>=temp/2:
            return num - temp
        else:
            return num
            
    #清空接收缓存
    def clearReceiveBuffer(self):
        self.textEditReceiveData.clear()
        self.receiveFramesCount = 0
        self.receiveBytesCount = 0
        self.sendFramesCount = 0
        self.sendBytesCount = 0
        self.label_11.setText(str(self.receiveFramesCount ))
        self.label_12.setText(str(self.receiveBytesCount))
        self.label_21.setText(str(self.sendFramesCount))
        self.label_22.setText(str(self.sendBytesCount))
        
    #保存接收数据
    def saveReceiveData(self):
        filename, _ = QFileDialog.getSaveFileName(self, '保存接收数据', self.pathName , "Document (*.txt)")
        if filename != '':  #不是空文件
            with open(filename, 'w',  errors='ignore') as f:
                text = self.textEditReceiveData.toPlainText()
                f.write(text)
    
    #载入接收到的数据   
    def loadSerialData(self):
        ld = []
        self.joint0.clear()
        self.joint1.clear()
        self.joint2.clear()
        self.joint3.clear()
        self.joint4.clear()
        self.joint5.clear()
        self.urControl.clear()
        self.matplotlibWidgetJointParam.setVisible(False)#隐藏图像显示
        filename, _ = QFileDialog.getOpenFileName(self, '打开数据文件', self.pathName, "Document(*.txt)")
        if filename != '':  #不是空文件
            with open(filename, 'r', errors='ignore') as f: 
                for data in f.readlines():
                    list = data.split()
                    for i in range(len(list)):
                        for item in list[i]:
                            if item == '\0':
                                continue
                            ld += item
                    if ld == '':
                        continue
                    if ld[0:4] =='1507':
                        self.joint0.append(''.join(ld))
                    elif ld[0:4] =='1508':
                        self.joint1.append(''.join(ld))
                    elif ld[0:4] =='1509':
                        self.joint2.append(''.join(ld))
                    elif ld[0:4] =='150A':
                        self.joint3.append(''.join(ld))
                    elif ld[0:4] =='150B':
                        self.joint4.append(''.join(ld))
                    elif ld[0:4] =='150C':
                        self.joint5.append(''.join(ld))
                    elif ld[0:2] =='48':
                        self.urControl.append(''.join(ld))
                    ld = ''
#            print(self.joint0[0:10])
#            self.matplotlibWidgetJointParam.setVisible(True)#图像显示
#            self.dataVisualized()      
            self.pushButtonDataVisualized.setEnabled(True)
    #隐藏图像显示        
    def matplotlibWidget_visible(self):
        self.matplotlibWidgetJointParam.setVisible(False)#隐藏图像显示
        
    #数据可视化
    def dataVisualized(self):
        joint_data = []
        self.matplotlibWidgetJointParam.setVisible(True)#显示图像
        jointID = self.comboBoxJointId.currentText()
        jointParam = self.comboBoxParameter.currentText()
        p1, p2 = self.jointParamDic[jointParam][0:2]
        for item in self.jointDic[jointID]:
            joint_data.append(self.uhex2oct(item[p1: p2]))
        obj = Series(joint_data)
        self.matplotlibWidgetJointParam.mpl.fig.suptitle(jointParam)
        self.matplotlibWidgetJointParam.mpl.axes.plot(list(obj.index),list(obj.values),label="ref_pos", linewidth = 2)
        self.matplotlibWidgetJointParam.mpl.axes.set_ylabel('静态图：Y轴')
        self.matplotlibWidgetJointParam.mpl.axes.set_xlabel('静态图：X轴')
        self.matplotlibWidgetJointParam.mpl.axes.grid(True)
        self.matplotlibWidgetJointParam.show()

#        plt.close()#关闭
#        plt.plot(list(obj.index), list(obj.values), label='ref_pos', linewidth=2)
#        plt.show()
    
    #串口状态
    def serialStatus(self):
        pass
        
    #机械臂打开、启动按钮
    def robotOpenSlot(self, text):
        if text == "开":
            self.robotOpen.setText("启动")
            self.robotClose.setEnabled(True)
        elif text == "启动":
            self.robotOpen.setEnabled(False)
        #改变发送区数据
        self.sendBuffer = self.Rb.robotOpenData(text)
        
    #机械臂关闭按钮
    def robotCloseSlot(self):
        if not self.robotOpen.isEnabled() :
            self.robotOpen.setEnabled(True)
        self.robotOpen.setText("开")
        #改变发送区数据
        self.sendBuffer = self.Rb.robotCloseData()
        
    #肘部顺时针旋转
    def pressedJointMoveSlot(self, jointMove):
        #改变发送区数据
        self.sendBuffer = self.Rb.pressedJointMoveData(jointMove)
        
    def releaseJointMove(self):
        #初始化机械臂按键松开
        self.sendBuffer = self.Rb.releaseJointMoveData()
        
    def startSingleRotate_slot(self):
        #单轴以恒定的速度转动
        jointID = self.singleJointParam.currentIndex()
        jointSpeed = self.singleJointSpeed.value()
        
        self.sendBuffer = self.Rb.singleRotateData(jointID, jointSpeed)
    def stopSingleRotate_slot(self):
        #停止单轴以恒定的速度转动
        self.sendBuffer = self.Rb.stopSingleRotateData()
        
    def calCRCWindowShow(self):
        #添加子窗口
        self.calCRCWindow.show()
        
    def helpTextShow(self):
        self.helpTextWindow.show()
        
    def advancedSettingShow(self):
        self.advancedSettingWindow.show()
        
    def settingData_slot(self, list):
        self.showReceiveFlag = list[0]
        self.showSendFlag = list[1]
        self.showLogFlag = list[2]
        self.receiveDelayMs = list[3]
        self.sendPeriod = list[4]
        self.showDataPeriod = list[5]
        
class CalCRC(QWidget, Ui_CRCForm):
    def __init__(self, parent=None):
        super(CalCRC, self).__init__(parent)
        self.setupUi(self)
        self.initVariable()
        self.initTool()
        self.initEvent()
        
    def initVariable(self):
        self.CrcValue = b''
        
    def initEvent(self):
        #生成CRC
        self.generateCRC.clicked.connect(self.generateCRC_slot)
        #清除所有数据
        self.clearAllData.clicked.connect(self.clearAllData_slot)
        
    def initTool(self):
        self.Rb = QxRobot()
        
    def generateCRC_slot(self):
        MainWindow = MyWindow()
        
        data = MainWindow.string2hex(self.originalData.toPlainText())
        if data != b'':
            CRC16 = self.Rb.generateCRC(data)
            self.CRCValue.setText(MainWindow.ascii2Hexstr(CRC16))
        
    def clearAllData_slot(self):
        self.originalData.clear()
        self.CRCValue.clear()
      
      
class HelpText(QWidget, Ui_helpForm):
    def __init__(self, parent=None):
        super(HelpText, self).__init__(parent)
        self.setupUi(self)
        
        
class AdvanceingSetting(QDialog, Ui_AdvancedForm):
    #自定义信号列表[ReceivedFlag,SendFlag,LogFlag,ShowDataTime,RecDelayTime,SendDataTime]
    SettingDataList = pyqtSignal(list)#用于跟主窗口通信
    
    def __init__(self, parent=None):
        super(AdvanceingSetting, self).__init__()
        self.setupUi(self)
        self.initEvent()
        self.initVariable()
        
    def initEvent(self):
        self.pushButtonOk.clicked.connect(self.buttonOk_Slot)
        self.pushButtonCancel.clicked.connect(self.buttonCancel_Slot)
        self.pushButtonDefault.clicked.connect(self.buttonDefault_Slot)
        
    def initVariable(self):
        self.defaultDataList = [1, 0, 0, 100, 1, 8]
        
    def buttonOk_Slot(self):
        DataList = []
        ReceivedFlag = int(self.checkBoxReceive.isChecked())
        SendFlag = int(self.checkBoxSend.isChecked())
        LogFlag = int(self.checkBoxLog.isChecked())
        ShowDataTime = int(self.spinBoxShowPeriod.text())
        RecDelayTime = int(self.spinBoxRecDelay.text())
        SendDataTime = int(self.spinBoxSendPeriod.text())
        DataList = [ReceivedFlag, SendFlag, LogFlag, ShowDataTime, RecDelayTime, SendDataTime]
        self.SettingDataList.emit(DataList)
        self.close()
    
    def buttonCancel_Slot(self):
        self.close()
    
    def buttonDefault_Slot(self):
        self.SettingDataList.emit(self.defaultDataList)
        self.close()
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = MyWindow()
    demo.show()
    sys.exit(app.exec_())

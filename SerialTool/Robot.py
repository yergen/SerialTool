import struct
from datetime import datetime

class QxRobot(object):
    def __init__(self):
        #super(QxRobot, self).__init__(parent)
        self.initVariable()
        
    def initVariable(self):
        self.jointVersion = 0
        self.multiple = 0
        self.errorLog = []
        self.lastID = 255
        self.joint0 = []
        self.joint1 = []
        self.joint2 = []
        self.joint3 = []
        self.joint4 = []
        self.joint5 = []
        self.joint6 = []
        self.allJoint = {"基座":self.joint0, "肩部":self.joint1, "肘部":self.joint2, 
                            "手腕1":self.joint3, "手腕2":self.joint4, "手腕3":self.joint5, "工具板":self.joint6}
   
    #数据解析
    def dataProcess(self, receiveBuffer):
        if len(receiveBuffer) >3:
            ID = receiveBuffer[1]#获取关节ID
            if self.checkCRC(receiveBuffer):#校验CRC
                if ID <= self.lastID and self.lastID != 255 and self.multiple:
                    self.error(38, ID-self.lastID)
                else:
                    if ID >=0+ self.jointVersion and ID <= 6+self.jointVersion:
                        if ID == 6+self.jointVersion:
                            self.lastID = 255
                        else:
                            self.lastID = ID
                        self.jointModeProcess(receiveBuffer[1:-2])
                    else:
                        self.error(30, ID)
            else:
                self.error(44, ID)
    #数据打包
    #sendBuffer：为一个列表，索引值的数据是相应关节和工具板的数据。
    def dataPack(self, sendBuffer): 
        data = b''
        for i in range(7):
            data += sendBuffer[i]

        dataLength = struct.pack('B', len(data)+1)
        no_CRCData = dataLength + data
        CRCData = self.generateCRC(no_CRCData)
        
        return CRCData
    #将接收到的关节数据根据不同的工作模式进行解包
    def jointModeProcess(self, buffer):
        joint_ID = buffer[0]
        workMode = buffer[1]
        tempForm = {}
        
        if joint_ID != 0x06+self.jointVersion:
            if workMode == 0x00:
                self.error(buffer[2], buffer[3])
                ID, Mode, Code, Msg = struct.unpack('>4B', buffer)#>:大端 B:无符号char
                tempForm = {"jointID": ID,"workMode":Mode, "errorCode":Code, "errorMsg":Msg}
            elif workMode == 0x8C:
                ID, Mode, End = struct.unpack('>2BH', buffer)
                tempForm = {"jointID": ID,"workMode":Mode, "endAddress":End}
            elif workMode == 0x94:
                ID, Mode, Cycle, L_Pos = struct.unpack('>2BlH', buffer)
                tempForm = {"jointID": ID,"workMode":Mode, "Cycle":Cycle, "lastPos":L_Pos}
            elif workMode == 0xFD:
                ID, Mode, Pos, Speed, Cur, GearMax, Gear, Sensor = struct.unpack('>2BL3shlhB', buffer)
                SpeedValue = self.speedProcess(Speed)
                tempForm = {"jointID":ID, "workMode":Mode, "jointPos":Pos,"jointSpeed":SpeedValue,
                                    "jointCur":Cur,"gearMax":GearMax, "gear":Gear, "sensor":Sensor}
            elif workMode == 0xFB:
                ID, Mode, Pos, Cur, GearMax, Gear, Sensor = struct.unpack('>2BLhlhB', buffer)
                tempForm = {"jointID":ID, "workMode":Mode, "jointPos":Pos, "jointCur":Cur,
                                    "gearMax":GearMax, "gear":Gear, "sensor":Sensor}
            elif workMode == 0xF3:
                ID, Mode, Pos, Speed, Cur, GearMax, Gear, Sensor = struct.unpack('>2BL3shlhB', buffer)
                SpeedValue = self.speedProcess(Speed)
                tempForm = {"jointID":ID, "workMode":Mode, "jointPos":Pos,"jointSpeed":SpeedValue, 
                                    "jointCur":Cur,"gearMax":GearMax, "gear":Gear, "sensor":Sensor}
            elif workMode == 0xFF:
                ID, Mode, GearMax, Gear, Sensor = struct.unpack('>2BlhB', buffer)
                tempForm = {"jointID":ID, "workMode":Mode, "gearMax":GearMax, "gear":Gear, "sensor":Sensor}
            elif workMode == 0xF6:
                ID, Mode, GearMax, Gear, Sensor = struct.unpack('>2BlhB', buffer)
                tempForm = {"jointID":ID, "workMode":Mode, "gearMax":GearMax, "gear":Gear, "sensor":Sensor}
            elif workMode == 0xFE:
                ID, Mode,Speed, Cur, GearMax, Gear, Sensor = struct.unpack('>2B3shlhB', buffer)
                SpeedValue = self.speedProcess(Speed)
                tempForm = {"jointID":ID, "workMode":Mode, "jointSpeed":SpeedValue, "jointCur":Cur,
                                    "gearMax":GearMax, "gear":Gear, "sensor":Sensor}
            elif workMode == 0xED:
                ID, Mode,Speed, Cur, GearMax, Gear, Sensor = struct.unpack('>2B3shlhB', buffer)
                SpeedValue = self.speedProcess(Speed)
                tempForm = {"jointID":ID, "workMode":Mode, "jointSpeed":SpeedValue, "jointCur":Cur,
                                    "gearMax":GearMax, "gear":Gear, "sensor":Sensor}
            elif workMode == 0xF0:
                ID, Mode,Speed, Cur, GearMax, Gear, Sensor = struct.unpack('>2B3shlhB', buffer)
                SpeedValue = self.speedProcess(Speed)
                tempForm = {"jointID":ID, "workMode":Mode, "jointSpeed":SpeedValue, "jointCur":Cur,
                                    "gearMax":GearMax, "gear":Gear, "sensor":Sensor}
            elif workMode == 0xEE:
                ID, Mode,Speed, Cur, GearMax, Gear, Sensor = struct.unpack('>2B3shlhB', buffer)
                SpeedValue = self.speedProcess(Speed)
                tempForm = {"jointID":ID, "workMode":Mode, "jointSpeed":SpeedValue, "jointCur":Cur,
                                    "gearMax":GearMax, "gear":Gear, "sensor":Sensor}
            elif workMode == 0xF7: 
                if len(buffer) == 0x0E-3:
                    ID, Mode, AddIndex, FlashData = struct.unpack('>3B8s', buffer)
                    tempForm = {"jointID":ID, "workMode":Mode, "addIndex":AddIndex, "flashData":FlashData}
                elif len(buffer) == 0x0A-3:
                    ID, Mode, AddIndex, FlashData = struct.unpack('>3B4s', buffer)
                    tempForm = {"jointID":ID, "workMode":Mode, "addIndex":AddIndex, "flashData":FlashData}
        else:
            if workMode == 0xFD:#只处理运行模式数据，其他都舍弃。
                ID, Mode, Others = struct.unpack('>2B14s', buffer)
                tempForm = {"jointID":ID, "workMode":Mode, "others":Others}
        #将解析完的数据进行存储
        if len(tempForm) != 0:
            if tempForm["jointID"] == 0x00 + self.jointVersion:
                self.joint0.append(tempForm)
            elif tempForm["jointID"] == 0x01 + self.jointVersion:
                self.joint1.append(tempForm)
            elif tempForm["jointID"] == 0x02 + self.jointVersion:
                self.joint2.append(tempForm)
            elif tempForm["jointID"] == 0x03 + self.jointVersion:
                self.joint3.append(tempForm)
            elif tempForm["jointID"] == 0x04 + self.jointVersion:
                self.joint4.append(tempForm)
            elif tempForm["jointID"] == 0x05 + self.jointVersion:
                self.joint5.append(tempForm)
            elif tempForm["jointID"] == 0x06 + self.jointVersion:
                self.joint6.append(tempForm)
        
        #print(tempForm)
    #速度的特殊格式处理
    def speedProcess(self, Speed):
        if Speed[0] & 0x80:
            tempSpeed  = b'\xFF' + Speed
        else:
            tempSpeed = b'\x00' + Speed
            
        speedValue,  =  struct.unpack('>l', tempSpeed)#speedValue,逗号必须添加。否则返回tuple类型
        
        return speedValue
        
    #在数据最后打包CRC
    def generateCRC(self, sendBuffer):
        tempBuffer = bytearray(sendBuffer[0]+2)#新建bytearray类型,sendBuffer[0]+2大小的变量
        for i in range(len(sendBuffer)):
            tempBuffer[i] = sendBuffer[i]
        temp = 0x0000 
        
        #sendBuffer[0] = sendBuffer[0] + 2 #error: 字节流数组是不可修改的
        tempBuffer[0] += 2 #bytearray可以修改
        for d in tempBuffer[:-2]:
            temp = self.calculateCrc(temp, d)
        tempBuffer[-2] = temp &0xff
        tempBuffer[-1] = temp>>8
        
        return tempBuffer
    
    #CRC校验
    def checkCRC(self, receiveBuffer):
        temp = 0x0000
        
        for d in receiveBuffer:
            temp = self.calculateCrc(temp, d)
            
        return 1 if temp == 0 else 0
        
    #计算要生成的CRC
    def calculateCrc(self, crc, data):
        data=(data^(crc&0xff))
        data=data^(data << 4&0xff)
        
        return (((data<<8)|((crc>>8)&0xff))^(data>>4))^(data<<3)
    
    #错误日志
    def error(self, code, message):
        time = datetime.now()
        self.errorLog.append({"time":time,"code":code, "mes":message})
    
    #机械臂开、启动发送数据
    def robotOpenData(self, text):
        data = []
        
        if text == "开":
            for i in range(6):
                data.append(b'\x02\x82')
            data.append(b'\x03\x95\x40')
        elif text == "启动":
            for i in range(6):
                data.append(b'\x02\x84')
            data.append(b'\x03\x95\x40')
        
        return data
    #机械臂关闭发送数据
    def robotCloseData(self):
        data = []
        
        for i in range(6):
            data.append(b'\x02\x82')
        data.append(b'\x03\x95\x40')
        
        return data
    
    #单轴关节旋转
    def pressedJointMoveData(self, MoveJoint):
        data = []
        
        for i in range(6):
            data.append(b'\x07\x0A\x00\x00\x00\x00\x00')
        data.append(b'\x03\x95\x40')
        
        if MoveJoint >0 and MoveJoint <= 3:
            data[MoveJoint-1] = b'\x07\x0A\x00\x1F\xAE\x00\x00'
        elif MoveJoint >3 and MoveJoint <= 6:
            data[MoveJoint -1] = b'\x07\x0A\x00\x10\xE5\x00\x00'
        elif MoveJoint <0 and MoveJoint >= -3:
            data[abs(MoveJoint)-1] = b'\x07\x0A\xFF\xE0\x52\x00\x00'
        elif MoveJoint <-3 and MoveJoint >= -6:
            data[abs(MoveJoint)-1] = b'\x07\x0A\xFF\xEF\x1B\x00\x00'
            
        return data
    
    def releaseJointMoveData(self):
        data = []
        
        for i in range(6):
            data.append(b'\x07\x0A\x00\x00\x00\x00\x00')
        data.append(b'\x03\x95\x40')
        
        return data
    def singleRotateData(self, jointID, jointSpeed):
        data = []
        speed = b''
        
        for i in range(6):
            data.append(b'\x07\x0A\x00\x00\x00\x00\x00')
        data.append(b'\x03\x95\x40')
        
        if jointID >= 0 and jointID < 3:
            speed = struct.pack('>l', int(jointSpeed/0.0123291015625))[-3:]
        elif jointID >= 3 and jointID < 6:
            speed = struct.pack('>l', int(jointSpeed/0.02311706543))[-3:]
            
        if speed != b'':
            data[jointID] = b'\x07\x0A' + speed + b'\x00\x00'
            
        return data 
    
    def stopSingleRotateData(self):
        data = []
        
        for i in range(6):
            data.append(b'\x07\x0A\x00\x00\x00\x00\x00')
        data.append(b'\x03\x95\x40')
        
        return data
if __name__ == '__main__':
    Rb = QxRobot()
    recData = b'\x12\x02\x82\x02\x82\x02\x82\x02\x82\x02\x82\x02\x82\x03\x95\x40\x71\x01'
    transData = b'\x10\x02\x82\x02\x82\x02\x82\x02\x82\x02\x82\x02\x82\x03\x95\x40'
    recData = b'\x07\xFD\x2C\xD8\xDD\x63\xF1\x83\x84\x04\x10\x00\x00\x19\x63\x05\xD3\x5B'
#    48 0B 0B 29 53 79 B7 01 A4 80 05 02 0B 0B 00 00 00 00 00 00 00 FE DB 0B 0B 00 00 00 00 00 00 00 00 8E
#    0B 0B 00 00 00 00 00 00 00 FF C5 0B 0B 00 00 00 00 00 00 00 00 53 0B 0B 00 00 00 00 00 00 00 00 00 
#    03 95 40 ED 03
    sendBuffer = [ b'\x0B\x0B\x29\x53\x79\xB7\x01\xA4\x80\x05\x02',
                        b'\x0B\x0B\x00\x00\x00\x00\x00\x00\x00\xFE\xDB', 
                        b'\x0B\x0B\x00\x00\x00\x00\x00\x00\x00\x00\x8E', 
                        b'\x0B\x0B\x00\x00\x00\x00\x00\x00\x00\xFF\xC5', 
                        b'\x0B\x0B\x00\x00\x00\x00\x00\x00\x00\x00\x53', 
                        b'\x0B\x0B\x00\x00\x00\x00\x00\x00\x00\x00\x00', 
                        b'\x03\x95\x40']

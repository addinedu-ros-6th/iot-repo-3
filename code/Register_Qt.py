import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import cv2, imutils
import time
import MySQLdb as mdb
import pymysql

import serial ######################
import struct #######################
import csv
import pandas as pd
from datetime import datetime

count = 0

class Receiver(QThread):#############################
    detected = pyqtSignal(bytes)#############################

    def __init__(self,conn,parent=None):#############################
        super(Receiver,self).__init__(parent)#############################
        self.is_running = False
        self.conn = conn#############################
        print('recv init')

    def run(self):#############################
        print("recv start")
        self.is_running = True
        while(self.is_running==True):
            if (self.conn.readable()):
                res = self.conn.read_until(b'\n')
                if len(res) > 0:
                    res = res[:-2]
                    cmd = res[:2].decode()
                    if cmd == 'GS' and res[2] == 0:
                        print('recv detected')
                        self.detected.emit(res[3:])
                    else:
                        print('no signal')

    def stop(self):#############################
        print("recv stop")#############################
        self.is_running = False#######################################################################################


from_class = uic.loadUiType("Register.ui")[0]

class WindowClass(QMainWindow, from_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.uid = bytes(4)
        self.conn = serial.Serial(port='/dev/ttyACM0',baudrate=9600, timeout=1)
        self.recv = Receiver(self.conn)
        self.recv.start()
        self.recv.detected.connect(self.detected)

        self.isCameraOn = False
        self.pixmap = QPixmap()
        self.camera = Camera(self)
        self.camera.daemon = True
        self.count = 0
        self.capButton.hide()

        self.openButton.clicked.connect(self.openFile)
        self.camButton.clicked.connect(self.clickCamera)
        self.camera.update.connect(self.updateCamera)
        self.regiButton.clicked.connect(self.DBConnect)
        self.capButton.clicked.connect(self.capture)

        self.timer = QTimer()
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.getStatus)
        self.timer.start()

        self.setWindowTitle("Let's Register Card!")

    
    # def insert(self):
    #     now = datetime.now()
    #     date_str = now.strftime("%Y-%m-%d")  # 날짜 형식: YYYY-MM-DD
    #     time_str = now.strftime("%H:%M:%S")  # 시간 형식: HH:MM:SS

    #     db = mdb.connect('localhost','root','1','iot_project')
    #     with db:
    #         cur = db.cursor()
    #         cur.execute("INSERT INTO _Attendance_log VALUES ('%s','%s','%s','%s','%s')" % (date_str,time_str,self.uidEdit.text(),self.nameEdit.text(),1))
    #         db.commit()
    
    def send(self, command, data=0): 
        print("send")
        req_data = struct.pack('<2s4sic',command, self.uid, data, b'\n')
        self.conn.write(req_data)
        return
    
    def getStatus(self):
        print("getStatus")
        self.send(b'GS')
        return
    
    def detected(self, uid):
        global count
        self.uid = uid
        a = uid.hex()
        status = 0

        print('card uid : ', a)
        self.uidInfo.setText(a)
        
        ##등록여부 확인
        db1 = mdb.connect('localhost','root','1','iot_project')
        with db1:
            cur = db1.cursor()
            f = open('test2_output.csv','w',encoding='utf-8',newline='')
            wr = csv.writer(f)
            cur.execute("select * from test01 where uid = '%s'" % a)
            rows = cur.fetchall()

            for row in rows:
                wr.writerow([row[0],row[1],row[2],row[3]])

            db1.commit()

        csv_path = '/home/leedw/dev_ws/EDA/src/test2_output.csv'
        test_csv = pd.read_csv(csv_path, names=['col1','col2','col3','col4'])

        if len(test_csv)>0:
            self.isRegistered.setText('~~님 환영합니다.') # 메시지 창 띄우기

            #만약 등록된 사용자라면
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")  # 날짜 형식: YYYY-MM-DD
            time_str = now.strftime("%H:%M:%S")  # 시간 형식: HH:MM:SS
            
            #전역변수 count 카드마다 다른데... ################################################################
            if(count % 2 == 0):
                status = 1
                count += 1
            else:
                status = 0
                count += 1
            
            #등록된 사용자가 카드를 찍었을 때 Log 테이블에 기록 데이터(날짜,시간,uid,이름,상태값) 삽입
            db2 = mdb.connect('localhost','root','1','iot_project')
            with db2:
                cur = db2.cursor()
                cur.execute("INSERT INTO test03 VALUES ('%s','%s','%s','%s','%s')" % (date_str,time_str,row[1],row[0],status))
                db2.commit()     
        else:
            self.isRegistered.setText('미등록된 카드입니다.') # 메시지 창 띄우기

        return
        
    def openFile(self):
        file = QFileDialog.getOpenFileName(filter='Image (*.*)')

        image = cv2.imread(file[0])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
   
        h, w = image.shape
        qimage = QImage(image.data, w, h, QImage.Format_Grayscale8)

        self.pixmap = self.pixmap.fromImage(qimage)
        self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())

        self.label.setPixmap(self.pixmap)

    def clickCamera(self): #4.2
        if self.isCameraOn == False:
            self.camButton.setText('Camera off')
            self.isCameraOn = True
            self.capButton.show()

            self.cameraStart() #4.6
        else:
            self.camButton.setText('Camera')
            self.isCameraOn = False
            self.capButton.hide()

            self.cameraStop() #4.6

    def cameraStart(self): #4.6
        self.camera.running = True
        self.camera.start()
        self.video = cv2.VideoCapture(-1)

    def cameraStop(self): #4.6
        self.camera.running = False
        self.count = 0
        self.video.release

    def updateCamera(self): #4.7
        retval, image = self.video.read()
        if retval:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            h,w = image.shape
            qimage = QImage(image.data,w,h,QImage.Format_Grayscale8)

            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(),self.label.height())
            
            self.label.setPixmap(self.pixmap)

        self.count += 1
        
    def capture(self):
        self.now = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.now + '.png'
        cv2.imwrite(filename, cv2.cvtColor(self.image, cv2.COLOR_RGB2GRAY))

    def DBConnect(self):
        db = mdb.connect('localhost','root','1','iot_project')
        
        #try:
        with db:
            cur = db.cursor()
            cur.execute("INSERT INTO test01 VALUES ('%s','%s','%s','%s')" % (self.nameEdit.text(),self.uidEdit.text(),self.ageEdit.text(),self.companyEdit.text()))
            db.commit()
            
        QMessageBox.about(self,'inserted','Data Inserted Successfully')

class Camera(QThread): # 4.4
    update = pyqtSignal()

    def __init__(self,sec=0,parent=None):
        super().__init__()
        self.main = parent
        self.running = True

    def run(self):
        count = 0
        while self.running == True:
            self.update.emit()
            time.sleep(0.1)

    def stop(self):
        self.running = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()

    sys.exit(app.exec_())
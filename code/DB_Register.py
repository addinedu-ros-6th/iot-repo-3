import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import uic
import cv2, imutils
import time
import MySQLdb as mdb
import pymysql
import serial
import struct 
import csv
import pandas as pd
from datetime import datetime
from PIL import Image
import io
import base64

password = '1'

class Receiver(QThread):
    detected = pyqtSignal(bytes)

    def __init__(self,conn,parent=None):
        super(Receiver,self).__init__(parent)
        self.is_running = False
        self.conn = conn
        print('recv init')

    def run(self):
        print("recv start")
        self.is_running = True
        while(self.is_running==True):
            if (self.conn.readable()):
                res = self.conn.read_until(b'\n')
                if len(res) > 0:
                    res = res[:-2]
                    if res[0] == 0:
                        print('recv detected')
                        self.detected.emit(res[1:])
                    else:
                        print('no signal')

    def stop(self):
        print("recv stop")
        self.is_running = False

from_class = uic.loadUiType("Qt_Register.ui")[0]

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
        self.isRecStart = False
        self.pixmap = QPixmap()
        self.camera = Camera(self)
        self.camera.daemon = True
        self.record = Camera(self)
        self.record.daemon = True

        self.capButton.hide()
        self.openButton.clicked.connect(self.openFile)
        self.camButton.clicked.connect(self.clickCamera)
        self.camera.update.connect(self.updateCamera)
        self.regiButton.clicked.connect(self.CardRegister)
        self.capButton.clicked.connect(self.capture)
        self.resetButton.clicked.connect(self.reset)
        self.count = 0

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.send)
        self.timer.start()

        self.setWindowTitle("Card Register")
    
    def reset(self):
        self.nameEdit.setText("")
        self.uidEdit.setText("")
        self.floorEdit.setText("")
        self.companyEdit.setText("")
        self.label.clear()
        return
    
    def send(self, data=0): 
        print("send")
        req_data = struct.pack('<i4sc', data, self.uid, b'\n')
        self.conn.write(req_data)
        return

    def detected(self, uid):
        global count
        status = 0
        self.uid = uid
        a = uid.hex()
        print('card uid : ', a)
        self.uidInfo.setText(a)
    
        ##DB접속 후 등록여부 확인
        db1 = mdb.connect('localhost','root',password,'iot_project')
        with db1:
            cur = db1.cursor()
            csv_path = 'DB_query_output.csv'
            f = open(csv_path ,'w',encoding='utf-8',newline='')
            wr = csv.writer(f)
            cur.execute("select * from User where uid = '%s'" % a)
            rows = cur.fetchall()
            #쿼리문 결과를 csv파일에 입력하기
            for row in rows:
                wr.writerow([row[0],row[1],row[2],row[3],row[4]])

            db1.commit()
        #쿼리 결과가 있다 = 등록된 사용자
        if len(rows) > 0:
            db2 = mdb.connect('localhost','root',password,'iot_project')
            with db2:
                cur_2 = db2.cursor()
                csv_path_2 = 'DB_status.csv'
                f_2 = open(csv_path_2 ,'w',encoding='utf-8',newline='')
                wr_2 = csv.writer(f_2)
                cur_2.execute("select * from Log where uid = '%s'" % a)
                statusrow = cur_2.fetchall()
                for row_2 in statusrow:
                    wr_2.writerow([row_2[0],row_2[1],row_2[2],row_2[3],row_2[4]])
            if len(statusrow) % 2 == 0:
                self.isRegistered.setText("'%s'님 환영합니다." % row[0]) # 메시지 창 띄우기
                #status : 상태값, 0:퇴근, 1:출근
                status = 1
            else:
                self.isRegistered.setText("'%s'님 안녕히 가십시오"% row[0])
                status = 0
            
            #만약 등록된 사용자라면
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")  # 날짜 형식: YYYY-MM-DD
            time_str = now.strftime("%H:%M:%S")  # 시간 형식: HH:MM:S
            
            #등록된 사용자가 카드를 찍었을 때 Log 테이블에 기록 데이터(날짜,시간,uid,이름,상태값) 삽입
            db3 = mdb.connect('localhost','root',password,'iot_project')
            with db3:
                cur = db3.cursor()
                cur.execute("INSERT INTO Log VALUES ('%s','%s','%s','%s','%s')" % (date_str,time_str,row[0],row[1],status))
                db3.commit()   
     
        else:
            self.isRegistered.setText('미등록') # 메시지 창 띄우기
            QMessageBox.about(self,'failed','미등록된 카드입니다. 먼저 등록해주세요.')

        return
        
    def openFile(self):
        file = QFileDialog.getOpenFileName(filter='Image (*.*)')
        self.image = cv2.imread(file[0])
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        h, w, c = self.image.shape
        qimage = QImage(self.image.data, w, h, w*c, QImage.Format_RGB888)
        self.pixmap = self.pixmap.fromImage(qimage)
        self.pixmap = self.pixmap.scaled(self.label.width(), self.label.height())
        self.label.setPixmap(self.pixmap)

    def clickCamera(self):
        if self.isCameraOn == False:
            self.camButton.setText('Camera off')
            self.isCameraOn = True
            self.capButton.show()
            self.cameraStart()
        else:
            self.camButton.setText('Camera')
            self.isCameraOn = False
            self.capButton.hide()
            self.cameraStop()

    def cameraStart(self):
        self.camera.running = True
        self.camera.start()
        self.video = cv2.VideoCapture(-1)

    def cameraStop(self):
        self.camera.running = False
        self.count = 0
        self.video.release

    def updateCamera(self):
        retval, image = self.video.read()
        if retval:
            self.image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h,w,c = image.shape
            qimage = QImage(self.image.data,w,h,w*c,QImage.Format_RGB888)
            self.pixmap = self.pixmap.fromImage(qimage)
            self.pixmap = self.pixmap.scaled(self.label.width(),self.label.height())
            self.label.setPixmap(self.pixmap)
        self.count += 1

    def capture(self):
        self.now = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.now + '.png'
        cv2.imwrite(filename, cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
        self.cameraStop()

    def CardRegister(self):
        
        db = mdb.connect('localhost','root',password,'iot_project')
        #try:
        with db:
            cur = db.cursor()
            cur.execute("INSERT INTO User VALUES ('%s','%s','%s','%s','%s')" % (self.nameEdit.text(),self.uid.hex(),self.floorEdit.text(),self.companyEdit.text(),self.image))
            db.commit()
            
        QMessageBox.about(self,'inserted','Data Inserted Successfully')
        #except - 형식을 벗어났을 때 예외처리하기

class Camera(QThread):
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
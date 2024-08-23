###는 클래스,
##는 함수,
#는 변수

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

# class Receiver : bytes크기의 신호를 받으면 실행되는 클래스
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

from_class = uic.loadUiType("Qt_Manager.ui")[0]

class WindowClass(QMainWindow, from_class) :
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.uid = bytes(4)
        self.conn = serial.Serial(port='/dev/ttyACM0',baudrate=9600, timeout=1)
        self.recv = Receiver(self.conn)
        self.recv.start()
        self.recv.detected.connect(self.detected)

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.send)
        self.timer.start()
        
        self.Reset.clicked.connect(self.reset)
        self.setWindowTitle("Manager")

    def reset(self):
        self.tableWidget.setRowCount(0)

    def send(self, data=0): 
        print("send")
        req_data = struct.pack('<i4sc', data, self.uid, b'\n')
        self.conn.write(req_data)
        return

    def detected(self, uid):
        global count
        self.uid = uid
        a = uid.hex()
        #status : 상태값, 0:퇴근, 1:출근
        status = 0

        ##등록여부 확인
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

        if len(rows) > 0:  #만약 등록된 사용자라면
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
                #status : 상태값, 0:퇴근, 1:출근
                status = 1
            else:
                status = 0
            now = datetime.now() #현재 날짜, 시간 가져오기
            date_str = now.strftime("%Y-%m-%d")  #date_str : 날짜 저장
            time_str = now.strftime("%H:%M:%S")  #time_str : 시간 저장
            
            #등록된 사용자가 카드를 찍었을 때 Log 테이블에 기록 데이터(날짜,시간,uid,이름,상태값) 삽입
            db3 = mdb.connect('localhost','root',password,'iot_project')
            with db3:
                cur = db3.cursor()
                cur.execute("INSERT INTO Log VALUES ('%s','%s','%s','%s','%s')" % (date_str,time_str,row[0],row[1],status))
                db3.commit()   
            
            
            self.dayEdit.setText(date_str)
            self.timeEdit.setText(time_str)
            self.floorEdit.setText(str(row[2]))
            self.uidEdit.setText(row[1])
            
            # img = Image.open(row[4])
            # self.label.setPixmap(img)

            row_position = self.tableWidget.rowCount()
            self.tableWidget.setColumnCount(5)
            self.tableWidget.horizontalHeader().setStretchLastSection(True) #레이블 칼럼길이 조정 가능
            self.tableWidget.setSortingEnabled(True)
            self.tableWidget.insertRow(row_position)
            self.tableWidget.setItem(row_position, 0, QTableWidgetItem(date_str))
            self.tableWidget.setItem(row_position, 1, QTableWidgetItem(time_str))
            self.tableWidget.setItem(row_position, 2, QTableWidgetItem(row[0]))
            self.tableWidget.setItem(row_position, 3, QTableWidgetItem(row[1]))
            self.tableWidget.setItem(row_position, 4, QTableWidgetItem(row_2[4]))
            
        else:
            QMessageBox.about(self,'failed','미등록된 카드입니다. 먼저 등록해주세요.')

        return

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()

    sys.exit(app.exec_())
    
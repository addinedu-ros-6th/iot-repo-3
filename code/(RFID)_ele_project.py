import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from PyQt5.QtCore import *
import serial
import struct
import binascii
import mysql.connector


from_class = uic.loadUiType("elevator.ui")[0]
class WindowClass(QMainWindow, from_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.uid_list = []
        self.el_A=2 #--------------
        self.el_B=3 #              
        self.do_A=0 #아두이노 포트넘버
        self.do_B=1 #--------------
       #self.elev_A = elevator(self.el_A)
       #self.elev_B = elevator(self.el_B)
        self.door_A = door(self.do_A) # 출입구 1번 클래스 인스턴스
        #self.door_B = door(self.do_B)
        
        
    def search(self,uid):  # RFID카드를 찍으면 데이터베이스에 접속해서 uid가 사전에 등록된 카드인지 조회하는 함수 
        user_data = mysql.connector.connect(
            host = 'localhost',
            port = 3306,
            user = 'root',
            password = '8414',
            database = 'iot_project'
        )
        cursor = user_data.cursor()
        cursor.execute(f"select uid from user where uid = '{uid}'") # RFID에서 읽은 UID로 데이터베이스의 uid column에서 조회
        result = cursor.fetchall()
        i = 0
        for i in result:
            print(i)
        if i != 0 :
            user_data.close() # 일치하는 값이 있으면 True를 반환
            return "True"
        else:
            user_data.close() # 없으면 False를 반환
            return "False"
        
    
    def send_valid(self,conn,command): # Serial통신 연결과, serach함수에서 받은 반환값을 command로 사전에 등록된 uid일 경우 True
        req_data = struct.pack('<5sc',command.encode(),b'\n') # 아닐경우 False를 아두이노에 명령값으로 보냄
        print(req_data)
        conn.write(req_data)
            
         
     
       
    
  
        
        
        

class door():
    def __init__(self,num):
        self.num = num
        self.conn_d = serial.Serial(port=f'/dev/ttyACM{self.num}',baudrate=9600,timeout=1) # 각 아두이노마다 포트넘버를 바꿔서 연결
        self.recv_d = Receiver(self.conn_d,self.num)  # 신호를 받는용도의 Receiver 클래스(보내는용도로도 사용)
        self.recv_d.start() # 쓰레드 시작
        
    def no_retouch(self,uid):
        myWindows.uid_list.append(uid)
        print(myWindows.uid_list)
     
        
class Elevator():
    def __init__(self,num):
        self.conn_e = serial.Serial(port=f'/dev/ttyACM{num}',baudrate=9600,timeout=1)
        self.recv_e = Receiver(self.conn_e)   



class Receiver(QThread):
    detected = pyqtSignal(bytes)
    
    def __init__(self, conn,num, parent=None):
        super(Receiver, self).__init__(parent)
        self.is_running = False
        self.conn = conn # door나 elevator 인스턴스의 Serial 통신 연결값
        self.num = num # 각 인스턴스에 연결된 아두이노 포트넘버
        
    def run(self):
        self.is_running = True
        while (self.is_running == True):
            if self.conn.readable():
                res = self.conn.read_until('\n')
             #cmd = binascii.hexlify(res).decode('utf-8') # binascii.hexlify: 바이트 데이터를 16진수로 변환->decode('utf-8):문자열로 디코딩
                cmd = res.hex() # 16진수로 변환(str타입이된다)
                print(f"door({self.num}) :{cmd}")
                if len(cmd) > 0:
                    valid = WindowClass.search(self,cmd) # windowClass에 선언해둔 RFID의 uid조회함수 호출
                    WindowClass.send_valid(self,self.conn,valid) # 조회결과에 따른 명령을 아두이노에 보내는 함수 호출
                    door.no_retouch(self,cmd)
             
                        

    def stop(self):
        print("receive thread stop")
        self.is_running = False
                                      
                    
                    
                    
                    
                    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindows = WindowClass()
    myWindows.show()
    
    sys.exit(app.exec_())
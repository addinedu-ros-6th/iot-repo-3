import sys
import time
import serial
import threading
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow
import mysql.connector
import binascii

# 시리얼 포트 설정 (환경에 맞게 변경)
ser_elevator = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # 엘리베이터 보드 연결
ser_rfid = serial.Serial('/dev/ttyACM1', 9600, timeout=1)  # RFID 및 출입구 보드 연결
time.sleep(2)

# 엘리베이터 클래스 정의
class Elevator():
    def __init__(self):
        self.present_floor = 1
        self.up = False
        self.down = False
        self.stop = True
        self.goal = 1
        self.end_floor = 1
        self.ul = []
        self.dl = []
        self.door_closed = True
        self.gap = 0

    def up_list(self, uid_goal):
        self.ul.append(uid_goal)
        self.ul = list(set(self.ul))
        self.ul.sort()

    def down_list(self, button_goal):
        self.dl.append(button_goal)
        self.dl = list(set(self.dl))
        self.dl.sort(reverse=True)

    def status(self):
        if self.gap > 0:
            self.up = True
            self.down = False
            self.stop = False
        elif self.gap < 0:
            self.down = True
            self.up = False
            self.stop = False
        elif len(self.dl) == 0 and len(self.ul) == 0:
            self.stop = True
            self.up = False
            self.down = False
        return {key: value for key, value in vars(self).items() if value is True}

Elev = Elevator()

# RFID 카드 읽기 및 처리 함수
def read_rfid():
    while True:
        if ser_rfid.in_waiting > 0:
            raw_data = ser_rfid.readline()
            uid_hex = binascii.hexlify(raw_data).decode('ascii')  # 16진수 문자열로 변환
            print(f"Received UID: {uid_hex}")  # 변환된 UID 출력
            
            # 변환된 UID가 'e32de10f'와 일치하는지 확인
            if uid_hex == 'e32de10f':
                Elev.up_list(3)
                print("UID 일치: 3층.")
                
        time.sleep(0.01)

# 데이터베이스에서 UID 조회 함수
def search(uid):
    user_data = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='030200',
        database='amrbase'
    )
    cursor = user_data.cursor()
    cursor.execute(f"SELECT Uid FROM User WHERE Uid = '{uid}'")
    result = cursor.fetchall()
    user_data.close()
    return "True" if result else "False"

# 모터 회전 함수
def rotate_motor(steps):
    command = f"{steps}\n"
    ser_elevator.write(command.encode())
    time.sleep(1)

# 메인 윈도우 클래스 정의
class ElevatorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('elevator.ui', self)  # UI 로드
        self.initUI()

    def initUI(self):
        # 버튼에 대한 클릭 이벤트 연결
        self.btn_floor3.clicked.connect(lambda: self.move_to_floor(3))
        self.btn_floor2.clicked.connect(lambda: self.move_to_floor(2))
        self.btn_floor1.clicked.connect(lambda: self.move_to_floor(1))
        self.btn_close.clicked.connect(lambda: self.rfid_move(Elev.ul[0]))
        self.update_floor_display()

    def move_to_floor(self, floor):
        if floor == Elev.present_floor:
            self.label_floor.setText(f'{floor}층에 이미 있습니다.')
            return
        else:
            Elev.down_list(floor)
            self.move_elevator(Elev.dl[0])
            Elev.dl.pop(0)

    def move_elevator(self, goal_floor):
        if len(Elev.dl) > 0:
            print("down")
            Elev.gap = goal_floor - Elev.present_floor
            grad = int(Elev.gap / abs(Elev.gap))
            Elev.status()
            for i in range(1, Elev.gap + 1):
                steps = grad * 1500
                rotate_motor(steps)
                time.sleep(abs(grad*1.7))
                Elev.present_floor = Elev.present_floor + grad
                self.update_floor_display()
            print(f'{Elev.present_floor}층 문이 열립니다.')
            time.sleep(1)
            print('문이 닫힙니다')
            Elev.gap = 1 - Elev.present_floor
            grad = int(Elev.gap / abs(Elev.gap))
            steps = grad * 1500
            for i in range(1, abs(Elev.gap) + 1):
                rotate_motor(steps)
                time.sleep(abs(grad*1.7))
                Elev.present_floor = Elev.present_floor + grad
                self.update_floor_display()
            self.update_floor_display()
        elif len(Elev.ul) > 0 and Elev.present_floor == 1:
            print("up")
            Elev.gap = goal_floor - Elev.present_floor
            grad = int(Elev.gap / abs(Elev.gap))
            Elev.status()
            for i in range(1, Elev.gap + 1):
                steps = grad * 1500
                rotate_motor(steps)
                time.sleep(1.5)
                Elev.present_floor = Elev.present_floor + grad
                self.update_floor_display()
            print(f'{Elev.present_floor}층 문이 열립니다.')
            time.sleep(1.5)
            print('문이 닫힙니다')
            self.update_floor_display()
        
    def rfid_move(self, goal_floor):
        print("up")
        Elev.gap = goal_floor - Elev.present_floor
        grad = int(Elev.gap / abs(Elev.gap))
        Elev.status()
        for i in range(1, Elev.gap + 1):
            steps = grad * 1500
            rotate_motor(steps)
            time.sleep(1.5)
            Elev.present_floor = Elev.present_floor + grad
            self.update_floor_display()
        print(f'{Elev.present_floor}층 문이 열립니다.')
        time.sleep(1.5)
        print('문이 닫힙니다')
        self.update_floor_display()


    def update_floor_display(self):
        self.label_floor.setText(f'현재 층: {Elev.present_floor}층')
        self.label_floor.repaint()

# 메인 함수
def main():
    app = QApplication(sys.argv)

    # RFID 및 버튼 신호를 읽어오는 쓰레드 생성 및 시작
    thread_rfid = threading.Thread(target=read_rfid)
    thread_rfid.daemon = True
    thread_rfid.start()

    ex = ElevatorApp()
    ex.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

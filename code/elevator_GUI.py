import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

form_class = uic.loadUiType("/home/mymy/dev_ws/QT/Manager222.ui")[0]

class OptionWindow(QMainWindow):
    def __init__(self, parent=None):
        super(OptionWindow, self).__init__(parent)
        option_ui = '/home/mymy/dev_ws/QT/Register.ui' # Register.ui 파일 로드
        uic.loadUi(option_ui, self)
        self.setWindowTitle("Register")
        self.show()

class ElevatorWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ElevatorWindow, self).__init__(parent)
        elevator_ui = '/home/mymy/dev_ws/QT/elevator.ui' # Elevator.ui 파일 로드
        uic.loadUi(elevator_ui, self)
        self.setWindowTitle("Elevator Status")
        self.show()

class MainWindow(QMainWindow, form_class):         #MainWindow 는 Manager 파일
    def __init__(self):
        super().__init__()
        self.setupUi(self)                               # Manager222.ui 파일 로드 및 설정
    
        self.pushButton.clicked.connect(self.open_register_window) # 회원등록 버튼을 눌렀을 때 Register창이 열리는 함수 실행
        self.pushButton_2.clicked.connect(self.open_elevator_window) # 엘리베이터현황 버튼을 눌렀을 때 Register창이 열림
        self.setWindowTitle("Manager")

    def open_register_window(self):
        self.option_window = OptionWindow(self) #Option Window 클래스 호출

    def open_elevator_window(self):
        self.elevator_window = ElevatorWindow(self) #Elevator Window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())






##########엘리베이터 현황 GUI 코드 (작업중) ############


# import sys
# import serial
# from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
# from PyQt5.QtCore import QTimer, QSequentialAnimationGroup, QPropertyAnimation, QRect

# class ElevatorGUI(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#         self.serial_port = serial.Serial('/dev/ttyACM0', 9600)  # 아두이노가 연결된 포트 설정
        
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.read_serial)
#         self.timer.start(1000)  # 1초마다 시리얼 포트 읽기

#     def initUI(self):
#         self.setWindowTitle('Elevator Simulation')
#         self.setGeometry(100, 100, 300, 400)
        
#         self.current_floor = 0
#         self.label = QLabel(f'Current Floor: {self.current_floor}', self)
#         self.label.setGeometry(100, 50, 200, 50)
        
#         layout = QVBoxLayout()
#         layout.addWidget(self.label)
        
#         container = QWidget()
#         container.setLayout(layout)
#         self.setCentralWidget(container)
        
#     def read_serial(self):
#         if self.serial_port.in_waiting > 0:
#             uid = self.serial_port.readline().decode('utf-8').strip()
#             self.move_elevator(uid)
        
#     def move_elevator(self, uid):
#         floor_map = {
#             'uid1': 1,
#             'uid2': 2,
#             'uid3': 3,
#             # UID와 층 매핑
#         }
#         target_floor = floor_map.get(uid, self.current_floor)
#         self.animate_elevator(target_floor)
        
#     def animate_elevator(self, target_floor):
#         animation_group = QSequentialAnimationGroup()
        
#         for floor in range(self.current_floor + 1, target_floor + 1):
#             animation = QPropertyAnimation(self.label, b"text")
#             animation.setDuration(1000)  # 1초 동안 애니메이션 실행
#             animation.setStartValue(f'Current Floor: {self.current_floor}')
#             animation.setEndValue(f'Current Floor: {floor}')
#             animation_group.addAnimation(animation)
#             self.current_floor = floor
        
#         animation_group.start()

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = ElevatorGUI()
#     ex.show()
#     sys.exit(app.exec_())









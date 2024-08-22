import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

form_class = uic.loadUiType("/home/mymy/dev_ws/git_ws/iot-repo-3/code/Qt_Manager.ui")[0]

class OptionWindow(QMainWindow):
    def __init__(self_1, parent=None):
        super(OptionWindow, self_1).__init__(parent)
        option_ui = '/home/mymy/dev_ws/git_ws/iot-repo-3/code/Qt_Register.ui' # Register.ui 파일 로드
        uic.loadUi(option_ui, self_1)
        self_1.setWindowTitle("Register")
        self_1.show()


class ElevatorWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ElevatorWindow, self).__init__(parent)
        elevator_ui = '/home/mymy/dev_ws/git_ws/iot-repo-3/code/QT_elevator_status.ui' # Elevator.ui 파일 로드
        uic.loadUi(elevator_ui, self)
        self.setWindowTitle("Elevator Status")
        self.show()


class MainWindow(QMainWindow, form_class):         #MainWindow 는 Manager 파일
    def __init__(self_2):
        super().__init__()
        self_2.setupUi(self_2)                               # Manager222.ui 파일 로드 및 설정
    
        self_2.pushButton.clicked.connect(self_2.open_register_window) # 회원등록 버튼을 눌렀을 때 Register창이 열리는 함수 실행
        self_2.pushButton_2.clicked.connect(self_2.open_elevator_window) # 엘리베이터현황 버튼을 눌렀을 때 Register창이 열림
        self_2.setWindowTitle("Manager")

    def open_register_window(self_2):
        self_2.option_window = OptionWindow(self_2) #Option Window 클래스 호출

    def open_elevator_window(self_2):
        self_2.elevator_window = ElevatorWindow(self_2) #Elevator Window

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())















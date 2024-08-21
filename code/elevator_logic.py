import time
import serial
import threading

class Elevator():
    def __init__(self):
        self.present_floor = 1
        self.up = False
        self.down = False
        self.stop = True
        self.goal = 1
        self.end_floor = 1
        self.total_list = []
        self.ul = []
        self.dl = []
        self.door_closed = False
        self.gap = 0

    def up_list(self, uid_goal):
        self.ul.append(uid_goal)
        self.ul = list(set(self.ul))
        self.ul.sort()

    def down_list(self, button_goal):
        self.dl.append(button_goal)
        self.dl = list(set(self.dl))
        self.dl.sort(reverse=True)

    def up_and_down(self, floor):
        self.plus_minus = abs((floor - self.present_floor)) / (floor - self.present_floor)
        print(self.plus_minus)
        
    def status(self):
        if self.gap > 0:
            self.up = True
            self.down = False
            self.stop = False

        elif self.gap < 0:
            self.down = True
            self.up = False
            self.stop = False
        else:
            self.stop = True
            self.up = False
            self.down = False
        
        return print({key: value for key, value in vars(self).items() if value is True})

Elev = Elevator()

# 시리얼 포트 설정
ser = serial.Serial('/dev/ttyACM3', 9600, timeout=1)
time.sleep(2)

def rotate_motor(steps):
    command = f"{steps}\n"
    ser.write(command.encode())
    time.sleep(1)

def read_buttons():
    debounce_delay = 0.05
    last_button_time = 0
    
    while True:
        if ser.in_waiting > 0:
            current_time = time.time()
            if current_time - last_button_time > debounce_delay:
                button = ser.readline().decode().strip()
                if button == "Button_1":
                    Elev.down_list(1)
                    print(1)
                elif button == "Button_2":
                    Elev.down_list(2)
                    print(2)
                elif button == "Button_3":
                    Elev.down_list(3)
                    print(3)
                last_button_time = current_time
        time.sleep(0.01)

# 버튼 신호를 읽어오는 쓰레드 생성 및 시작
thread_b = threading.Thread(target=read_buttons)
thread_b.daemon = True
thread_b.start()

print("시스템 가동")

# 메인 루프
while True:
    if Elev.present_floor == 1:
        if Elev.door_closed:
            for i in Elev.ul:
                gap = (i - Elev.present_floor)
                print(f"{i}층으로 이동 중")
                rotate_motor(gap)
                time.sleep(gap / 1000)
                Elev.present_floor = i
                print(f"{Elev.present_floor}")

    if len(Elev.dl) > 0:
        print(f"{Elev.dl[0]}층으로 이동 중")
        Elev.gap = (Elev.dl[0] - Elev.present_floor)
        Elev.status()
        steps = Elev.gap * 1500
        rotate_motor(steps)
        time.sleep(Elev.gap * 3)
        Elev.present_floor = Elev.dl[0]
        print(f"{Elev.dl[0]}층")

        if Elev.dl[0] == Elev.present_floor:
            Elev.dl.pop(0)
            Elev.gap = (1 - Elev.present_floor)
            Elev.status()
            steps = Elev.gap * 1500
            print("1층으로 이동 중")
            rotate_motor(steps)
            time.sleep(abs(Elev.gap * 3))
            Elev.present_floor = 1
            print("1층")
            Elev.status()

    time.sleep(0.5)

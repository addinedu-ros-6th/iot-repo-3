import time
import serial
import threading

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # COM3은 아두이노가 연결된 포트로 변경 필요
time.sleep(2)  # 아두이노와의 연결 대기 시간

rfid_to_floor = {
    "YOUR_RFID_TAG_1": 1,
    "YOUR_RFID_TAG_2": 2,
    # 다른 RFID 태그와 층 매핑 추가
}

def send_command(command):
    ser.write(command.encode())  # 명령을 바이트 형식으로 전송

def read_buttons(self):
    if ser.in_waiting > 0:
        button = ser.readline().decode().strip()
        if button == "Button_1":
            #Elev.down_list(1)
            self.floor_1 = True
            print(1)
            if self.floor_1 == True:
                self.floor_1 = False
        elif button == "Button_2":
            #Elev.down_list(2)
            self.floor_2 = True
            print(2)
            if self.floor_2 == True:
                self.floor_2 = False
        elif button == "Button_3":
            #Elev.down_list(3)
            self.floor_3 = True
            print(3)
            if self.floor_3 == True:
                self.floor_3 = False

# 버튼 신호를 읽어오는 쓰레드 생성 및 시작
thread_b = threading.Thread(target=read_buttons)
thread_b.daemon = True
thread_b.start()

def read_motor():
    if ser.in_waiting > 0:
        motor = ser.readline().decode().strip()
        if motor == 'done':
            motor = 0
        else:
            motor = 1
    return motor

thread_m = threading.Thread(target=read_motor)
thread_m.daemon = True
thread_m.start()

def read_serial_data():
    """ 시리얼 포트에서 데이터를 읽어오는 함수 """
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        return data
    return None

def rotate_motor(steps):
    command = f"{steps}\n"  # 스텝 수를 문자열로 변환하고 줄바꿈 추가
    ser.write(command.encode())  # Arduino로 명령 전송
    time.sleep(1)  # 모터가 회전하는 동안 대기

while True:
    if 1층에서 승인 된 rfid 찍었을 때:
        if 둘 다 쉰다면 1번 엘베 선정
        if 둘 중 하나가 쉴 때 Elev 와 Elev_2 status() stop이 True 인 것 선택:
        if 둘 다 가동 중일 때 리스트 원소가 적은 것 선택
    if Elev.present_floor == 1:
        uid = input("층 번호를 입력하세요. 문을 닫으려면 c를 입력하세요")

        if uid == 'q':
            break
        elif uid == 'c':
                Elev.door_closed = True
                print("문이 닫힙니다.")
        elif uid.isdigit():
            Elev.up_list(int(uid))
            Elev.end_floor = max(Elev.ul)
        elif uid == 'u':
            rfid = True
        else:
            print("잘못된 입력입니다.")

    if Elev.door_closed == True and len(Elev.ul) > 0:
        gap = Elev.ul[0] - Elev.present_floor
        rotate_motor(gap)
        while ser.readline().decode('utf-8').strip() != 'done':
            time.sleep(1)
        
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            if line == "done":
                print(f"현재층은 {Elev.present_floor}층입니다")
                print("문이 열립니다.")
                Elev.door_closed = False
                time.sleep(2)
                print("문이 닫힙니다.")
                time.sleep(2)
                Elev.door_closed = True
                Elev.present_floor = Elev.ul[0]
                Elev.ul.pop(0)
            else:
                print("이동 중")
#include <Stepper.h>

const int buttonPin_1 = 2;
const int buttonPin_2 = 3;
const int buttonPin_3 = 4;
bool lastButtonState_1 = LOW;  // 버튼의 이전 상태
bool lastButtonState_2 = LOW;
bool lastButtonState_3 = LOW;
bool currentButtonState_1 = LOW;  // 버튼의 현재 상태
bool currentButtonState_2 = LOW;
bool currentButtonState_3 = LOW;
const int stepsPerRevolution = 200;  // 스텝 모터의 1회전 당 스텝 수

Stepper myStepper(stepsPerRevolution, 11, 9, 10, 8);  // 모터 제어 핀

void setup() {
  Serial.begin(9600);
  pinMode(buttonPin_1, INPUT); // 버튼 핀 설정
  pinMode(buttonPin_2, INPUT);
  pinMode(buttonPin_3, INPUT);
  myStepper.setSpeed(110);  // 모터 속도 설정 (단위: RPM)
}

void loop() {
currentButtonState_1 = digitalRead(buttonPin_1);  // 버튼 상태 읽기
currentButtonState_2 = digitalRead(buttonPin_2);
currentButtonState_3 = digitalRead(buttonPin_3);

  // 버튼이 HIGH로 변경된 경우
  if (currentButtonState_1 == HIGH && lastButtonState_1 == LOW) {
    Serial.println("Button_1");  // 시리얼로 신호 전송
    delay(100);  // 버튼의 디바운스를 방지하기 위해 잠시 지연
  }

  if (currentButtonState_2 == HIGH && lastButtonState_2 == LOW) {
    Serial.println("Button_2");  // 시리얼로 신호 전송
    delay(100);  // 버튼의 디바운스를 방지하기 위해 잠시 지연
  }
  
  if (currentButtonState_3 == HIGH && lastButtonState_3 == LOW) {
    Serial.println("Button_");  // 시리얼로 신호 전송
    delay(100);  // 버튼의 디바운스를 방지하기 위해 잠시 지연
  }
  lastButtonState_1 = currentButtonState_1;  // 상태 업데이트
  lastButtonState_2 = currentButtonState_2;
  lastButtonState_3 = currentButtonState_3;

  delay(100); // 디바운싱을 위해 약간의 지연
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    int steps = data.toInt();
    myStepper.step(steps);  // 받은 스텝 수만큼 모터를 회전
    // 모터가 모든 스텝을 완료하면 완료 메시지 전송
    Serial.println("done");
  }
}
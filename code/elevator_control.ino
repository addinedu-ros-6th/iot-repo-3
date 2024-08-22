#include <Stepper.h>

const int stepsPerRevolution = 1024;  // 스텝 모터의 1회전 당 스텝 수

Stepper myStepper(stepsPerRevolution, 11, 9, 10, 8);  // 모터 제어 핀 in1:8, in2 : 9 in3: 10 in4 : 11

void setup() {
  Serial.begin(9600);
  myStepper.setSpeed(30);  // 모터 속도 설정 (단위: RPM)
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    int steps = data.toInt();
    myStepper.step(steps);  // 받은 스텝 수만큼 모터를 회전
    // 모터가 모든 스텝을 완료하면 완료 메시지 전송
    Serial.println("done");
  }
}

#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>

Servo servo;

const int RST_PIN = 9;
const int SS_PIN  =10;
const int index = 60 ; // 블록넘버

MFRC522 rc522(SS_PIN, RST_PIN);

void send_uid(){ // RFID로 읽은 UID를 파이썬으로 전송하는 함수
  char send_buffer[16]; // 문자열 배열 선언
  memset(send_buffer, 0x00,sizeof(send_buffer)); // send_buffer 배열내의 쓰레기값을 0으로 초기화
  memcpy(send_buffer,rc522.uid.uidByte,4); // RFID에서 읽은 UID값이 저장된 rc522.uid에서 처음 4바이트의 정보를 send_buffer에 복사해서 저장
  Serial.write(send_buffer,4); // send_buffer에 저장된 4바이트를 파이썬으로 전송
}

void auth_uid(){ // 데이터 전송 타이밍을 정확하게 지정하지 못해서 신호가 한번씩 밀리는 상태
   char receive[5];
   int i = 0;
   memset(receive, 0x00,sizeof(receive));
   while(Serial.available() > 0 ){  
     receive[i] = Serial.read();
     i++;
   }
  
   receive[4] = '\0';

   if (strcmp(receive,"True") == 0) {
      for (int i = 0 ; i <90 ; i++){
        servo.write(i);  // 서보모터를 90도로 이동
        delay(20);
      }
      delay(1800);
      for (int j=90 ; j>0 ; j--){
        servo.write(j);
        delay(20);
      }
}
}

void setup() {

Serial.begin(9600);
SPI.begin(); // SPI 통신 시작
rc522.PCD_Init(); // PCD 리더기 시작
servo.attach(14); // 서보모터 핀 지정
servo.write(0); // 서보모터 0도로 초기화
}

void loop() {

auth_uid();  

if ( ! rc522.PICC_IsNewCardPresent()){ // 카드접촉 여부 확인
  return;
}

if ( ! rc522.PICC_ReadCardSerial()){ // 카드에서 읽기 가능한 정보 읽어옴
  return;
}

MFRC522::StatusCode status; // MFRC522의 상태 변수 status 선언
MFRC522::MIFARE_Key key; // MIFARE 카드의 인증키 변수 key 선언

for (int i = 0;i <6; i++)
{
  key.keyByte[i] = 0xFF; // key의 전체 값을 0xFF로 초기화
}

status = rc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, index, &key, &(rc522.uid)); // key인증 상태를 status에 저장(OK)

send_uid();


// data = 데이터베이스에서 uid에 따라 층정보를 가져오기위한 코드

int data = 3;  // 카드에 층번호를 저장하기위한 임시변수

byte buffer[16]; 
memset(buffer, 0x00,sizeof(buffer));

buffer[0] = data & 0xFF;
// buffer[1] = (data >> 8) & 0xFF; 숫자가 2바이트 이상의 16진수일 경우 상위 1바이트를 1번 index에 저장한다.

status = rc522.MIFARE_Write(index, buffer, sizeof(buffer)); // 블록넘버 60번(index)에 buffer에 저장된 3을 저장 


SPI.begin();  // 카드가 지속적으로 정보를 갱신할 수 있도록 SPI 통신 초기화
rc522.PCD_Init(); // PCD 리더도 초기화
delay(1500);
}

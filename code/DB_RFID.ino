
#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN         9          // Configurable, see typical pin layout above
#define SS_PIN          10         // Configurable, see typical pin layout above

MFRC522 rc522(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);		// Initialize serial communications with the PC
	while (!Serial);		// Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
	SPI.begin();			// Init SPI bus
	rc522.PCD_Init();		// Init MFRC522

}

void loop() {
  // put your main code here, to run repeatedly:
	// Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
	int recv_size = 0;
  char recv_buffer[14];

  if(Serial.available() > 0)
  {
    recv_size = Serial.readBytesUntil('\n',recv_buffer,14);
  }

  bool newCard = rc522.PICC_IsNewCardPresent();
  bool readCard = rc522.PICC_ReadCardSerial();

  if(recv_size > 0)
  {
    // char cmd[2];
    // memset(cmd,0x00,sizeof(cmd));
    // memcpy(cmd,recv_buffer,2);

    char send_buffer[14];
    memset(send_buffer,0x00,sizeof(send_buffer));
    // memcpy(send_buffer,cmd,2);

    MFRC522::StatusCode status = MFRC522::STATUS_ERROR;

    if(newCard = true && readCard == true)
    {
      memset(send_buffer, MFRC522::STATUS_OK, 1);
      memcpy(send_buffer + 1, rc522.uid.uidByte, 4);
      Serial.write(send_buffer, 5);
    }
      // if(strncmp(cmd, "GS", 2) == 0)
      // {
      //   memset(send_buffer + 2, MFRC522::STATUS_OK, 1);
      //   memcpy(send_buffer + 3, rc522.uid.uidByte, 4);
      //   Serial.write(send_buffer, 7);
      // }
      // else
      // {
      //   memset(send_buffer + 2, 0xFE, 1);
      //   Serial.write(send_buffer,3);
      // } 
    else
    {
      memset(send_buffer, 0xFA, 1);
      Serial.write(send_buffer, 1);
    }
    // else
    // {
    //   // memset(send_buffer + 2, 0xFA, 1);
    //   // Serial.write(send_buffer, 3);
    // }
    Serial.println();
  }
}

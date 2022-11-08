#include <SPI.h>
#include <MFRC522.h>
#include <Keypad.h>
#include <LiquidCrystal_I2C.h>

#define SS_PIN 9
#define RST_PIN 8

const int ROW_NUM = 4;
const int COLUMN_NUM = 4;
const int LOCK_ID = 1;
const int RELAY_PIN = A1;

MFRC522 rfid(SS_PIN, RST_PIN);

char keys[ROW_NUM][COLUMN_NUM] = {
  { '1', '2', '3', 'A' },
  { '4', '5', '6', 'B' },
  { '7', '8', '9', 'C' },
  { '*', '0', '#', 'D' }
};

byte pin_rows[ROW_NUM] = { 35, 37, 39, 41 };
byte pin_column[COLUMN_NUM] = { 43, 45, 47, 49 };

Keypad keypad = Keypad(makeKeymap(keys), pin_rows, pin_column, ROW_NUM, COLUMN_NUM);

char incomingData;
String outgoingData = String("");

LiquidCrystal_I2C lcd(0x27, 16, 2);

int defaultMessage = 0;


void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  pinMode(RELAY_PIN, OUTPUT);
}

void loop() {

  if (defaultMessage != 1) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("EverEye");
    defaultMessage = 1;
  }

  if (rfid.PICC_IsNewCardPresent()) {
    if (rfid.PICC_ReadCardSerial()) {
      defaultMessage = 0;
      for (int i = 0; i < rfid.uid.size; i++) {
        outgoingData.concat(String(rfid.uid.uidByte[i], HEX));
      }
      outgoingData.toUpperCase();
      Serial.println(outgoingData);
      outgoingData = "";
      rfid.PICC_HaltA();
      rfid.PCD_StopCrypto1();

      while(incomingData != 'a' && incomingData != 'b' && incomingData != 'c' && incomingData != 'g') {
        if (Serial.available() > 0) {
          incomingData = Serial.read();
        }
      }
      Serial.read();

      if(incomingData == 'a') {
        lcd.clear();
        lcd.print("Password");
        char keyEntry = '*';
        while (keyEntry != '#') {
          keyEntry = keypad.getKey();
          if (keyEntry) {
            outgoingData += keyEntry;
          }
        }
        outgoingData.remove(outgoingData.length() - 1);
        Serial.println(outgoingData);
        outgoingData = "";

        while(incomingData != 'd' && incomingData != 'e' && incomingData != 'f') {
          if (Serial.available() > 0) {
            incomingData = Serial.read();
          }
        }
        Serial.read();

        if(incomingData == 'd') {
          lcd.clear();
          lcd.print("Lock Open.");
          lcd.setCursor(0, 0);
          digitalWrite(RELAY_PIN, HIGH);
          delay(5000);
          digitalWrite(RELAY_PIN, LOW);
        }
        else if(incomingData == 'e') {
          lcd.clear();
          lcd.print("Wrong Password");
          lcd.setCursor(0, 0);
          delay(2500);
        }
        else if (incomingData == 'f') {
          lcd.clear();
          lcd.print("Unknown Error");
          lcd.setCursor(0, 1);
          lcd.print("Please Try Again");
          delay(2500);
        }

      }
      else if(incomingData == 'b') {
        lcd.clear();
        lcd.print("Invalid ID");
        lcd.setCursor(0, 1);
        lcd.print("Scanned");
        delay(2500);
      }
      else if(incomingData == 'c') {
        lcd.clear();
        lcd.print("Unknown Error");
        lcd.setCursor(0, 1);
        lcd.print("Please Try Again");
        delay(2500);
      }
      else if(incomingData == 'g'){
        lcd.clear();
        lcd.print("User Not");
        lcd.setCursor(0, 1);
        lcd.print("Authorized");
        delay(2500);
      }
      incomingData = 'z';
    }
  }

  if (Serial.available() > 0) {
    boolean check = false;
    char key = '*';
    String passwordEntry;
    defaultMessage = 0;

    incomingData = Serial.read();

    switch(incomingData) {
      case '1':
        lcd.clear();
        lcd.print("Please Scan");
        lcd.setCursor(0, 1);
        lcd.print("RFID Tag.");

        while (check != true) {
          if (rfid.PICC_IsNewCardPresent()) {
            if (rfid.PICC_ReadCardSerial()) {
              for (int i = 0; i < rfid.uid.size; i++) {
                outgoingData.concat(String(rfid.uid.uidByte[i], HEX));
              }
              outgoingData.toUpperCase();
              Serial.println(outgoingData);
              outgoingData = "";
              rfid.PICC_HaltA();
              rfid.PCD_StopCrypto1();
              check = true;
            }
          }
        }

        lcd.clear();
        lcd.print("ID Tag Scanned.");
        lcd.setCursor(0, 0);
        delay(1000);
        break;        
      case '2':
        lcd.clear();
        lcd.print("Please Enter");
        lcd.setCursor(0, 1);
        lcd.print("Password.");

        while (key != '#') {
          key = keypad.getKey();
          if (key) {
            passwordEntry += key;
          }
        }
        passwordEntry.remove(passwordEntry.length() - 1);
        Serial.println(passwordEntry);

        lcd.clear();
        lcd.print("Password Entered.");
        lcd.setCursor(0, 0);
        delay(1000);
        break;
      case '3':
        lcd.clear();
        lcd.print("Opening Lock");
        lcd.setCursor(0, 0);
        digitalWrite(RELAY_PIN, HIGH);
        delay(5000);
        digitalWrite(RELAY_PIN, LOW);
        break;
      default:
        break;
    }
    Serial.read();
  }
}
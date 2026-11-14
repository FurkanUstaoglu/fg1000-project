//=====================================================
// ARDUINO MEGA - RCWS v3.2 (BAĞIMSIZ MOTORLAR + USB)
//=====================================================

#include <Servo.h>
#include <EEPROM.h>

//=====================================================
// PIN TANIMLARI
//=====================================================
#define ESC1_PIN 6
#define ESC2_PIN 7

#define STEP1 22
#define DIR1 24
#define ENA1 23

#define STEP2 26
#define DIR2 28
#define ENA2 27

Servo esc1;
Servo esc2;

//=====================================================
// AYARLAR (TORK İÇİN OPTİMİZE)
//=====================================================
const int pulseDelay = 400;      // 400 = İyi Tork + Orta Hız
#define ENABLE_STATE HIGH

//=====================================================
// EEPROM ADRESLERİ
//=====================================================
#define EEPROM_ADDR_POS1 0
#define EEPROM_ADDR_POS2 4

//=====================================================
// LİMİT AYARLARI
//=====================================================
#define AZIMUT_MIN_STEP -12000
#define AZIMUT_MAX_STEP  12000
#define ELEVATION_MIN_STEP -5000
#define ELEVATION_MAX_STEP  5000

//=====================================================
// DEĞİŞKENLER
//=====================================================
long currentPos1 = 0;
long currentPos2 = 0;
long targetPos1 = 0;
long targetPos2 = 0;
bool isMoving1 = false;
bool isMoving2 = false;

String inputStringESP = "";
String inputStringUSB = "";

//=====================================================
// FONKSİYON PROTOTİPLERİ
//=====================================================
void processCommand(char cmd);
void moveAzimuth(long steps);
void moveElevation(long steps);
void moveToAzimuth(long target);
void moveToElevation(long target);
void updateMotors();
void testMode();
void printStatus();
void goHome();
void saveToEEPROM();
void loadFromEEPROM();
void resetToHome();
void checkSerialPort(HardwareSerial &port, String &inputString);

//=====================================================
// SETUP
//=====================================================
void setup()
{
  Serial.begin(115200);
  Serial1.begin(115200);
  
  delay(500);
  Serial.println("=========================================");
  Serial.println("   RCWS v3.2 - BAGIMSIZ MOTORLAR");
  Serial.println("=========================================");
  Serial.println("ESP32 (Serial1) ve USB (Serial) dinleniyor...");
  Serial.println("Motorlar bagimsiz calisacak!");

  pinMode(STEP1, OUTPUT);
  pinMode(DIR1, OUTPUT);
  pinMode(ENA1, OUTPUT);

  pinMode(STEP2, OUTPUT);
  pinMode(DIR2, OUTPUT);
  pinMode(ENA2, OUTPUT);

  digitalWrite(ENA1, ENABLE_STATE);
  digitalWrite(ENA2, ENABLE_STATE);

  loadFromEEPROM();
  
  targetPos1 = currentPos1;
  targetPos2 = currentPos2;

  Serial.print("Azimut (kayitli): "); Serial.println(currentPos1);
  Serial.print("Elevasyon (kayitli): "); Serial.println(currentPos2);
  Serial.println("=========================================");
  Serial.println("KOMUTLAR:");
  Serial.println("  A-Sag  B-Sol  C-Yukari  D-Asagi");
  Serial.println("  R=+2000  L=-2000  U=+2000  W=-2000");
  Serial.println("  H=Home  M=Konum Kaydet  Z=Sifirla");
  Serial.println("  T=Test  P=Pozisyon  S=Durdur");
  Serial.println("=========================================");
}

//=====================================================
// LOOP
//=====================================================
void loop()
{
  // ESP32'den gelen komutlar (Serial1)
  checkSerialPort(Serial1, inputStringESP);
  
  // USB Seri Monitörden gelen komutlar (Serial) - TEST İÇİN
  checkSerialPort(Serial, inputStringUSB);
  
  // Motorları güncelle
  updateMotors();
}

//=====================================================
// SERI PORT KONTROL
//=====================================================
void checkSerialPort(HardwareSerial &port, String &inputString) {
  while (port.available()) {
    char inChar = (char)port.read();
    
    if (inChar == '\n' || inChar == '\r') {
      if (inputString.length() > 0) {
        processCommand(inputString.charAt(0));
        inputString = "";
      }
    } else {
      inputString += inChar;
    }
  }
}

//=====================================================
// MOTORLARI GÜNCELLE (BAĞIMSIZ)
//=====================================================
void updateMotors()
{
  // Motor 1 (Azimut) - Bağımsız
  if (isMoving1) {
    long diff1 = targetPos1 - currentPos1;
    if (diff1 != 0) {
      if (diff1 > 0) {
        digitalWrite(DIR1, HIGH);
        currentPos1++;
      } else {
        digitalWrite(DIR1, LOW);
        currentPos1--;
      }
      
      digitalWrite(STEP1, HIGH);
      delayMicroseconds(pulseDelay);
      digitalWrite(STEP1, LOW);
      delayMicroseconds(pulseDelay);
      
      if (currentPos1 == targetPos1) {
        isMoving1 = false;
        saveToEEPROM();
        Serial.print("Azimut: "); Serial.println(currentPos1);
      }
    } else {
      isMoving1 = false;
    }
  }
  
  // Motor 2 (Elevasyon) - Bağımsız
  if (isMoving2) {
    long diff2 = targetPos2 - currentPos2;
    if (diff2 != 0) {
      if (diff2 > 0) {
        digitalWrite(DIR2, HIGH);
        currentPos2++;
      } else {
        digitalWrite(DIR2, LOW);
        currentPos2--;
      }
      
      digitalWrite(STEP2, HIGH);
      delayMicroseconds(pulseDelay);
      digitalWrite(STEP2, LOW);
      delayMicroseconds(pulseDelay);
      
      if (currentPos2 == targetPos2) {
        isMoving2 = false;
        saveToEEPROM();
        Serial.print("Elevasyon: "); Serial.println(currentPos2);
      }
    } else {
      isMoving2 = false;
    }
  }
}

//=====================================================
// KOMUT İŞLEME
//=====================================================
void processCommand(char cmd)
{
  Serial.print("Komut: "); Serial.println(cmd);
  
  switch(cmd) {
    // AZİMUT
    case 'A': 
      targetPos1 = currentPos1 + 500;
      if (targetPos1 >= AZIMUT_MIN_STEP && targetPos1 <= AZIMUT_MAX_STEP) {
        isMoving1 = true;
      } else {
        Serial.println("Azimut LIMIT!");
        targetPos1 = currentPos1;
      }
      break;
      
    case 'B': 
      targetPos1 = currentPos1 - 500;
      if (targetPos1 >= AZIMUT_MIN_STEP && targetPos1 <= AZIMUT_MAX_STEP) {
        isMoving1 = true;
      } else {
        Serial.println("Azimut LIMIT!");
        targetPos1 = currentPos1;
      }
      break;
      
    case 'R': 
      targetPos1 = currentPos1 + 2000;
      if (targetPos1 >= AZIMUT_MIN_STEP && targetPos1 <= AZIMUT_MAX_STEP) {
        isMoving1 = true;
      } else {
        Serial.println("Azimut LIMIT!");
        targetPos1 = currentPos1;
      }
      break;
      
    case 'L': 
      targetPos1 = currentPos1 - 2000;
      if (targetPos1 >= AZIMUT_MIN_STEP && targetPos1 <= AZIMUT_MAX_STEP) {
        isMoving1 = true;
      } else {
        Serial.println("Azimut LIMIT!");
        targetPos1 = currentPos1;
      }
      break;
    
    // ELEVASYON
    case 'C': 
      targetPos2 = currentPos2 + 500;
      if (targetPos2 >= ELEVATION_MIN_STEP && targetPos2 <= ELEVATION_MAX_STEP) {
        isMoving2 = true;
      } else {
        Serial.println("Elevasyon LIMIT!");
        targetPos2 = currentPos2;
      }
      break;
      
    case 'D': 
      targetPos2 = currentPos2 - 500;
      if (targetPos2 >= ELEVATION_MIN_STEP && targetPos2 <= ELEVATION_MAX_STEP) {
        isMoving2 = true;
      } else {
        Serial.println("Elevasyon LIMIT!");
        targetPos2 = currentPos2;
      }
      break;
      
    case 'U': 
      targetPos2 = currentPos2 + 2000;
      if (targetPos2 >= ELEVATION_MIN_STEP && targetPos2 <= ELEVATION_MAX_STEP) {
        isMoving2 = true;
      } else {
        Serial.println("Elevasyon LIMIT!");
        targetPos2 = currentPos2;
      }
      break;
      
    case 'W': 
      targetPos2 = currentPos2 - 2000;
      if (targetPos2 >= ELEVATION_MIN_STEP && targetPos2 <= ELEVATION_MAX_STEP) {
        isMoving2 = true;
      } else {
        Serial.println("Elevasyon LIMIT!");
        targetPos2 = currentPos2;
      }
      break;
    
    // SİSTEM KOMUTLARI
    case 'S': 
      isMoving1 = false;
      isMoving2 = false;
      Serial.println("DURDURULDU");
      break;
      
    case 'H': 
      goHome();
      break;
      
    case 'M': 
      saveToEEPROM();
      Serial.println("KONUM KAYDEDILDI!");
      break;
      
    case 'Z': 
      resetToHome();
      break;
      
    case 'T': 
      testMode();
      break;
      
    case 'P': 
      printStatus();
      break;
      
    default:
      Serial.print("Bilinmeyen komut: ");
      Serial.println(cmd);
      break;
  }
}

//=====================================================
// HOME
//=====================================================
void goHome()
{
  Serial.println("HOME...");
  targetPos1 = 0;
  targetPos2 = 0;
  isMoving1 = true;
  isMoving2 = true;
}

//=====================================================
// SIFIRLA
//=====================================================
void resetToHome()
{
  Serial.println("=== SIFIRLANIYOR ===");
  currentPos1 = 0;
  currentPos2 = 0;
  targetPos1 = 0;
  targetPos2 = 0;
  isMoving1 = false;
  isMoving2 = false;
  saveToEEPROM();
  Serial.println("SIFIRLAMA TAMAMLANDI!");
}

//=====================================================
// TEST MODU (BAĞIMSIZ - AYNI ANDA)
//=====================================================
void testMode()
{
  Serial.println("=== TEST MODU ===");
  Serial.println("Her iki motor AYNI ANDA hareket edecek!");
  targetPos1 = 2000;
  targetPos2 = 1000;
  isMoving1 = true;
  isMoving2 = true;
}

//=====================================================
// EEPROM
//=====================================================
void saveToEEPROM()
{
  EEPROM.put(EEPROM_ADDR_POS1, currentPos1);
  EEPROM.put(EEPROM_ADDR_POS2, currentPos2);
  Serial.println("EEPROM'a kaydedildi.");
}

void loadFromEEPROM()
{
  EEPROM.get(EEPROM_ADDR_POS1, currentPos1);
  EEPROM.get(EEPROM_ADDR_POS2, currentPos2);
  
  if (currentPos1 < AZIMUT_MIN_STEP || currentPos1 > AZIMUT_MAX_STEP) {
    currentPos1 = 0;
  }
  if (currentPos2 < ELEVATION_MIN_STEP || currentPos2 > ELEVATION_MAX_STEP) {
    currentPos2 = 0;
  }
}

//=====================================================
// POZİSYON SORGULA
//=====================================================
void printStatus()
{
  Serial.println("=== POZISYON ===");
  Serial.print("Azimut: "); Serial.println(currentPos1);
  Serial.print("Elevasyon: "); Serial.println(currentPos2);
  Serial.println("=================");
}
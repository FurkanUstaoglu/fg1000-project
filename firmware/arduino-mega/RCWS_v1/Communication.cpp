#include "Communication.h"
#include "Motor.h"

void Communication::begin() {
  Serial1.begin(115200);  // ESP32'nin göndereceği Serial (RX1, TX1)
  Serial.println(F("ESP32 haberlesmesi baslatildi."));
}

void Communication::handleIncomingCommands() {
  static String receivedCommand = "";
  
  while (Serial1.available()) {
    char c = Serial1.read();
    if (c == '\n' || c == '\r') {
      if (receivedCommand.length() > 0) {
        processStringCommand(receivedCommand);
        receivedCommand = "";
      }
    } else {
      receivedCommand += c;
    }
  }
}

void Communication::processStringCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();
  
  if (cmd.length() == 0) return;
  
  Serial.print(F("Gelen komut: ")); Serial.println(cmd);
  
  // Tek harfli komutlar
  if (cmd.length() == 1) {
    processCommand(cmd.charAt(0));
    return;
  }
  
  // Parametreli komutlar (örnek: AZ+100, EL-50)
  if (cmd.startsWith("AZ")) {
    int value = cmd.substring(2).toInt();
    if (value != 0) {
      Motor::moveAzimuth(value);
    }
  }
  else if (cmd.startsWith("EL")) {
    int value = cmd.substring(2).toInt();
    if (value != 0) {
      Motor::moveElevation(value);
    }
  }
  else if (cmd.startsWith("MOVE_AZ")) {
    int value = cmd.substring(7).toInt();
    Motor::moveToAzimuth(value);
  }
  else if (cmd.startsWith("MOVE_EL")) {
    int value = cmd.substring(7).toInt();
    Motor::moveToElevation(value);
  }
  else if (cmd == "STATUS") {
    sendStatus();
  }
  else {
    Serial.println(F("Bilinmeyen komut!"));
  }
}

void Communication::processCommand(char cmd) {
  switch(cmd) {
    case 'A': // Azimut +
      Motor::moveAzimuth(133);  // ~10° (133 step = 10°)
      break;
    case 'B': // Azimut -
      Motor::moveAzimuth(-133);
      break;
    case 'C': // Elevasyon +
      Motor::moveElevation(100);  // ~7.5°
      break;
    case 'D': // Elevasyon -
      Motor::moveElevation(-100);
      break;
    case 'S': // Stop
      Motor::stop();
      break;
    case 'H': // Home (Sıfırla)
      Motor::moveToAzimuth(0);
      Motor::moveToElevation(0);
      break;
    case 'T': // Test modu
      Serial.println(F("=== TEST MODU ==="));
      Motor::moveAzimuth(2000);
      delay(3000);
      Motor::moveAzimuth(-2000);
      delay(3000);
      Motor::moveElevation(1000);
      delay(3000);
      Motor::moveElevation(-1000);
      break;
    default:
      Serial.print(F("Bilinmeyen komut: ")); Serial.println(cmd);
      break;
  }
}

void Communication::sendStatus() {
  Serial.print(F("AZ:")); Serial.print(Motor::getAzimuthPosition());
  Serial.print(F(",EL:")); Serial.println(Motor::getElevationPosition());
}

void Communication::sendAck() {
  Serial1.println("OK");
}
#ifndef ESCCONTROL_H
#define ESCCONTROL_H

#include <Arduino.h>

class ESCControl {
public:
  static void begin() {
    Serial.println(F("ESC Kontrol PASIF modda."));
  }
  static void setSpeed(int speed1, int speed2) {
    // Şimdilik boş
  }
  static void arm() {
    // Şimdilik boş
  }
  static void stop() {
    // Şimdilik boş
  }
  static void test() {
    Serial.println(F("ESC test PASIF."));
  }
};

#endif
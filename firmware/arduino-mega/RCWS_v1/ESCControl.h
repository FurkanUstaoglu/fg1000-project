#ifndef ESCCONTROL_H
#define ESCCONTROL_H

#include <Servo.h>

class ESCControl {
public:
  static void begin();
  static void setSpeed(int speed1, int speed2); // 1000-2000 arası
  static void arm();
  static void stop();
  static void test();

private:
  static Servo esc1;
  static Servo esc2;
  
  static const int ESC1_PIN = 6;
  static const int ESC2_PIN = 7;
  
  static bool isArmed;
};

#endif
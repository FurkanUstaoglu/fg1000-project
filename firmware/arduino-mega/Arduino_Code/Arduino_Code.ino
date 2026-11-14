#include <Servo.h>

//=====================================================
// ESC TANIMLARI (ŞİMDİLİK PASİF)
//=====================================================
#define ESC1_PIN 6
#define ESC2_PIN 7

Servo esc1;
Servo esc2;

//=====================================================
// STEP MOTOR 1
//=====================================================
#define STEP1 22
#define DIR1 24
#define ENA1 23

//=====================================================
// STEP MOTOR 2
//=====================================================
#define STEP2 26
#define DIR2 28
#define ENA2 27

//=====================================================
// AYARLAR
//=====================================================
const int pulseDelay = 1000;     // Motor hızı
const int steps = 2000;          // Atılacak adım

// Enable seviyesi
#define ENABLE_STATE HIGH

//=====================================================

void moveMotor(int stepPin)
{
  for(int i = 0; i < steps; i++)
  {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(pulseDelay);

    digitalWrite(stepPin, LOW);
    delayMicroseconds(pulseDelay);
  }
}

void setup()
{
  Serial.begin(115200);

  pinMode(STEP1, OUTPUT);
  pinMode(DIR1, OUTPUT);
  pinMode(ENA1, OUTPUT);

  pinMode(STEP2, OUTPUT);
  pinMode(DIR2, OUTPUT);
  pinMode(ENA2, OUTPUT);

  // Enable
  digitalWrite(ENA1, ENABLE_STATE);
  digitalWrite(ENA2, ENABLE_STATE);

  delay(1000);

  /*
  =====================================================
                    ESC TEST KODU
  =====================================================

  esc1.attach(ESC1_PIN);
  esc2.attach(ESC2_PIN);

  Serial.println("ESC ARM");

  esc1.writeMicroseconds(1000);
  esc2.writeMicroseconds(1000);

  delay(5000);

  for(int pwm = 1130; pwm <= 1300; pwm += 10)
  {
      Serial.println(pwm);

      esc1.writeMicroseconds(pwm);
      esc2.writeMicroseconds(pwm);

      delay(3000);
  }

  esc1.writeMicroseconds(1000);
  esc2.writeMicroseconds(1000);

  =====================================================
  */

  Serial.println("STEP MOTOR TEST BASLADI");
}

void loop()
{
  //=====================================
  // MOTOR 1 CW
  //=====================================
  Serial.println("Motor 1 CW");

  digitalWrite(DIR1, HIGH);

  moveMotor(STEP1);

  delay(3000);

  //=====================================
  // MOTOR 1 CCW
  //=====================================
  Serial.println("Motor 1 CCW");

  digitalWrite(DIR1, LOW);

  moveMotor(STEP1);

  delay(5000);

  //=====================================
  // MOTOR 2 CW
  //=====================================
  Serial.println("Motor 2 CW");

  digitalWrite(DIR2, HIGH);

  moveMotor(STEP2);

  delay(3000);

  //=====================================
  // MOTOR 2 CCW
  //=====================================
  Serial.println("Motor 2 CCW");

  digitalWrite(DIR2, LOW);

  moveMotor(STEP2);

  delay(5000);
}
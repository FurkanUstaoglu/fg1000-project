#include "Motor.h"
#include "Limits.h"

// Statik üyeleri tanımla
AccelStepper Motor::azimuthStepper(AccelStepper::DRIVER, AZ_STEP_PIN, AZ_DIR_PIN);
AccelStepper Motor::elevationStepper(AccelStepper::DRIVER, EL_STEP_PIN, EL_DIR_PIN);
long Motor::currentAzimuthSteps = 0;
long Motor::currentElevationSteps = 0;

void Motor::begin() {
  // Enable pinlerini ayarla
  pinMode(AZ_ENA_PIN, OUTPUT);
  pinMode(EL_ENA_PIN, OUTPUT);
  digitalWrite(AZ_ENA_PIN, HIGH);   // Enable aktif (motorlar çalışabilir)
  digitalWrite(EL_ENA_PIN, HIGH);
  
  // Azimut motor ayarları
  azimuthStepper.setMaxSpeed(1000.0);
  azimuthStepper.setAcceleration(800.0);
  azimuthStepper.setSpeed(600.0);
  
  // Elevasyon motor ayarları
  elevationStepper.setMaxSpeed(800.0);
  elevationStepper.setAcceleration(600.0);
  elevationStepper.setSpeed(400.0);

  // Başlangıç pozisyonlarını sıfırla (Home)
  azimuthStepper.setCurrentPosition(0);
  elevationStepper.setCurrentPosition(0);
  currentAzimuthSteps = 0;
  currentElevationSteps = 0;

  Serial.println(F("Motorlar baslatildi."));
  Serial.print(F("Azimut Enable Pin: ")); Serial.println(AZ_ENA_PIN);
  Serial.print(F("Elevasyon Enable Pin: ")); Serial.println(EL_ENA_PIN);
}

void Motor::update() {
  azimuthStepper.run();
  elevationStepper.run();
}

void Motor::moveAzimuth(long steps) {
  long newPosition = currentAzimuthSteps + steps;
  if (Limits::isAzimuthWithinLimit(newPosition)) {
    azimuthStepper.moveTo(newPosition);
    currentAzimuthSteps = newPosition;
    Serial.print(F("Azimut hedef: ")); Serial.println(newPosition);
  } else {
    Serial.print(F("Azimut limit disi! (Mevcut: ")); 
    Serial.print(currentAzimuthSteps);
    Serial.print(F(", Talep: ")); Serial.println(newPosition);
  }
}

void Motor::moveElevation(long steps) {
  long newPosition = currentElevationSteps + steps;
  if (Limits::isElevationWithinLimit(newPosition)) {
    elevationStepper.moveTo(newPosition);
    currentElevationSteps = newPosition;
    Serial.print(F("Elevasyon hedef: ")); Serial.println(newPosition);
  } else {
    Serial.print(F("Elevasyon limit disi! (Mevcut: ")); 
    Serial.print(currentElevationSteps);
    Serial.print(F(", Talep: ")); Serial.println(newPosition);
  }
}

void Motor::moveToAzimuth(long targetSteps) {
  if (Limits::isAzimuthWithinLimit(targetSteps)) {
    azimuthStepper.moveTo(targetSteps);
    currentAzimuthSteps = targetSteps;
    Serial.print(F("Azimut mutlak hedef: ")); Serial.println(targetSteps);
  } else {
    Serial.println(F("Azimut hedef limit disi!"));
  }
}

void Motor::moveToElevation(long targetSteps) {
  if (Limits::isElevationWithinLimit(targetSteps)) {
    elevationStepper.moveTo(targetSteps);
    currentElevationSteps = targetSteps;
    Serial.print(F("Elevasyon mutlak hedef: ")); Serial.println(targetSteps);
  } else {
    Serial.println(F("Elevasyon hedef limit disi!"));
  }
}

void Motor::stop() {
  azimuthStepper.stop();
  elevationStepper.stop();
  Serial.println(F("Tum motorlar durduruldu."));
}

void Motor::printStatus() {
  Serial.print(F("Az: ")); Serial.print(currentAzimuthSteps);
  Serial.print(F(" | El: ")); Serial.println(currentElevationSteps);
}

long Motor::getAzimuthPosition() {
  return currentAzimuthSteps;
}

long Motor::getElevationPosition() {
  return currentElevationSteps;
}
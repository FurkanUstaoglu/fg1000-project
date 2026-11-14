#ifndef MOTOR_H
#define MOTOR_H

#include <AccelStepper.h>

class Motor {
public:
  static void begin();
  static void update();
  static void moveAzimuth(long steps);
  static void moveElevation(long steps);
  static void moveToAzimuth(long targetSteps);
  static void moveToElevation(long targetSteps);
  static void stop();
  static void printStatus();
  static long getAzimuthPosition();
  static long getElevationPosition();

private:
  // SENİN MEVCUT PIN BAĞLANTILARIN
  static const int AZ_STEP_PIN = 22;
  static const int AZ_DIR_PIN  = 24;
  static const int AZ_ENA_PIN  = 23;
  
  static const int EL_STEP_PIN = 26;
  static const int EL_DIR_PIN  = 28;
  static const int EL_ENA_PIN  = 27;

  static AccelStepper azimuthStepper;
  static AccelStepper elevationStepper;

  static long currentAzimuthSteps;
  static long currentElevationSteps;
};

#endif
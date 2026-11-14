#ifndef LIMITS_H
#define LIMITS_H

#include <Arduino.h>

class Limits {
public:
  static void begin();
  static bool isAzimuthWithinLimit(long steps);
  static bool isElevationWithinLimit(long steps);
  static long getAzimuthMaxSteps();
  static long getElevationMinSteps();
  static long getElevationMaxSteps();

private:
  // AÇI -> ADIM DÖNÜŞÜM ORANI
  static const float DEGREE_TO_STEP = 13.33; // 2000 step = 150° => 1° = 13.33 step
  
  // AZİMUT LİMİTLERİ (Derece)
  static const int AZIMUT_MIN_DEG = -150;  // Sola 150°
  static const int AZIMUT_MAX_DEG =  150;  // Sağa 150°

  // ELEVASYON LİMİTLERİ (Derece)
  static const int ELEVATION_MIN_DEG = -10;  // Aşağı 10°
  static const int ELEVATION_MAX_DEG =  85;  // Yukarı 85°

  // Hesaplanmış step limitleri
  static long azimuthMinSteps;
  static long azimuthMaxSteps;
  static long elevationMinSteps;
  static long elevationMaxSteps;
};

#endif
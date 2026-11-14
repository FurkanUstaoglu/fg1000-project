#include "Limits.h"

// Statik üyeler
const float Limits::DEGREE_TO_STEP;
const int Limits::AZIMUT_MIN_DEG;
const int Limits::AZIMUT_MAX_DEG;
const int Limits::ELEVATION_MIN_DEG;
const int Limits::ELEVATION_MAX_DEG;

long Limits::azimuthMinSteps = 0;
long Limits::azimuthMaxSteps = 0;
long Limits::elevationMinSteps = 0;
long Limits::elevationMaxSteps = 0;

void Limits::begin() {
  // Derece -> Step çevrimi (SENİN 2000 step değerine göre)
  azimuthMinSteps = (long)(AZIMUT_MIN_DEG * DEGREE_TO_STEP);
  azimuthMaxSteps = (long)(AZIMUT_MAX_DEG * DEGREE_TO_STEP);
  elevationMinSteps = (long)(ELEVATION_MIN_DEG * DEGREE_TO_STEP);
  elevationMaxSteps = (long)(ELEVATION_MAX_DEG * DEGREE_TO_STEP);

  Serial.println(F("=== LIMIT AYARLARI ==="));
  Serial.print(F("Azimut Limitleri (Step): "));
  Serial.print(azimuthMinSteps); Serial.print(F(" - ")); Serial.println(azimuthMaxSteps);
  Serial.print(F("Elevasyon Limitleri (Step): "));
  Serial.print(elevationMinSteps); Serial.print(F(" - ")); Serial.println(elevationMaxSteps);
  Serial.print(F("1 Derece = ")); Serial.print(DEGREE_TO_STEP); Serial.println(F(" Step"));
  Serial.println(F("======================"));
}

bool Limits::isAzimuthWithinLimit(long steps) {
  return (steps >= azimuthMinSteps && steps <= azimuthMaxSteps);
}

bool Limits::isElevationWithinLimit(long steps) {
  return (steps >= elevationMinSteps && steps <= elevationMaxSteps);
}

long Limits::getAzimuthMaxSteps() {
  return azimuthMaxSteps;
}
long Limits::getElevationMinSteps() {
  return elevationMinSteps;
}
long Limits::getElevationMaxSteps() {
  return elevationMaxSteps;
}
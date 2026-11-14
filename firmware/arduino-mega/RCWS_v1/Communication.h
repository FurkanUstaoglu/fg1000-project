#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include <Arduino.h>

class Communication {
public:
  static void begin();
  static void handleIncomingCommands();
  static void sendStatus();

private:
  static void processCommand(char cmd);
  static void processStringCommand(String cmd);
  static void sendAck();
};

#endif
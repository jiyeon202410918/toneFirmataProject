#include <Arduino.h>
#include "toneFirmata.h"

void toneFirmata_sysex(byte argc, byte* argv) {
  if (argc < 5) return;

  byte pin = argv[0];
  int frequency = argv[1] | (argv[2] << 7);
  int duration  = argv[3] | (argv[4] << 7);

  if (frequency > 0) {
    tone(pin, frequency, duration);
  } else {
    noTone(pin);
  }
}
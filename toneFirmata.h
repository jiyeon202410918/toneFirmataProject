#include "toneFirmata.h"
#ifndef TONE_FIRMATA_H
#define TONE_FIRMATA_H

#define TONE_CMD 0x7E   // SAMPLING_INTERVAL(0x7A)와 충돌하지 않는 값

void toneFirmata_sysex(byte argc, byte* argv);

#endif
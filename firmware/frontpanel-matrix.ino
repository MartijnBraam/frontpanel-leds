#include <FrequencyTimer2.h>
#include <PacketSerial.h>
#include "arduino2.h"  

byte numCols = 7;
byte numRows = 6;

byte col = 0;
byte leds[7][6];

int pins[14] = { -1, A0, A1, A2, A3, A4, A5, 2, 3, 4, 5, 6, 7, 8};
int rows[6] = {A0, A1, A2, A3, A4, A5};
int cols[7] = {2, 3, 4, 5, 6, 7, 8};

byte cycle = 0;

PacketSerial serial;

void onPacket(const uint8_t* buffer, size_t size);

void setup() {
  for (int i = 1; i <= 14; i++) {
    pinMode(pins[i], OUTPUT);
  }

  // set up cols and rows
  for (int i = 1; i <= 6; i++) {
    digitalWrite(cols[i - 1], LOW);
  }

  for (int i = 1; i <= 7; i++) {
    digitalWrite(rows[i - 1], LOW);
  }

  // Turn off toggling of pin 11
  FrequencyTimer2::disable();
  // Set refresh rate (interrupt timeout period)
  FrequencyTimer2::setPeriod(500);
  // Set interrupt routine to be called
  FrequencyTimer2::setOnOverflow(display);


  serial.setPacketHandler(&onPacket);
  serial.begin(115200);
}

void loop() {
  serial.update();
}


void shift() {
  for (int x = 0; x < numCols-1; x++) {
    for (int y = 0; y < numRows; y++) {
      leds[x][y] = leds[x + 1][y];
    }
  }
}

void onPacket(const uint8_t* buffer, size_t size)
{
  uint8_t packet[size];
  memcpy(packet, buffer, size);

  switch (size) {
    case 1:
      for (int x = 0; x < numCols; x++) {
        for (int y = 0; y < numRows; y++) {
          leds[x][y] = packet[0];
        }
      }
      break;
    case 3:
      leds[packet[0]][packet[1]] = packet[2];
      break;
    case 42:
      memcpy(leds, buffer, size);
      break;
    case 6:
      shift();
      for (int y = 0; y < numRows; y++) {
        leds[6][y] = packet[y];
      }
      break;
  }
}


// Interrupt routine
void display() {
  digitalWrite2(cols[col], LOW);  // Turn whole previous column off
  col++;
  
  if (col == 7) {
    cycle++;
    col = 0;
  }
  for (int row = 0; row < 6; row++) {
    if (leds[col][5 - row] > 0 && cycle % leds[col][5 - row] == 0) {
      //PORTC &= ~ rows[row];
      digitalWrite2(rows[row], LOW);  // Turn on this led
    }
    else {
      //PORTC |= rows[row];
      digitalWrite2(rows[row], HIGH); // Turn off this led
    }
  }
  digitalWrite2(cols[col], HIGH); // Turn whole column on at once (for equal lighting times)
}

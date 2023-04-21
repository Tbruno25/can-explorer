/*
####################################################################################
example sketch to use arduino as CAN interface over serial with python-can / can-explorer
https://github.com/tbruno25/can-explorer

mcp_can library | https://github.com/coryjfowler/MCP_CAN_lib
default 500K baudrate / 8MHz clock speed

channel = "COM1" #Windows OR "/dev/ttyACM0" #Linux 
####################################################################################
*/

#include <mcp_can.h>
#include <SPI.h>

long unsigned int rxId;
unsigned char arrId[4];
unsigned char len = 0;
unsigned char rxBuf[8];
const unsigned char blank[] = {0, 0, 0, 0};

#define CAN0_INT 2 // Set INT to pin 2
MCP_CAN CAN0(10);  // Set CS to pin 10

void setup()
{
  CAN0.begin(MCP_ANY, CAN_500KBPS, MCP_8MHZ); // baudrate and clock speed
  CAN0.setMode(MCP_NORMAL);                   // Set operation mode to normal so the MCP2515 sends acks to received data.
  pinMode(CAN0_INT, INPUT);                   // Configuring pin for /INT input

  delay(50);
  Serial.begin(115200);
}

void loop()
{
  if (!digitalRead(CAN0_INT)) // If CAN0_INT pin is low, read receive buffer
  {
    CAN0.readMsgBuf(&rxId, &len, rxBuf); // read data

    Serial.write(0xAA);                        // start of frame
    Serial.write(blank, 4);                    // timestamp
    Serial.write(len);                         // dlc
    Serial.write((const uint8_t *)(&rxId), 4); // id
    Serial.write(rxBuf, len);                  // payload
    Serial.write(0xBB);                        // end of frame
  }
}

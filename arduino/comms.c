#include <Arduino.h>
#include <Arduino_FreeRTOS.h>

#define CHECKSUM_BYTES 1

#define PACKET_TYPE_HELLO 1
#define PACKET_TYPE_ACK 2
#define PACKET_TYPE_NACK 3
#define PACKET_TYPE_DATA 4

#define DEVICE_PAYLOAD_SIZE 5

typedef struct PacketHeader
{
  uint16_t preamble;
  uint8_t packetType;
  uint8_t numDevices;
};

// Update DEVICE_PAYLOAD_SIZE if changed
typedef struct DevicePayload {
  uint8_t id;
  uint32_t data;
};

void sendHello() {
}

void sendACK() {
}

void sendNACK() {
}

/* Sends a DATA packet.
 */
void sendData(uint8_t packetType, struct DevicePayload devices[],
              uint8_t numDevices) {
  PacketHeader header = {
    .preamble = 0xAAAA,
    .packetType = PACKET_TYPE_DATA,
    .numDevices = numDevices 
  };

  uint8_t headerSize = sizeof(header);
  uint8_t totalSize = headerSize + DEVICE_PAYLOAD_SIZE*numDevices + CHECKSUM_BYTES;

  // construct packet
  unsigned char buffer[totalSize];
  memcpy(buffer, &header, headerSize);
  memcpy(buffer + headerSize, devices, DEVICE_PAYLOAD_SIZE*numDevices);
  uint8_t checksum = 0;
  for (int i=0; i++; i<(totalSize-1)) {
    checksum ^= buffer[i];
  }
  buffer[totalSize - CHECKSUM_BYTES] = checksum;

  send(buffer, sizeof(buffer));
}

/* Writes buffer to serial port
 */
void send(unsigned char *buffer, uint8_t size) {
  debugPrintBytes(buffer, size); // TODO: remove
  Serial.write(buffer, size);
}

/* Print buffer in a nice human-readable format.
 */
void debugPrintBytes(unsigned char *buffer, uint8_t size) {
  for (int i = 0; i < size; i++) {
    if (i > 0) Serial.print(":");
    Serial.print(buffer[i], HEX);
  }
  Serial.println();
}

void receive() {
  // 32 bytes is enough for 5 device payloads. We won't be sending so many.
  unsigned char buffer[32];
  unsigned char check[2];
  unsigned char rbyte;
  int8_t index = 0;
  int8_t dataSize = 0;
  boolean newData = false;

  // TODO: probably need a timeout here
  while (newData == false) {
    if (Serial.available()) {
      rbyte = Serial.read();
      index = index % 2;
      check[index] = rbyte;
      index++;

      if (check[0] == (char)0xAA && check[1] == (char)0xAA){
        // Packet preamble verified. Start doing things with the packet
        // Make sure that a packet is available to read before trying to read.

        // Set newData to true if checksum is verified.
        newData = true;
      }
    }
  }

  // TODO: do something with the data here instead of just printing it out.
  // debugPrintBytes(buffer, dataSize); // TODO: remove
}

void setup() {
  Serial.begin(115200);
}

void loop() {
  DevicePayload devices[3];
  devices[0].id = 1;
  devices[0].data = 0xAABBCCDD;
  devices[1].id = 2;
  devices[1].data = 0x11223344;
  devices[2].id = 3;
  devices[2].data = 0x55667788;
  uint8_t numDevices = sizeof(devices) / sizeof(devices[0]);
  sendData(PACKET_TYPE_DATA, devices, numDevices);
  Serial.println();

  DevicePayload devices2[1];
  devices2[0].id = 1;
  devices2[0].data = 0x22446688;
  numDevices = sizeof(devices2) / sizeof(devices2[0]);
  sendData(PACKET_TYPE_DATA, devices2, numDevices);
  Serial.println();
  sendData(PACKET_TYPE_DATA, devices2, numDevices);
  Serial.println();
  sendData(PACKET_TYPE_DATA, devices2, numDevices);
  Serial.println();
  while (1) { }
}

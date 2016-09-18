#include <Arduino_FreeRTOS.h>
#include <mixLib.h>
mixLib MIXLIB;

#define CHECKSUM_BYTES 1
#define EOL_BYTES 2

#define PACKET_TYPE_HELLO 1
#define PACKET_TYPE_ACK 2
#define PACKET_TYPE_NACK 3
#define PACKET_TYPE_DATA 4

#define DEVICE_PAYLOAD_SIZE 3

typedef struct PacketHeader
{
    uint8_t packetType;
    uint8_t numDevices;
};

// Update DEVICE_PAYLOAD_SIZE if changed
typedef struct DevicePayload 
{
    uint8_t id;
    uint16_t data;
};

uint16_t UltrasonicFront;
uint16_t UltrasonicLeft;
uint16_t UltrasonicRight;

// the setup function runs once when you press reset or power the board
void setup() {
  
  // initialize serial communication at 9600 bits per second:
  Serial.begin(115200);
  Serial1.begin(115200);
  
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB, on LEONARDO, MICRO, YUN, and other 32u4 based boards.
  }
    
  MIXLIB.initialise();
  
  xTaskCreate(
        SendToPi
    ,  (const portCHAR *)"SendToPi"   
    ,  256  // Stack size
    ,  NULL
    ,  1  // priority
    ,  NULL
    );
    
  xTaskCreate(
        ReadUltrasonic
    ,  (const portCHAR *)"ReadUltrasonic"   
    ,  256  // Stack size
    ,  NULL
    ,  1  // priority
    ,  NULL
    );

  // Now the task scheduler, which takes over control of scheduling individual tasks, is automatically started.
}

void loop()
{
  // Empty. Things are done in Tasks.
}

/*--------------------------------------------------*/
/*---------------------- Tasks ---------------------*/
/*--------------------------------------------------*/

void ReadUltrasonic( void *pvParameters ){
    //(void) pvParameters;
    
    for(;;){
      UltrasonicFront = MIXLIB.getSR04_Front_cm();
      UltrasonicLeft = MIXLIB.getSR04_Left_cm();
      UltrasonicRight = 0x5667;//MIXLIB.getSR04_cm();
    }
}


void SendToPi( void *pvParameters ){
    //(void) pvParameters;
    
    for(;;){
      DevicePayload devices[6];
      devices[0].id = 1;
      devices[0].data = UltrasonicFront;
      devices[1].id = 2;
      devices[1].data = UltrasonicLeft;
      devices[2].id = 3;
      devices[2].data = 0xCCDD;
      devices[3].id = 4;
      devices[3].data = 0x3344;
      devices[4].id = 5;
      devices[4].data = 0xEEFF;
      devices[5].id = 6;
      devices[5].data = 0x5566;
      uint8_t numDevices = sizeof(devices) / sizeof(devices[0]);
      sendData(PACKET_TYPE_DATA, devices, numDevices);
    }
}

/* Sends a DATA packet
 *  .
 */
void sendData(uint8_t packetType, struct DevicePayload devices[],
              uint8_t numDevices) {
    PacketHeader header = {
        .packetType = PACKET_TYPE_DATA,
        .numDevices = numDevices
    };

    uint8_t headerSize = sizeof(header);
    uint8_t totalSize = headerSize + DEVICE_PAYLOAD_SIZE*numDevices + CHECKSUM_BYTES + EOL_BYTES;

    // construct packet
    unsigned char buffer[totalSize];
    memcpy(buffer, &header, headerSize);
    memcpy(buffer + headerSize, devices, DEVICE_PAYLOAD_SIZE*numDevices);
    uint8_t checksum = 0;
    for (int i=0; i<(totalSize-(CHECKSUM_BYTES+EOL_BYTES)); i++) {
        checksum ^= buffer[i];
    }
    buffer[totalSize - CHECKSUM_BYTES - EOL_BYTES] = checksum;
    buffer[totalSize - EOL_BYTES] = 0x0D;
    buffer[totalSize - 1] = 0x0A;
    send(buffer, sizeof(buffer));
}

/* Writes buffer to serial port
 */
void send(unsigned char *buffer, uint8_t size) {
    debugPrintBytes(buffer, size); // TODO: remove
    Serial1.write(buffer, size);
    Serial1.flush();
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


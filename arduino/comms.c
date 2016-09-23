#include <Arduino.h>
#include <Arduino_FreeRTOS.h>

#define MAX_BUF_LEN 23
#define NUM_DEVICES 4
#define PACKET_OK 1
#define PACKET_BAD_CHECKSUM 2

typedef struct Packet
{ //Packet Type, Number of Devices, 4x Device ID + value, checksum added later
  uint8_t pktType;
  uint8_t numDevices;
  uint8_t deviceId1;
  uint32_t valueof1;
  uint8_t deviceId2;
  uint32_t valueof2;
  uint8_t deviceId3;
  uint32_t valueof3;
  uint8_t deviceId4;
  uint32_t valueof4;
};

void sendData(uint8_t pktType, uint8_t dev1, uint32_t val1, 
                uint8_t dev2, uint32_t val2, uint8_t dev3, 
                uint32_t val3, uint8_t dev4, uint32_t val4){
  
  Packet pkt = {
    .pktType = pktType,
    .numDevices = NUM_DEVICES,
    .deviceId1 = dev1,
    .valueof1 = val1,
    .deviceId2 = dev2,
    .valueof2 = val2,
    .deviceId3 = dev3,
    .valueof3 = val3,
    .deviceId4 = dev4,
    .valueof4 = val4
  };
  
  char buffer[MAX_BUF_LEN+2];

  serialize(buffer, &pkt, sizeof(pkt));
  sendSerialData(buffer, sizeof(buffer));
}

unsigned int serialize(char *buf, void *p, size_t size){
  char checksum = 0;
  uint8_t startMarker1 = 0xAA; //preamble 0xAAAA
  uint8_t startMarker2 = 0xAA;
  buf[0] = startMarker1;
  buf[1] = startMarker2;
  memcpy(buf+2, p, size);
  for( int i = 2; i < size+2; i++ ){
    checksum ^= buf[i];
  }
  buf[size+3] = checksum;
  //Serial.print("Serialize Checksum = ");
  //Serial.println(checksum);
  return size+3;
}

void sendSerialData(char *buffer, int len){
  Serial1.write(buffer, len);
}

void receiveData(){
  char buffer[MAX_BUF_LEN];
  char check[2];
  Packet pkt;
  char rbyte;
  int index = 0;
  boolean newData = false; 

  while ( Serial.available() > 0 && newData == false ) {
    rbyte = Serial.read();
    index = index % 2;
    check[index] = rbyte;
    index++;
    //Serial.print(check[0]);
    //Serial.println(check[1]);
    
    if ( check[0] == (char)0xAA && check[1] == (char)0xAA ){
      for ( int j = 0; j < 23; j++ ){
        buffer[j] = Serial.read();    
      }
      newData = true;
    }
  }
  
  if (newData == true){
    newData = false;
    unsigned int result = deserialize(&pkt, buffer);
    //process the values here
    if ( result == 1 ){
      Serial.print("Serial Data: ");
      Serial.print(pkt.pktType);
      Serial.print("..");
      Serial.print(pkt.deviceId1);
      Serial.print("..");
      Serial.print(pkt.valueof1);
      Serial.print("..");
      Serial.print(pkt.deviceId2);
      Serial.print("..");
      Serial.print(pkt.valueof2);
      Serial.print("..");
      Serial.print(pkt.deviceId3);
      Serial.print("..");
      Serial.print(pkt.valueof3);
      Serial.print("..");
      Serial.print(pkt.deviceId4);
      Serial.print("..");
      Serial.print(pkt.valueof4);
      Serial.println("..");
    } else {
      Serial.println("Checksum failed?");
    }
  }
}

unsigned int deserialize(void *p, char *buf){
  // numDevices * 5bytes + 1byte pktType + 1byte numDevices
  size_t size = (buf[1] * 5) + 2;
  char checksum = 0;

  for( int i = 0; i < size; i++ ){
    checksum ^= buf[i];
  }
  //Serial.print("Deserialize Checksum = ");
  //Serial.println(checksum);

  if ( checksum == buf[size+1] ){
    memcpy(p, buf, size);
    return PACKET_OK;
  } else {
    return PACKET_BAD_CHECKSUM;
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial1.begin(115200);
}

void loop() {
  sendData(1, 7, 7, 2, 2, 3, 3, 4, 4); // dummy values for now
  receiveData();
  //sendData(1, 8, 8, 6, 6, 3, 4, 5, 4); // dummy values for now
  //receiveData();
}

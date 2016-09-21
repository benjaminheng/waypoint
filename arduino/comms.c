#include <Arduino.h>

typedef struct Packet
{
  uint8_t packetType;
  uint8_t deviceId1;
  uint32_t valueof1;
  uint8_t deviceId2;
  uint32_t valueof2;
  uint8_t deviceId3;
  uint32_t valueof3;
  uint8_t deviceId4;
  uint32_t valueof4;
};

void sendData(uint8_t packetType, uint8_t dev1, uint32_t val1, 
                uint8_t dev2, uint32_t val2, uint8_t dev3, 
                uint32_t val3, uint8_t dev4, uint32_t val4)
{
  Packet pkt;
  char buffer[24];
  pkt.packetType = packetType;
  pkt.deviceId1 = dev1;
  pkt.valueof1 = val1;
  pkt.deviceId2 = dev2;
  pkt.valueof2 = val2;
  pkt.deviceId3 = dev3;
  pkt.valueof3 = val3;
  pkt.deviceId4 = dev4;
  pkt.valueof4 = val4;
  unsigned len = serialize(buffer, &pkt, sizeof(pkt));
  sendSerialData(buffer, len);
}

unsigned int serialize(char *buf, void *p, size_t size)
{
  char checksum = 0;
  buf[0]=size;
  memcpy(buf+1, p, size);
  for(int i=1; i<=size; i++)
  {
    checksum ^= buf[i];
  }
  buf[size+1]=checksum;
  return size+2;
}

void sendSerialData(char *buffer, int len)
{
  for(int i=0; i<len; i++)
  Serial1.write(buffer[i]);
}

void setup() {
  // put your setup code here, to run once:
  Serial1.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  //payload len - packettype - deviceid - device value - ... - checksum
  sendData(1, 1, 1, 2, 2, 3, 3, 4, 4); // dummy values for now
  sendData(1, 5, 5, 6, 6, 7, 7, 8, 8);
}

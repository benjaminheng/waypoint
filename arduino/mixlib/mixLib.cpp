#include "Arduino.h"
#include "mixLib.h"
#include "LSM303.h"
#include "L3G.h"
#include "Wire.h"
#define PIN_URF 10
#define PIN_ECHO_SR04_ARM_RIGHT 40
#define PIN_TRIG_SR04_ARM_RIGHT 41
#define PIN_ECHO_SR04_ARM_LEFT 28
#define PIN_TRIG_SR04_ARM_LEFT 29


mixLib::mixLib(void)
{

}
void mixLib::initialise()
{
	pinMode(PIN_URF,INPUT);
	pinMode(PIN_ECHO_SR04_ARM_RIGHT,INPUT);
	pinMode(PIN_TRIG_SR04_ARM_RIGHT,OUTPUT);
	pinMode(PIN_ECHO_SR04_ARM_LEFT,INPUT);
	pinMode(PIN_TRIG_SR04_ARM_LEFT,OUTPUT);
	Wire.begin();
	compass.init();
	compass.enableDefault();
	gyro.init();
	gyro.enableDefault();
}

void mixLib::loadCompass_gyro(void)
{
	loadGyro();
	loadCompass();
}

void mixLib::loadGyro(void)
{
	gyro.read();
}


void mixLib::loadCompass(void)
{
	compass.read();
}

int16_t mixLib::getGyroX(void)
{
	return gyro.g.x;
}
int16_t mixLib::getGyroY(void)
{
	return gyro.g.y;
}
int16_t mixLib::getGyroZ(void)
{
	return gyro.g.z;
}
int16_t mixLib::getAccX(void)
{
	return compass.a.x;
}
int16_t mixLib::getAccY(void)
{
	return compass.a.y;
}
int16_t mixLib::getAccZ(void)
{
	return compass.a.z;
}
int16_t mixLib::getMagX(void)
{
	return compass.m.x;
}
int16_t mixLib::getMagY(void)
{
	return compass.m.y;
}
int16_t mixLib::getMagZ(void)
{
	return compass.m.z;
}
int mixLib::getURF_cm()
{
	return getURF_inch()*2.54;
}

int mixLib::getURF_inch()
{
	return getURF()/147;
}
int mixLib::getURF()
{
	return pulseIn(PIN_URF,HIGH);
}

int mixLib::getSR04_ArmRight_cm()
{
	return (getSR04_ArmRight()/2) / 29.1; 
}

int mixLib::getSR04_ArmLeft_cm()
{
	return (getSR04_ArmLeft()/2) / 29.1; 
}

int mixLib::getSR04_ArmRight()
{
	digitalWrite(PIN_TRIG_SR04_FRONT, LOW);
	delayMicroseconds(5);
	digitalWrite(PIN_TRIG_SR04_FRONT, HIGH);
	delayMicroseconds(10);
	digitalWrite(PIN_TRIG_SR04_FRONT, LOW);

	return pulseIn(PIN_ECHO_SR04_FRONT,HIGH);
}

int mixLib::getSR04_ArmLeft()
{
	digitalWrite(PIN_TRIG_SR04_LEFT, LOW);
	delayMicroseconds(5);
	digitalWrite(PIN_TRIG_SR04_LEFT, HIGH);
	delayMicroseconds(10);
	digitalWrite(PIN_TRIG_SR04_LEFT, LOW);

	return pulseIn(PIN_ECHO_SR04_LEFT,HIGH);
}

int mixLib::getSR08_Front()
{
  Wire.beginTransmission(0x70);
  Wire.write(0x01); 
  Wire.write(0x00); 
  Wire.endTransmission(); 
  
  Wire.beginTransmission(0x70); 
  Wire.write(0x02); 
  Wire.write(0x8C);
  Wire.endTransmission(); 

  int reading = 0;
  Wire.beginTransmission(0x70); 
  Wire.write(0);      
  Wire.write(byte(0x51));      
  Wire.endTransmission();    
  delay(70);                   
  Wire.beginTransmission(0x70);
  Wire.write(byte(0x02));      
  Wire.endTransmission();      
  Wire.requestFrom(0x70,2);
  if (2 <= Wire.available())   
  {
    reading = Wire.read();  
    reading = reading << 8;    
    reading |= Wire.read(); 
    return reading;
  }
}

int mixLib::getSR02_Right()
{
  Wire.beginTransmission(0x72);
  Wire.write(0x01); 
  Wire.write(0x00); 
  Wire.endTransmission(); 
  
  Wire.beginTransmission(0x72);
  Wire.write(0x02); 
  Wire.write(0x8C);
  Wire.endTransmission(); 

  int reading = 0;
  Wire.beginTransmission(0x72);
  Wire.write(0);      
  Wire.write(byte(0x51));      
  Wire.endTransmission();   
 
  delay(70);                 
  
  Wire.beginTransmission(0x72);
  Wire.write(byte(0x02));      
  Wire.endTransmission();      
  Wire.requestFrom(0x72,2);
  if (2 <= Wire.available())   
  {
    reading = Wire.read();  
    reading = reading << 8;    
    reading |= Wire.read(); 
    return reading;
  }
}

int mixLib::getSR02_Left()
{
  Wire.beginTransmission(0x71);
  Wire.write(0x01); 
  Wire.write(0x00); 
  Wire.endTransmission(); 
  
  Wire.beginTransmission(0x71);
  Wire.write(0x02); 
  Wire.write(0x8C);
  Wire.endTransmission(); 

  int reading = 0;
  Wire.beginTransmission(0x71);
  Wire.write(0);      
  Wire.write(byte(0x51));      
  Wire.endTransmission();  
  
  delay(70);              
     
  Wire.beginTransmission(0x71);
  Wire.write(byte(0x02));      
  Wire.endTransmission();      
  Wire.requestFrom(0x71,2);
  if (2 <= Wire.available())   
  {
    reading = Wire.read();  
    reading = reading << 8;    
    reading |= Wire.read(); 
    return reading;
  }
}
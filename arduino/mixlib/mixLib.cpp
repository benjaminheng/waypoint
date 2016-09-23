#include "Arduino.h"
#include "mixLib.h"
#include "LSM303.h"
#include "L3G.h"
#include "Wire.h"
#define PIN_URF 10
#define PIN_ECHO_SR04 40
#define PIN_TRIG_SR04 41


mixLib::mixLib(void)
{

}
void mixLib::initialise()
{
	pinMode(PIN_URF,INPUT);
	pinMode(PIN_ECHO_SR04,INPUT);
	pinMode(PIN_TRIG_SR04,OUTPUT);
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

int mixLib::getSR04_cm()
{
	return (getSR04()/2) / 29.1; 
}

int mixLib::getSR04()
{
	digitalWrite(PIN_TRIG_SR04, LOW);
	delayMicroseconds(5);
	digitalWrite(PIN_TRIG_SR04, HIGH);
	delayMicroseconds(10);
	digitalWrite(PIN_TRIG_SR04, LOW);

	return pulseIn(PIN_ECHO_SR04,HIGH);
}

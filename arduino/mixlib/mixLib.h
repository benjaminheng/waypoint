#ifndef mixLib_h
#define mixLib_h

#include "Arduino.h"
#include "LSM303.h"
#include "L3G.h"
class mixLib
{
	public:
		mixLib(void);
		void initialise();
		int getURF_inch(void);
		int getURF_cm(void);
		int getSR04_ArmRight_cm(void);
		int getSR04_ArmLeft_cm(void);
		int getSR08_Front(void);
		int getSR02_Left(void);
		int getSR02_Right(void);
		
		int16_t getAccX(void);
		int16_t getAccY(void);
		int16_t getAccZ(void);
		int16_t getMagX(void);
		int16_t getMagY(void);
		int16_t getMagZ(void);
		int16_t getGyroX(void);
		int16_t getGyroY(void);
		int16_t getGyroZ(void);

		void loadCompass(void);
		void loadCompass_gyro(void);
		void loadGyro(void);
	private:
		LSM303 compass;
		L3G gyro;
		int getURF(void);
		int getSR04_ArmRight(void);
		int getSR04_ArmLeft(void);

};

#endif

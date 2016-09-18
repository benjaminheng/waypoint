#include <mixLib.h>
mixLib ola;	
void setup() {
  // put your setup code here, to run once:
  ola.initialise();
  Serial.begin(9600);
}

void loop() {
#if 0 
  Serial.print("here is data for URF: ");
  Serial.println(ola.getURF_cm());
  Serial.println(ola.getURF_inch());
#endif

#if 0
  Serial.print("here is data for SR04: ");
  Serial.println(ola.getSR04_cm());
#endif


#if 0
  ola.loadCompass_gyro(); //load the value from compass and gyro      
  Serial.print(ola.getGyroX());
  Serial.print("  :  ");
  Serial.print(ola.getGyroY());
  Serial.print("  :  ");
  Serial.println(ola.getGyroZ());
  Serial.print("here is data for compass: ");
  Serial.print(ola.getAccX());
  Serial.print("  :  ");
  Serial.print(ola.getAccY());
  Serial.print("  :  ");
  Serial.print(ola.getAccZ());
  Serial.print("|||||||");
  Serial.print(ola.getMagX());
  Serial.print("  :  ");
  Serial.print(ola.getMagY());
  Serial.print("  :  ");
  Serial.println(ola.getMagZ());
#endif
  delay(100);
}

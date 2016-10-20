#include <Arduino_FreeRTOS.h>
#include <mixLib.h>
mixLib MIXLIB;
#include <Wire.h>
#include <Kalman.h>
Kalman kalmanX; // Create the Kalman instances
Kalman kalmanY;

#define RESTRICT_PITCH // Comment out to restrict roll to ±90deg instead - please read: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf

#define MOTOR_LEFT 26
#define MOTOR_RIGHT 27

#define CHECKSUM_BYTES 1
#define EOL_BYTES 2

#define PACKET_TYPE_HELLO 1
#define PACKET_TYPE_ACK 2
#define PACKET_TYPE_NACK 3
#define PACKET_TYPE_DATA 4

#define DEVICE_PAYLOAD_SIZE 3

#define STACKSIZE 512   

#define MAX_BUFFER 25

enum regAddr
{
       WHO_AM_I       = 0x0F,

       CTRL1          = 0x20, // D20H
       CTRL_REG1      = 0x20, // D20, 4200D
       CTRL2          = 0x21, // D20H
       CTRL_REG2      = 0x21, // D20, 4200D
       CTRL3          = 0x22, // D20H
       CTRL_REG3      = 0x22, // D20, 4200D
       CTRL4          = 0x23, // D20H
       CTRL_REG4      = 0x23, // D20, 4200D
       CTRL5          = 0x24, // D20H
       CTRL_REG5      = 0x24, // D20, 4200D
       REFERENCE      = 0x25,
       OUT_TEMP       = 0x26,
       STATUS         = 0x27, // D20H
       STATUS_REG     = 0x27, // D20, 4200D

       OUT_X_L        = 0x28,
       OUT_X_H        = 0x29,
       OUT_Y_L        = 0x2A,
       OUT_Y_H        = 0x2B,
       OUT_Z_L        = 0x2C,
       OUT_Z_H        = 0x2D,

       FIFO_CTRL      = 0x2E, // D20H
       FIFO_CTRL_REG  = 0x2E, // D20, 4200D
       FIFO_SRC       = 0x2F, // D20H
       FIFO_SRC_REG   = 0x2F, // D20, 4200D

       IG_CFG         = 0x30, // D20H
       INT1_CFG       = 0x30, // D20, 4200D
       IG_SRC         = 0x31, // D20H
       INT1_SRC       = 0x31, // D20, 4200D
       IG_THS_XH      = 0x32, // D20H
       INT1_THS_XH    = 0x32, // D20, 4200D
       IG_THS_XL      = 0x33, // D20H
       INT1_THS_XL    = 0x33, // D20, 4200D
       IG_THS_YH      = 0x34, // D20H
       INT1_THS_YH    = 0x34, // D20, 4200D
       IG_THS_YL      = 0x35, // D20H
       INT1_THS_YL    = 0x35, // D20, 4200D
       IG_THS_ZH      = 0x36, // D20H
       INT1_THS_ZH    = 0x36, // D20, 4200D
       IG_THS_ZL      = 0x37, // D20H
       INT1_THS_ZL    = 0x37, // D20, 4200D
       IG_DURATION    = 0x38, // D20H
       INT1_DURATION  = 0x38, // D20, 4200D

       LOW_ODR        = 0x39  // D20H
};

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

uint16_t UltrasonicArmLeft;
uint16_t UltrasonicArmRight;
uint16_t UltrasonicFront;
uint16_t UltrasonicLeft;
uint16_t UltrasonicRight;
uint16_t ALTIMUGyroX;
uint16_t Num_step;
uint16_t Total_dist;
uint16_t heading;
// JQ's Variables
const uint8_t IMUAddress = 0x6B; // AD0 is logic low on the PCB //initally 68
const uint16_t I2C_TIMEOUT = 1000; // Used to check for errors in I2C communication    
const uint8_t address = 0x6B;
/* IMU Data */
//double AccX, AccY, AccZ;
//double gyroX, gyroY, gyroZ;
int16_t tempRaw;
LSM303 compass; // needs to be replaced with 
double gyroXangle, gyroYangle; // Angle calculate using the gyro only
double compAngleX, compAngleY; // Calculated angle using a complementary filter
double kalAngleX, kalAngleY; // Calculated angle using a Kalman filter
uint8_t i2cData[14]; // Buffer for I2C data
    
int16_t AccX, AccY, AccZ, MagX, MagY, MagZ, GyroX, GyroY, GyroZ; // what about compass?

//declare for step counter
const int THRESHOLD = 1300;
const int CHANGING_PERIOD = 1000;
uint32_t lastChange_time;
uint32_t timer;
long x , y , z, xo , yo , zo;
long mag;
long buffer_value[3][MAX_BUFFER] = {{0}};
int pointer = 0;
double distance = 0.0;

int i;
long initial_value[3];
long temp[3]={0};
int count = 0;
//endhere



// the setup function runs once when you press reset or power the board
void setup() {
  
  // initialize serial communication at 9600 bits per second:
  Serial.begin(115200);
  Serial1.begin(115200);
  
  MIXLIB.initialise();
  
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB, on LEONARDO, MICRO, YUN, and other 32u4 based boards.
  }  
  

  // JQ Setup
  Wire.begin();
  #if ARDUINO >= 157
  Wire.setClock(400000UL); // Set I2C frequency to 400kHz
  #else
  TWBR = ((F_CPU / 400000UL) - 16) / 2; // Set I2C frequency to 400kHz
  #endif
  writeReg(LOW_ODR, 0x00);
  writeReg(CTRL_REG4, 0x00);
  writeReg(CTRL_REG1, 0x6F);
  delay(100); // Wait for sensor to stabilize,
  Serial.println("WRITEREGFINISH");
  compass.init();//UNCOMMENT ME
  compass.enableDefault();//UNCOMMENT ME
  compass.read();//UNCOMMENT ME

  //calibrating
  compass.m_min = (LSM303::vector<int16_t>){-32767, -32767, -32767};
  compass.m_max = (LSM303::vector<int16_t>){+32767, +32767, +32767};
  
  Serial.println("COMPASSINITFINISH");
  /* Set kalman and gyro starting angle */
  while (i2cRead(OUT_X_L | (1 << 7), i2cData, 6)); //UNCOMMENT MEE
  
  AccX = compass.a.x; //UNCOMMENT ME
  AccY = compass.a.y; //UNCOMMENT ME
  AccZ = compass.a.z; //UNCOMMENT ME
  //Serial.println("LINE149");
  
  // Source: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf eq. 25 and eq. 26
  // atan2 outputs the value of -π to π (radians) - see http://en.wikipedia.org/wiki/Atan2
  // It is then converted from radians to degrees
  #ifdef RESTRICT_PITCH // Eq. 25 and 26
  double roll  = atan2(AccY, AccZ) * RAD_TO_DEG;
  double pitch = atan(-AccX / sqrt(AccY * AccY + AccZ * AccZ)) * RAD_TO_DEG;
  #else // Eq. 28 and 29
  double roll  = atan(AccY / sqrt(AccX * AccX + AccZ * AccZ)) * RAD_TO_DEG;
  double pitch = atan2(-AccX, AccZ) * RAD_TO_DEG;
  #endif

  kalmanX.setAngle(roll); // Set starting angle
  kalmanY.setAngle(pitch);
  gyroXangle = roll;
  gyroYangle = pitch;
  compAngleX = roll;
  compAngleY = pitch;
  
  timer = micros();
  Serial.println("JQSETUPCOMPLETE");

  //step
  for( int i = 0 ; i < MAX_BUFFER ; i++)
  {
    compass.read();
    adjusting_buffer(compass.a.x, compass.a.y , compass.a.z);
  }
  lastChange_time = millis();

  
  xTaskCreate(
        SendToPi
    ,  (const portCHAR *)"SendToPi"   
    ,  STACKSIZE  // Stack size
    ,  NULL
    ,  1  // priority
    ,  NULL
    );
    
  xTaskCreate(
        ReadUltrasonic1
    ,  (const portCHAR *)"ReadUltrasonic1"   
    ,  STACKSIZE  // Stack size
    ,  NULL
    ,  1  // priority
    ,  NULL
    );
    
  xTaskCreate(
        ReadUltrasonic2
    ,  (const portCHAR *)"ReadUltrasonic2"   
    ,  STACKSIZE  // Stack size
    ,  NULL
    ,  1  // priority
    ,  NULL
    );

  xTaskCreate(
        ReadUltrasonic3
    ,  (const portCHAR *)"ReadUltrasonic3"   
    ,  STACKSIZE  // Stack size
    ,  NULL
    ,  1  // priority
    ,  NULL
    );

  xTaskCreate(
        ReadUltrasonic4
    ,  (const portCHAR *)"ReadUltrasonic4"   
    ,  STACKSIZE  // Stack size
    ,  NULL
    ,  1  // priority
    ,  NULL
    );

  xTaskCreate(
        ReadUltrasonic5
    ,  (const portCHAR *)"ReadUltrasonic5"   
    ,  STACKSIZE  // Stack size
    ,  NULL
    ,  1  // priority
    ,  NULL
    );
    
  xTaskCreate(
      ReadIMU
    ,  "ReadIMU"   
    ,  STACKSIZE  // Stack size
    ,  NULL
    ,  1  // priority
    ,  NULL
    );
      Serial.println("CREATEDREADIMU");
   
    xTaskCreate(
        CalcKalman
    ,  "CalcKalman"   
    ,  STACKSIZE  // Stack size
    ,  NULL
    ,  1  // priority
    ,  NULL
    );
      Serial.println("CREATEDCALCKALMAN");
      
  xTaskCreate(
        CalcSteps
    ,  "CalcSteps"   
    ,  STACKSIZE  // Stack size
    ,  NULL
    ,  1  // priority
    ,  NULL
    );
        Serial.println("CREATEDCALCSTEPS");
        
  xTaskCreate(
        GetCompass
    ,  "GetCompass"   
    ,  STACKSIZE  // Stack size
    ,  NULL
    ,  1  // priority
    ,  NULL
    );
        Serial.println("CREATEDGETCOMPASS"); 
   
   
   
  // Now the task scheduler, which takes over control of scheduling individual tasks, is automatically started.
}

void loop()
{
  // Empty. Things are done in Tasks.
}

/*--------------------------------------------------*/
/*---------------------- Tasks ---------------------*/
/*--------------------------------------------------*/

void ReadIMU( void *pvParameters ){
    Serial.println("INSIDEREADIMU");
    for(;;){
      
    AccX = MIXLIB.getAccX();
    AccX = MIXLIB.getAccX();
    AccY = MIXLIB.getAccY();
    AccZ = MIXLIB.getAccZ();
    MagX = MIXLIB.getMagX();
    MagY = MIXLIB.getMagY();
    MagZ = MIXLIB.getMagZ();
    GyroX = MIXLIB.getGyroX();
    GyroY = MIXLIB.getGyroY();
    GyroZ = MIXLIB.getGyroZ();
    }
}


void CalcKalman( void *pvParameters ){
    for(;;){
  //JQ Kalman processing code
     /* Update all the values */
    
    
    while (i2cRead(OUT_X_L | (1 << 7), i2cData, 14));
    compass.read();
  
    AccX = compass.a.x;
    AccY = compass.a.y;
    AccZ = compass.a.z;
    
    GyroX = (i2cData[1] << 8) | i2cData[0];
    GyroY = (i2cData[3] << 8) | i2cData[2];
    GyroZ = (i2cData[5] << 8) | i2cData[4];
    
    

    double dt = (double)(micros() - timer) / 1000000; // Calculate delta time
    timer = micros();

    // Source: http://www.freescale.com/files/sensors/doc/app_note/AN3461.pdf eq. 25 and eq. 26
    // atan2 outputs the value of -π to π (radians) - see         http://en.wikipedia.org/wiki/Atan2
    // It is then converted from radians to degrees
    #ifdef RESTRICT_PITCH // Eq. 25 and 26
    double roll  = atan2(AccY, AccZ) * RAD_TO_DEG;
    double pitch = atan(-AccX / sqrt(AccY * AccY + AccZ * AccZ)) * RAD_TO_DEG;
    #else // Eq. 28 and 29
    double roll  = atan(AccY / sqrt(AccX * AccX + AccZ * AccZ)) * RAD_TO_DEG;
    double pitch = atan2(-AccX, AccZ) * RAD_TO_DEG;
    #endif

    double gyroXrate = GyroX / 131.0; // Convert to deg/s
    double gyroYrate = GyroY / 131.0; // Convert to deg/s

    #ifdef RESTRICT_PITCH
    // This fixes the transition problem when the accelerometer angle jumps between -180 and 180 degrees
    if ((roll < -90 && kalAngleX > 90) || (roll > 90 && kalAngleX < -90)) {
        kalmanX.setAngle(roll);
        compAngleX = roll;
        kalAngleX = roll;
        gyroXangle = roll;
    } else
        kalAngleX = kalmanX.getAngle(roll, gyroXrate, dt); // Calculate the angle using a Kalman filter

    if (abs(kalAngleX) > 90)
        gyroYrate = -gyroYrate; // Invert rate, so it fits the restriced accelerometer reading
    kalAngleY = kalmanY.getAngle(pitch, gyroYrate, dt);
        #else
    // This fixes the transition problem when the accelerometer angle jumps between -180 and 180 degrees
    if ((pitch < -90 && kalAngleY > 90) || (pitch > 90 && kalAngleY < -90)) {
        kalmanY.setAngle(pitch);
        compAngleY = pitch;
        kalAngleY = pitch;
        gyroYangle = pitch;
    } else
        alAngleY = kalmanY.getAngle(pitch, gyroYrate, dt); // Calculate the angle using a Kalman filter

    if (abs(kalAngleY) > 90)
        gyroXrate = -gyroXrate; // Invert rate, so it fits the restriced accelerometer reading
        kalAngleX = kalmanX.getAngle(roll, gyroXrate, dt); // Calculate the angle using a Kalman filter
    #endif

    gyroXangle += gyroXrate * dt; // Calculate gyro angle without any filter
    gyroYangle += gyroYrate * dt;
    //gyroXangle += kalmanX.getRate() * dt; // Calculate gyro angle using the unbiased rate
    //gyroYangle += kalmanY.getRate() * dt;

    compAngleX = 0.93 * (compAngleX + gyroXrate * dt) + 0.07 * roll; // Calculate the angle using a Complimentary filter
    compAngleY = 0.93 * (compAngleY + gyroYrate * dt) + 0.07 * pitch;

  // Reset the gyro angle when it has drifted too much
    if (gyroXangle < -180 || gyroXangle > 180)
        gyroXangle = kalAngleX;
    if (gyroYangle < -180 || gyroYangle > 180)
        gyroYangle = kalAngleY;

  /* Print Data */
    #if 0 // Set to 1 to activate
    Serial.print(AccX); Serial.print("\t");
    Serial.print(AccY); Serial.print("\t");
    Serial.print(AccZ); Serial.print("\t");

    //  Serial.print(gyroX); Serial.print("\t\t");
    //  Serial.print(gyroY); Serial.print("\t\t");
    //  Serial.print(gyroZ); Serial.print("\t\t");

    Serial.print("\t");
    #endif
    #if 0
    Serial.print("i am here");
    Serial.print(roll); Serial.print("\t");  Serial.print(pitch); Serial.print("\t");
    Serial.print("\t");
    Serial.print(gyroXangle); Serial.print("\t");  Serial.print(gyroYangle); Serial.print("\t");
    Serial.print("\t");
    Serial.print(kalAngleX); Serial.print("\t");Serial.print(kalAngleY); Serial.print("\t");
    ALTIMUGyroX = gyroXangle;
    Serial.print("\t");

    //  Serial.print(compAngleX); Serial.print("\t");//  Serial.print(compAngleY); Serial.print("\t");
  
    #endif
    #if 0 // Set to 1 to print the temperature
    Serial.print("\t");

    double temperature = (double)tempRaw / 340.0 + 36.53;
    Serial.print(temperature); Serial.print("\t");
    #endif

    Serial.print("\r\n");
    delay(20); //MAYBE NEED TO COMMENT OUT
    }
  
}

void GetCompass( void *pvParameters ){
  for(;;){
    Serial.println("I GOT INNNNNNNNNNNNNNNNNNNNNNNNN");
    compass.read();
    heading = compass.heading();
    Serial.println("I READ THE COMPASS");
  }
}

void CalcSteps( void *pvParameters ){
  //JQ Step counting code
  for(;;){
  compass.read(); //load the value from compass and gyro  
  
//  double dt = (double)(micros() - timer) / 1000000; // Calculate delta time
//  timer = micros();
//  double roll = ola.getAccX();
//  distance += kalman.getAngle(0,roll-initial_value[0],dt);
//  Serial.println(distance);
  xo = compass.a.x;
  yo = compass.a.y;
  zo = compass.a.z;
  adjusting_buffer(xo,yo,zo);
  
  x=xo-initial_value[0];
  y=yo-initial_value[1];
  z=zo-initial_value[2];
//  Serial.print("here is data for compass: ");
//  Serial.print(x);
//  Serial.print("  :  ");
//  Serial.print(y);
//  Serial.print("  :  ");
//  Serial.print(z);
//  Serial.print("|||||||");
  
  mag = sqrt((x*x) + (y*y)+ (z*z));
  //Serial.print(mag);

  if(mag > THRESHOLD && (millis()-lastChange_time > CHANGING_PERIOD ))
  {
    count++;
    addDistance(x);
    lastChange_time = millis();
    
  }
  //Serial.print("distance : ");
  //Serial.print(distance);
  //Serial.print("  counttttt:");
  //Serial.println(count);
  Num_step = count;
  Total_dist = distance;
  delay(100);
  }
}

void ReadUltrasonic1( void *pvParameters ){
    for(;;){
      UltrasonicArmLeft = MIXLIB.getSR04_ArmLeft_cm();
      if(UltrasonicArmLeft > 30) {
        digitalWrite(MOTOR_LEFT, HIGH);  
      } else {
        digitalWrite(MOTOR_LEFT, LOW);
      }
    }
}

void ReadUltrasonic2( void *pvParameters ){
    for(;;){
      UltrasonicArmRight = MIXLIB.getSR04_ArmRight_cm();
      if(UltrasonicArmRight > 30) {
        digitalWrite(MOTOR_RIGHT, HIGH);  
      } else {
        digitalWrite(MOTOR_RIGHT, LOW);
      }
    }
}

void ReadUltrasonic3( void *pvParameters ){
    for(;;){
      UltrasonicFront = MIXLIB.getSR08_Front();
    }
}

void ReadUltrasonic4( void *pvParameters ){
    for(;;){
      UltrasonicLeft = MIXLIB.getSR02_Left();
    }
}

void ReadUltrasonic5( void *pvParameters ){   
    for(;;){
      UltrasonicRight = MIXLIB.getSR02_Right();
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
      devices[2].data = UltrasonicRight;
      devices[3].id = 4;
      devices[3].data = Total_dist;
      devices[4].id = 5;
      devices[4].data = Num_step;
      devices[5].id = 6;
      devices[5].data = heading;
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

//
//
//
//     JQ's Random but necessary functions
//
//
//
void writeReg(byte reg, byte value)
{
  //Serial.println("INSIDEWRITEREG");
  Wire.beginTransmission(address);
  Wire.write(reg);
  Wire.write(value);
  Wire.endTransmission();
}

uint8_t i2cWrite(uint8_t registerAddress, uint8_t data, bool sendStop) {
  //Serial.println("INSIDEI2CWRITE1");
  return i2cWrite(registerAddress, &data, 1, sendStop); // Returns 0 on success
}

uint8_t i2cWrite(uint8_t registerAddress, uint8_t *data, uint8_t length, bool sendStop) {
  //Serial.println("INSIDEI2CWRITE2");
  Wire.beginTransmission(IMUAddress);
  Wire.write(registerAddress);
  Wire.write(data, length);
  uint8_t rcode = Wire.endTransmission(sendStop); // Returns 0 on success
  if (rcode) {
    //Serial.print(F("i2cWrite failed: "));
    Serial.println(rcode);
  }
  return rcode; // See: http://arduino.cc/en/Reference/WireEndTransmission
}

uint8_t i2cRead(uint8_t registerAddress, uint8_t *data, uint8_t nbytes) {
    //Serial.println("INSIDEI2CREAD");
  uint32_t timeOutTimer;
  Wire.beginTransmission(IMUAddress);
  Wire.write(registerAddress);
  uint8_t rcode = Wire.endTransmission(false); // Don't release the bus
  if (rcode) {
    Serial.print(F("i2cRead failed: "));
    Serial.println(rcode);
    return rcode; // See: http://arduino.cc/en/Reference/WireEndTransmission
  }
  Wire.requestFrom(IMUAddress, nbytes, (uint8_t)true); // Send a repeated start and then release the bus after reading
  for (uint8_t i = 0; i < nbytes; i++) {
    if (Wire.available())
      data[i] = Wire.read();
    else {
      timeOutTimer = micros();
      while (((micros() - timeOutTimer) < I2C_TIMEOUT) && !Wire.available());
      if (Wire.available())
        data[i] = Wire.read();
      else {
        Serial.println(F("i2cRead timeout"));
        return 5; // This error value is not already taken by endTransmission
      }
    }
  }
  return 0; // Success
}


void addDistance(long x)
{
  double rate = abs(x)/1000.0;
  if(abs(x) > 1000)
  {
    distance = distance + (0.4*rate);
    
  }
  else
  {
    distance = distance + 0.4;
  }
}

void adjusting_buffer(long xo , long yo, long zo)
{
  buffer_value[0][pointer] = xo;
  buffer_value[1][pointer] = yo;
  buffer_value[2][pointer] = zo;
  pointer++;
  if( pointer == MAX_BUFFER)
  {
    pointer = 0;
    
  }
      for(int i = 0; i < MAX_BUFFER ; i ++)
    {
      temp[0] = temp[0] + buffer_value[0][i];
      temp[1] = temp[1] + buffer_value[1][i];
      temp[2] = temp[2] + buffer_value[2][i];
    }
    for(int i = 0 ; i < 3 ; i++)
    {
      initial_value[i] = temp[i] / MAX_BUFFER;
      temp[i] = 0;
    }

  
}

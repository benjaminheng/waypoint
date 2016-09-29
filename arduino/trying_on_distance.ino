#include <Kalman.h>

#include <mixLib.h>
mixLib ola;
int i;
long initial_value[3];
long temp[3]={0};
uint32_t timer;
double distance = 0.0;

const int MAX_BUFFER = 25;
Kalman kalman;
long x , y , z, xo , yo , zo;
long mag;
long buffer_value[3][MAX_BUFFER] = {{0}};
int pointer = 0;

const int THRESHOLD = 1500;
const int CHANGING_PERIOD = 1000;
uint32_t lastChange_time;




int count = 0;
void setup() {
  // put your setup code here, to run once:
  ola.initialise();
  Serial.begin(9600);
  
  for( int i = 0 ; i < MAX_BUFFER ; i++)
  {
    ola.loadCompass_gyro();
    adjusting_buffer(ola.getAccX(), ola.getAccY() , ola.getAccZ());
  }
  lastChange_time = millis();
  
//  kalman.setAngle(0);
  
}

void loop() {




  ola.loadCompass_gyro(); //load the value from compass and gyro  
  
//  double dt = (double)(micros() - timer) / 1000000; // Calculate delta time
//  timer = micros();
//  double roll = ola.getAccX();
//  distance += kalman.getAngle(0,roll-initial_value[0],dt);
//  Serial.println(distance);
  xo = ola.getAccX();
  yo = ola.getAccY();
  zo = ola.getAccZ();
  adjusting_buffer(xo,yo,zo);
  
  x=xo-initial_value[0];
  y=yo-initial_value[1];
  z=zo-initial_value[2];
  Serial.print("here is data for compass: ");
  Serial.print(x);
  Serial.print("  :  ");
  Serial.print(y);
  Serial.print("  :  ");
  Serial.print(z);
  Serial.print("|||||||");


  
  mag = sqrt((x*x) + (y*y)+ (z*z));
  Serial.print(mag);

  if(mag > THRESHOLD && (millis()-lastChange_time > CHANGING_PERIOD ))
  {
    count++;
    addDistance(x);
    lastChange_time = millis();
    
  }
  Serial.print("distance : ");
  Serial.print(distance);
  Serial.print("  counttttt:");
  
  Serial.println(count);
  
  delay(100);
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


#include <Wire.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include "keys.h"
#include "Adafruit_seesaw.h"

/*PINS USED
D2 - SDA
D1 - SCL
D6 - Power sensor
D8 - Power pump
D7 - Input for water level sensor 1
D5 - Input for water level sensor 2
*/

//Setup global variables
Adafruit_seesaw ss; //create seesaw object for moisture sensor

WiFiUDP Udp;
unsigned int localPort = 4210;
char sensorData[15];
IPAddress ip(10, 43, 1, 178);
unsigned int remotePort = 20001;
char recvData[255];


//Sensor related global variables
char waterlvl;
uint16_t moisture;
int pumperr = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, passwd);
  while(WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.printf(".");  
  }
  Serial.println("Connected");

  Udp.begin(localPort);

  //Configure wires for i2c and set GPIO for sensor operations
  Wire.begin(D2,D1);
  pinMode(D6, OUTPUT); //Power for all sensors
  pinMode(D8, OUTPUT); //Power for pump
  pinMode(D5, INPUT_PULLUP); //input for water level sensor 1
  pinMode(D7, INPUT_PULLUP); //input for water level sensor 2  


  digitalWrite(D6, HIGH); //GPIO 12 needs to momentarily turned on for seesaw library
  if (!ss.begin(0x36)){
    Serial.println("ERROR! seesaw not found");
    while(1);
  }else{
    Serial.print("seesaw started! version: ");
    Serial.println(ss.getVersion(),HEX);
  }
  digitalWrite(D6, LOW); //turn it off to conserver power  

}

//Water level operation
char SampleWaterLevel()
{
  if (digitalRead(D5) == LOW) //Read input 
  {
    if (digitalRead(D7) == LOW)
    {
      return 'C';
    }
    else
    {
      return 'L';
    }
  }
  else
  {
    return 'G';
  }
}

//Moisture sensor operation
uint16_t SampleMoistureLevel()
{
  uint16_t temp_moisture = 0;
  uint16_t tot_moisture = 0;  
  digitalWrite(D6, HIGH);  //turn sensor on
  for (int i=0; i < 5; i++) //sample 5 times
  {
    temp_moisture = ss.touchRead(0);
    tot_moisture += temp_moisture;
    //Serial.print("Moisture:");
    //Serial.println(temp_moisture);
    delay(100);
  }  
  digitalWrite(D6, LOW); //turn off sensor
  return uint16_t(tot_moisture / 5); //this should probably be mode
}


void loop() {
  digitalWrite(D8, LOW); //ensure pump power is off at the beginning of next loop
  moisture=SampleMoistureLevel();
  waterlvl=SampleWaterLevel();
  sprintf(sensorData, "%04d%c%d", moisture, waterlvl, pumperr);
  Serial.print("Sending data: ");
  Serial.println(sensorData);
  Udp.beginPacket(ip, remotePort);
  Udp.write(sensorData);
  Udp.endPacket();
  for(int i=0; i < 10; i++)
  {
    int fromRPI = Udp.parsePacket();
    if (fromRPI)
    {
      //Serial.printf("Received %d bytes from %s, port %d\n", fromRPI, Udp.remoteIP().toString().c_str(), Udp.remotePort());
      int len =Udp.read(recvData, 255);
      if (len > 0)
      {
        if (recvData[0] == '1')
        {
          int waterLvlNow = SampleWaterLevel();
          if (waterLvlNow != 'C')
          {
            Serial.print("Turning on pump ");
            int dur = ((recvData[1] - '0')*100 + (recvData[2] - '0')*10 + (recvData[3] - '0')) * 1000;
            Serial.println(dur);
            digitalWrite(D8, HIGH);
            delay(dur);
            digitalWrite(D8, LOW);
            pumperr = 0;
          }
          else {
            pumperr = 1;
          }
        }
        else {
          Serial.println("Received packet, but pump switch is off...");
          pumperr = 1;
        }
        break;
      }
    }
    delay(400);
  }
  delay(20000); 

}

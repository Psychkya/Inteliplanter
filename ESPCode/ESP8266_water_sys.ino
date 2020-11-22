#include <Wire.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include "keys.h"
#include "Adafruit_seesaw.h"

//Setup global variables
Adafruit_seesaw ss; //create seesaw object for moisture sensor

WiFiUDP Udp; //setup UDP object
unsigned int localPort = 4210; //ESP8266 local port
char sensorData[15]; //buffer to store hold sensor data
IPAddress remoteIP(192, 168, 1, 178); //Raspberry PI IP address
unsigned int remotePort = 20001; //Raspberry PI port
char recvData[255]; //buffer to receive data

//Sensor related global variables
uint16_t waterlvl;
uint16_t moisture;
int pumperr = 0;

void setup() {
  //set baud rate
  Serial.begin(115200);

  //Connect to Wifi
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, passwd);
  while(WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.printf(".");  
  }
  Serial.println("Connected");
  Udp.begin(localPort); //Configure local port  to listen/send over

  //Configure wires for i2c and set GPIO for sensor operations
  Wire.begin(4,5);
  pinMode(12, OUTPUT); //for water level
  pinMode(14, OUTPUT); //for moisture sensor
  pinMode(15, OUTPUT); //for pump
  
  digitalWrite(14, HIGH); //GPIO 14 needs to momentarily turned on for seesaw library
  if (!ss.begin(0x36)){
    Serial.println("ERROR! seesaw not found");
    while(1);
  }else{
    Serial.print("seesaw started! version: ");
    Serial.println(ss.getVersion(),HEX);
  }
  digitalWrite(14, LOW); //turn it off to conserver power
  
}

//Water level operation
uint16_t SampleWaterLevel()
{
  uint16_t temp_waterlvl = 0;
  uint16_t tot_waterlvl = 0;
  digitalWrite(12, HIGH); //turn sensor on  
  for (int i=0; i < 5; i++) //sample 5 times
  {
    delay(100);
    temp_waterlvl = analogRead(A0);
    tot_waterlvl += temp_waterlvl;
    Serial.print("Water:");
    Serial.println(temp_waterlvl);
  }
  digitalWrite(12, LOW);  //turn sensor off
  return uint16_t(tot_waterlvl / 5); //this probably should be mode and perhaps put some delta smartness
}

//Moisture sensor operation
uint16_t SampleMoistureLevel()
{
  uint16_t temp_moisture = 0;
  uint16_t tot_moisture = 0;  
  digitalWrite(14, HIGH);  //turn sensor on
  for (int i=0; i < 5; i++) //sample 5 times
  {
    temp_moisture = ss.touchRead(0);
    tot_moisture += temp_moisture;
    Serial.print("Moisture:");
    Serial.println(temp_moisture);
    delay(100);
  }  
  digitalWrite(14, LOW); //turn off sensor
  return uint16_t(tot_moisture / 5); //this should probably be mode
}

void loop() {

  waterlvl = SampleWaterLevel();
  Serial.print("Final water level: ");
  Serial.println(waterlvl);  
  
  moisture = SampleMoistureLevel();
  Serial.print("Final moisture level: ");
  Serial.println(moisture);  
  
  //UDP portion
  sprintf(sensorData, "%04d%04d%d", moisture, waterlvl, pumperr);
  Serial.print("Sensor data sent: ");
  Serial.println(sensorData);
  Udp.beginPacket(remoteIP, remotePort);
  Udp.write(sensorData);
  Udp.endPacket();

  //Wait for a max of 1 seconds from response from RPI (in reality perhaps 5 seconds)
  int len = 0;
  for(int i=0; i < 10; i++)
  {
    int fromRPI = Udp.parsePacket();
    if (fromRPI)
    {
      Serial.printf("Received %d bytes from %s, port %d\n", fromRPI, Udp.remoteIP().toString().c_str(), Udp.remotePort());
      len = Udp.read(recvData, 255);
      if (len > 0)
      {
        recvData[len] = 0;
        Serial.printf("content: %s\n", recvData);
        break;
      }
    }
    delay(100);
  }
  if (len > 0)
  {
    if (recvData[0] == '1')
    {
      int waterLvlNow = SampleWaterLevel();
      if (waterLvlNow > 200)
      {
        Serial.println("Turning on pump");
        int dur = ((recvData[1] - '0')*100 + (recvData[2] - '0')*10 + (recvData[3] - '0')) * 1000;
        Serial.print("Turning on pump on for ");
        Serial.println(dur);
        digitalWrite(15, HIGH);
        delay(dur);
        digitalWrite(15, LOW);
      }
      else {
        Serial.println("Water level too low!");
      }
    }
    else {
      Serial.println("Received packet, but pump switch is off...");
    }
  }
  
  delay(5000);
  
}

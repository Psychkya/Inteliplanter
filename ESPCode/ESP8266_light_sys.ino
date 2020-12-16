#include <Wire.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include "keys.h"
#include "Adafruit_SI1145.h"

/*PINS
 * D5 - Sensor power
 * D6 - Power toggle
 * D7 - Cycle dimmer
 */

//UDP and Wifi global vars
WiFiUDP Udp;
unsigned int localPort = 4210;
IPAddress ip(10, 43, 1, 178);
unsigned int  remotePort = 20002;
char sensorData[25];
char recvData[255];

Adafruit_SI1145 uv;
const int MaxLevel = 9;

void setup() {
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


  pinMode(D5, OUTPUT);
  pinMode(D6, OUTPUT);
  pinMode(D7, OUTPUT);

  digitalWrite(D5, HIGH);
  delay(100);
  uv = Adafruit_SI1145();
  if (! uv.begin()) {
    Serial.println("Didn't find Si1145");
    while (1);
  }  
  //digitalWrite(D5, LOW);

}

void loop() {

  //Light sensor outputs
  //digitalWrite(D5 , HIGH);
  //delay(1000);
  int VisLight = uv.readVisible();
  int IRLight = uv.readIR();
  int UVIndex = (int)(uv.readUV() * 100);

  Serial.print("Vis: ");
  Serial.println(VisLight);
  Serial.print("IR: ");
  Serial.println(IRLight);
  Serial.print("UV: ");
  Serial.println(UVIndex);  

  sprintf(sensorData, "%04d%04d%04d", VisLight, IRLight, UVIndex);  

  Serial.print("Sensor data: ");
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
        recvData[len] = 0;
        if (recvData[0] != 'x')
        {
          digitalWrite(D6, HIGH);
          Serial.println("Light switched toggled!");
          delay(200);
          digitalWrite(D6, LOW);
        }
        if (recvData[1] != 'x')
        {
          int count = (recvData[1] - '0')*10 + (recvData[2] - '0');
          for (int i=0; i < count; i++)
          {
            digitalWrite(D7, HIGH);
            delay(200);
            Serial.printf("Dimmer click %d!", i);
            Serial.println();
            digitalWrite(D7, LOW);
            delay(100);
          }
        }
        Serial.printf("content: %s\n", recvData);
        break;
      }
    }
    delay(400);
  }  
  //digitalWrite(D5, LOW);
  delay(10000);
  

}

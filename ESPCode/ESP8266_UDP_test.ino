
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include "keys.h"

WiFiUDP Udp;
unsigned int localPort = 8888;
char *replyPacket = "Hello from ESP866";
IPAddress ip(192, 168, 1, 178);
unsigned int remotePort = 20001;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, passwd);
  while(WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");  
  }
  Serial.println("Connected");

  //Udp.begin(localPort);

}

void loop() {
  // put your main code here, to run repeatedly:
  Udp.beginPacket(ip, remotePort);
  Udp.write(replyPacket);
  Udp.endPacket();
  delay(2000);

}

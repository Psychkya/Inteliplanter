void setup() {
  Serial.begin(115200);
  pinMode(12, OUTPUT);
  digitalWrite(12, HIGH);

}
int moistureVal;
void loop() {
  moistureVal = analogRead(A0);
  Serial.print("Moisture :");
  Serial.println(moistureVal);
  delay(500);
  
  // put your main code here, to run repeatedly:

}

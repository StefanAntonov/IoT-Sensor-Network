#include <Adafruit_AHTX0.h>
#include <MAX44009.h>
#include <Wire.h>

Adafruit_AHTX0 aht;
MAX44009 Lux(0x4A);

void setup() {
  Lux.Begin(0, 188000);
  Wire.begin();
  delay(1000);
  
  Serial.begin(9600);
  if (!aht.begin()) {
    Serial.println("Could not find AHT? Check wiring");
    while (1){delay(10);}
  }
  Serial.println("--aht10 or aht20 found--");
}

void loop() {
  sensors_event_t humidity, temp;
  aht.getEvent(&humidity, &temp);// populate temp and humidity objects with fresh data
  
  Serial.println("SN-2 :");//Station Number
  Serial.print("T: "); Serial.println(temp.temperature);//print Temperature
  Serial.print("H: "); Serial.println(humidity.relative_humidity);//print Relative Humidity
  Serial.print("L: "); Serial.println(Lux.GetLux());//print Ambient light
  
  delay(5000);
}

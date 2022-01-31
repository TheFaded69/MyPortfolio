#include <Adafruit_BME280.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <SPI.h>
#include <iarduino_OLED.h>

#define SEALEVELPRESSURE_HPA (1013.25)

iarduino_OLED myOLED(0x3C);
extern uint8_t MediumFont[];                               

Adafruit_BME280 bme1;
Adafruit_BME280 bme2;
Adafruit_BME280 bme3;

enum
{
  FIRST_BME = 0,
  SECOND_BME = 1,
  THIRD_BME = 2,
};

struct SensorsData
{
  float firstBME_temp;
  float secondBME_temp;
  float thirdBME_temp;

  float firstBME_press;
  float secondBME_press;
  float thirdBME_press;

  float firstBME_humid;
  float secondBME_humid;
  float thirdBME_humid;
};

void SetAdress(uint8_t enum_adress)
{
  Wire.beginTransmission(0x70); 
  Wire.write(1 << enum_adress);
  Wire.endTransmission();
}

void setup()
{
  Serial.begin(9600);

  myOLED.begin();
  myOLED.setFont(MediumFont);

  delay(500);
  
  SetAdress(FIRST_BME);
  if (!bme1.begin(0x76))
  {
    Serial.println("Could not find a valid first BME280 sensor, check wiring!");
  }
  
  SetAdress(SECOND_BME);
  if (!bme2.begin(0x76))
  {
    Serial.println("Could not find a valid second BME280 sensor, check wiring!");
  }

  SetAdress(THIRD_BME);
  if (!bme3.begin(0x76))
  {
    Serial.println("Could not find a valid second BME280 sensor, check wiring!");
  }
  
  delay(1000);
}


void loop() 
{
  SensorsData allData;
  
  SetAdress(FIRST_BME);
  allData.firstBME_temp = bme1.readTemperature();
  allData.firstBME_humid = bme1.readHumidity();
  allData.firstBME_press = bme1.readPressure();
  
  myOLED.setCursor(5, 20);
  myOLED.print("T1: ");
  myOLED.print(allData.firstBME_temp);
  myOLED.print("C");
  myOLED.setCursor(5, 40);
  myOLED.print("H1: ");
  myOLED.print(allData.firstBME_humid);
  myOLED.print("%");
  myOLED.setCursor(5, 60);
  myOLED.print("P1: ");
  myOLED.print(allData.firstBME_press);

  delay(5000);
  
  SetAdress(SECOND_BME);
  allData.secondBME_temp = bme2.readTemperature();
  allData.secondBME_humid = bme2.readHumidity();
  allData.secondBME_press = bme2.readPressure();
  
  myOLED.setCursor(5, 20);
  myOLED.print("T2: ");
  myOLED.print(allData.secondBME_temp);
  myOLED.print("C");
  myOLED.setCursor(5, 40);
  myOLED.print("H2: ");
  myOLED.print(allData.secondBME_humid);
  myOLED.print("%");
  myOLED.setCursor(5, 60);
  myOLED.print("P2: ");
  myOLED.print(allData.secondBME_press);
  
  delay(5000);
  
  SetAdress(THIRD_BME);
  
  allData.thirdBME_temp = bme3.readTemperature();
  allData.thirdBME_humid = bme3.readHumidity();
  allData.thirdBME_press = bme3.readPressure();
  
  myOLED.setCursor(5, 20);
  myOLED.print("T3: ");
  myOLED.print(allData.thirdBME_temp);
  myOLED.print("C");
  myOLED.setCursor(5, 40);
  myOLED.print("H3: ");
  myOLED.print(allData.thirdBME_humid);
  myOLED.print("%");
  myOLED.setCursor(5, 60);
  myOLED.print("P3: ");
  myOLED.print(allData.thirdBME_press);
  
  delay(5000);
  
}

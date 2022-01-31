#include <Adafruit_BME280.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <SPI.h>
#include <iarduino_OLED.h>
#include <DallasTemperature.h>
#include <OneWire.h>
#include <GyverPID.h>

#define SEALEVELPRESSURE_HPA (1013.25)

#define RELAY_PIN 22                                // выход для подключения реле нагревателя нагревателя
#define PIN_FAN 23                                  // выход для подключения реле включения вентилятора

#define HEAT_INTERVAL 1000                          // цикл работы реле нагрева, 1 секунда, измеряется в мс,            
#define PERIOD_SENSORS_DISPLAY 10000                // период обновления данных на дисплее, 1 секунда, в мс
#define PERIOD_SENSORS 10000                        // период считывания данных с датчиков, 1 секунда, в мс   
#define PERIOD_DISPLAY 1000                         // период обновления времени на дисплее, 1 секунда, в мс   
#define PERIOD_PID 1000                             // период работы ПИД регулятора
#define PERIOD_MIN_DRYING 7200000                   // время минимальной сушки перед возможным повышением температуры

#define DS_PIN 12                                   // вход датчика DS18B20

#define MAX_POWER 210                               // максимальная мощность нагревателя

iarduino_OLED myOLED(0x3C);
extern uint8_t MediumFont[];  

int it = 1;
int i = 0;

OneWire oneWire(DS_PIN);
DallasTemperature sensor_DS18B20(&oneWire);
DeviceAddress insideThermometer;

Adafruit_BME280 bme1;
Adafruit_BME280 bme2;
Adafruit_BME280 bme3;

GyverPID regulator(200, 10, 0, 1000);

unsigned long work_time;

float Temp_meas = 0;                                  //температура воздуха после нагревателя DS18B20
float Temp_task = 55;                                 //заданная температура для ПИД

float Power = 0;                                      // мощность, потребленная в процессе сушки

unsigned long time_sensors = 0;                       // время последнего считывания данных с датчиков, в мс 
unsigned long time_display = 0;                       // время последнего обновления времени на дисплее, в мс 
unsigned long time_sensors_display = 0;               // время последнего обновдения данных на дисплее, в мс 
unsigned long Heat_last = 0;                          // последнее время включения нагрева, измеряется в мс
unsigned long time_PID = 0;                           // последнее время вызова ПИД
unsigned long time_min_drying = 0;                    // время минимальной сушки до возможного повышения температуры

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

SensorsData allData;
String arrayOfData[100];

void SetAdress(uint8_t enum_adress);

void setup()
{
  Serial.begin(9600);

  pinMode(PIN_FAN, OUTPUT);                                     // устанавливаем пин в режим вывода
  pinMode(RELAY_PIN,OUTPUT);
  pinMode(DS_PIN, INPUT);                                       // устанавливаем пин в режим ввода
  pinMode(DS_PIN+1, INPUT);                                     // устанавливаем пин в режим ввода

  sensor_DS18B20.begin();
  sensor_DS18B20.setResolution(insideThermometer, 10);
  sensor_DS18B20.setWaitForConversion(false);
  sensor_DS18B20.requestTemperatures();

  myOLED.begin();
  myOLED.setFont(MediumFont);
  
  SetAdress(FIRST_BME);
  if (!bme1.begin(0x76))
  {
    Serial.println("Первый датчик не работает");
  }
  
  SetAdress(SECOND_BME);
  if (!bme2.begin(0x76))
  {
    Serial.println("Второй датчик не работает");
  }

  SetAdress(THIRD_BME);
  if (!bme3.begin(0x76))
  {
    Serial.println("Третий датчик не работает");
  }

  regulator.setDirection(NORMAL);                   // направление регулирования (NORMAL/REVERSE). ПО УМОЛЧАНИЮ СТОИТ NORMAL
  regulator.setLimits(0, 1000);                     // пределы (ставим для 8 битного ШИМ). ПО УМОЛЧАНИЮ СТОЯТ 0 И 255
  regulator.setpoint = Temp_task;                   // сообщаем регулятору температуру, которую он должен поддерживать
  
  delay(1000);
}


void loop() 
{  
 
  if(millis() - work_time > 10000)
  { 
    work_time = millis();

    SetAdress(FIRST_BME);
      
    allData.firstBME_temp = bme1.readTemperature();
    allData.firstBME_humid = bme1.readHumidity();
    allData.firstBME_press = bme1.readPressure();

    SetAdress(SECOND_BME);
      
    allData.secondBME_temp = bme2.readTemperature();
    allData.secondBME_humid = bme2.readHumidity();
    allData.secondBME_press = bme2.readPressure();

    SetAdress(THIRD_BME);
      
    allData.thirdBME_temp = bme3.readTemperature();
    allData.thirdBME_humid = bme3.readHumidity();
    allData.thirdBME_press = bme3.readPressure();

    String currentData = "Измерение " + (String)(i + 1) + "\tT1: " + (String)allData.firstBME_temp + " C\tH1: " + (String)allData.firstBME_humid + " %\tP1: " + (String)allData.firstBME_press + " Pa\t" + "T2: " + (String)allData.secondBME_temp + " C\tH2: " + (String)allData.secondBME_humid + " %\tP2: " + (String)allData.secondBME_press + " Pa\t" + "T3: " + (String)allData.thirdBME_temp + " C\tH3: " + (String)allData.thirdBME_humid + " %\tP3: " + (String)allData.thirdBME_press + " Pa\n";
    Serial.print(currentData);
    
    arrayOfData[i] = currentData;
    i++;
//    if (i==100)                       //Отправление массива данных размором 100, реализации пока что нет
//    {
//      sendAllData(arrayOfData);
//      
//      i = 0;
//    }
    
    switch (it)
    {
      case 1:  
        
        myOLED.setCursor(5, 20);
        myOLED.print("T1: " + (String)allData.firstBME_temp + "C");
        myOLED.setCursor(5, 40);
        myOLED.print("H1: " + (String)allData.firstBME_humid + "%");
        myOLED.setCursor(5, 60);
        myOLED.print("P1: " + (String)allData.firstBME_press);
        
        it = 2;
        
        break;
                
      case 2:
      
        myOLED.setCursor(5, 20);
        myOLED.print("T2: " + (String)allData.secondBME_temp + "C");
        myOLED.setCursor(5, 40);
        myOLED.print("H2: " + (String)allData.secondBME_humid + "%");
        myOLED.setCursor(5, 60);
        myOLED.print("P2: " + (String)allData.secondBME_press);

        it = 3;
        
        break;
        
      case 3:
       
        myOLED.setCursor(5, 20);
        myOLED.print("T3: " + (String)allData.thirdBME_temp + "C");
        myOLED.setCursor(5, 40);
        myOLED.print("H3: " + (String)allData.thirdBME_humid + "%");
        myOLED.setCursor(5, 60);
        myOLED.print("P3: " + (String)allData.thirdBME_press);

        it = 1;
        
        break;
    }
  }  
}

void SetAdress(uint8_t enum_adress)
{
  Wire.beginTransmission(0x70); 
  Wire.write(1 << enum_adress);
  Wire.endTransmission();
}

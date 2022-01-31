#include <ESP8266WiFi.h>
#include <WiFiClientSecure.h>
//#include <ESP8266TelegramBOT.h>
#include <UniversalTelegramBot.h>
#include <Adafruit_BME280.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <SPI.h>
#include <iarduino_OLED.h>
#include <DallasTemperature.h>
#include <OneWire.h>
#include <GyverPID.h>

#define BOTtoken "1724680776:AAGoLnLlVBtwXoXl_5fAXiWX8a3VJ7o-Cz4"                   //Токен бота полученного от @BotFather
#define BOTname "DehydratorBot"                                                     // Имя бота
#define BOTusername "dehydrator_bot"                                                // Логин бота
#define PERIOD_BOT 10000                                                            // период опроса телеграм-бота
#define PERIOD_BOT_SEND 30000                                                       // период вывода данных в телеграм-бот

#define FIRST_BME 0                                   //Первый датчик ВМЕ280       //Константы для выбора нужного датчика с помощью мультиплексора
#define SECOND_BME 1                                  //Второй датчик ВМЕ280
#define THIRD_BME 2                                   //Третий датчик ВМЕ280
#define SEALEVELPRESSURE_HPA (1013.25)                //Какая-то константа давления для работы ВМЕ280

#define RELAY_PIN 15                                  // выход для подключения реле нагревателя нагревателя
#define PIN_FAN  13                                   // выход для подключения реле включения вентилятора

#define HEAT_INTERVAL 1000                            // цикл работы реле нагрева, 1 секунда, измеряется в мс,            
#define PERIOD_SENSORS_DISPLAY 10000                  // период обновления данных на дисплее, 1 секунда, в мс
#define PERIOD_SENSORS 60000                          // период считывания данных с датчиков, 1 секунда, в мс   
#define PERIOD_DISPLAY 5000                           // период обновления времени на дисплее, 1 секунда, в мс   
#define PERIOD_PID 1000                               // период работы ПИД регулятора

#define DS_PIN 2                                      // вход датчика DS18B20

#define MAX_POWER 210                                 // максимальная мощность нагревателя
/////////////////////////////////////////////////////////////////////Создание объектов для работы с переферией/////////////////////////////////////////////////////////////////////////////////
WiFiClientSecure secured_client;
UniversalTelegramBot bot(BOTtoken, secured_client);

iarduino_OLED myOLED(0x3C);
extern uint8_t MediumFont[];  

OneWire oneWire(DS_PIN);
DallasTemperature sensor_DS18B20(&oneWire);
DeviceAddress insideThermometer;

Adafruit_BME280 bme1;
Adafruit_BME280 bme2;
Adafruit_BME280 bme3;

GyverPID regulator(200, 10, 0, 1000);
/////////////////////////////////////////////////////////////////////Создание ппеременных для работы программы/////////////////////////////////////////////////////////////////////////////////
bool flag1 = false;                                //Переменные для выполения циклов\итераций\условий и т.п.   //для вывода на экран
bool Relay_on = false;
bool button_on = false;                            // флаг нажатия кнопки начала нагрева
bool regulator_run = false;                        // флаг включения регулятора
bool regulator_stop = false;

int it = 1;                                           //итерация для выбора данных нужного датчика ВМЕ280
int i = 0;                                            //итерация для чего хочеца (но одного)

float Temp_meas = 0;                                  //температура воздуха после нагревателя DS18B20
float Temp_task = 60;                                 //заданная температура для ПИД
float Power = 0;                                      // мощность, потребленная в процессе сушки
float water_col_1 = 0;                                // количество воды, уносимой воздухом при сушке
float water_col_2 = 0; 

unsigned long period_min_drying = 86400000;               // время минимальной сушки перед возможным повышением температуры
unsigned long time_sensors = 0;                       // время последнего считывания данных с датчиков, в мс 
unsigned long time_display = 0;                       // время последнего обновления времени на дисплее, в мс 
unsigned long time_sensors_display = 0;               // время последнего обновдения данных на дисплее, в мс 
unsigned long Heat_last = 0;                          // последнее время включения нагрева, измеряется в мс
unsigned long time_PID = 0;                           // последнее время вызова ПИД
unsigned long time_min_drying = 0;                    // время минимальной сушки до возможного повышения температуры
unsigned long Relay_last = 0;                         // время последнего включения реле, измеряется в мс
unsigned long time_BOT = 0;                           // последнее время работы с телеграм-ботом
unsigned long time_BOT_SEND = 0;                      // последнее время пересылки данных телеграм-ботом

String arr_commands[]={"/start","/help","/run","/stop","/monitor","/set_temp"}; // массив допустимых команд от телеграм - бота
int arr_commands_length = 6;                                                    // длина массива команд

String currentData;                                                             //Строка с данными работы дегидратора
String users_id;

int Relay_run = 400;                                  // длительность работы реле, измеряется в мс. 40 мс - стартовое значение

//const char* ssid = "RedmiNote5";
//const char* password = "11111111"; 
const char* ssid = "5G_DONSTU_M";
const char* password = "{@univer2019donstu}";

struct SensorsData
{
    float firstBME_temp = 0;
    float secondBME_temp = 0;
    float thirdBME_temp = 0;

    float firstBME_press = 0;
    float secondBME_press = 0;
    float thirdBME_press = 0;

    float firstBME_humid = 0;
    float secondBME_humid = 0;
    float thirdBME_humid = 0;
};

SensorsData allData;

void SetAdress(uint8_t enum_adress);
void Bot_EchoMessages(); 
float calc_wap_press(float T_air);                          
float calc_water(float T_hot, float H_hot, float T_cold, float H_cold);

void setup()
{
    Serial.begin(115200);

    Serial.println("START\n");

    pinMode(PIN_FAN, OUTPUT);                                                                // устанавливаем пин в режим вывода
    pinMode(RELAY_PIN, OUTPUT);
    pinMode(DS_PIN, INPUT);                                                                  // устанавливаем пин в режим ввода

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

    regulator.setDirection(NORMAL);                                                          // направление регулирования (NORMAL/REVERSE). ПО УМОЛЧАНИЮ СТОИТ NORMAL
    regulator.setLimits(0, 1000);                                                            // пределы (ставим для 8 битного ШИМ). ПО УМОЛЧАНИЮ СТОЯТ 0 И 255
    regulator.setpoint = Temp_task;                                                          // сообщаем регулятору температуру, которую он должен поддерживать

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        Serial.print(".");
        delay(500);
    }

    //digitalWrite(PIN_FAN,HIGH);                                                              //включаем вентилятор

    secured_client.setInsecure();
}


void loop() 
{  
    if ((millis() - time_BOT) > PERIOD_BOT)                                      // Проверяем наличие команд в боте от пользователя
    {
        time_BOT = millis();

        bot.getUpdates(bot.message[0][1]);                                       // Включаем API и получаем новые сообщения

        Bot_EchoMessages();

    }
    
    if (regulator_run)
    {         
        digitalWrite(PIN_FAN, HIGH);
        
        if ((millis() - time_PID) > PERIOD_PID)
        {                                                                                        // обновляем время последнего опроса датчиков раз в сек
            time_PID = millis();

            sensor_DS18B20.requestTemperatures();                                                  // запускаем измерение температуры DS18B20
            Temp_meas = sensor_DS18B20.getTempCByIndex(0);

            regulator.input = Temp_meas;                                                           //передача новой температуры в регулятор
            Relay_run = regulator.getResultTimer();

            if (Relay_run == 0)
            {
                button_on = false;
            }
            else
            {
                button_on = true;
            }
        }

        if ((millis() - time_sensors) > PERIOD_SENSORS)
        {
            time_sensors = millis();

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

            Serial.print("Показания и влагопотери №" + (String)(i + 1) + "\t");
            Serial.print(" Td= " + (String)Temp_meas);
            Serial.print("\tT1= " + (String)allData.firstBME_temp);
            Serial.print("\tH1= " + (String)allData.firstBME_humid);
            Serial.print("\tP1= " + (String)allData.firstBME_press);
            Serial.print("\tT2= " + (String)allData.secondBME_temp);
            Serial.print("\tH2= " + (String)allData.secondBME_humid);
            Serial.print("\tP2= " + (String)allData.secondBME_press);
            Serial.print("\tT3= " + (String)allData.thirdBME_temp);
            Serial.print("\tH3= " + (String)allData.thirdBME_humid);
            Serial.print("\tP3= " + (String)allData.thirdBME_press);

            water_col_1 = calc_water(allData.firstBME_temp, allData.firstBME_humid, allData.firstBME_press, allData.secondBME_temp, allData.secondBME_humid, allData.secondBME_press);
            Serial.print("\tW1-2= " + (String)water_col_1);

            water_col_2 = calc_water(allData.thirdBME_temp, allData.thirdBME_humid, allData.thirdBME_press, allData.secondBME_temp, allData.secondBME_humid, allData.secondBME_press);
            Serial.print("\tW3-2= " + (String)water_col_2);

            Serial.print("\tPower= " + (String)Power);
            Serial.print("\trel= " + (String)Relay_run + "\n");

            i++;

            //currentData = "Measurement " + (String)(i + 1) + " T1:" + (String)allData.firstBME_temp + " H1:" + (String)allData.firstBME_humid + " P1: " + (String)allData.firstBME_press  + " T2:" + (String)allData.secondBME_temp + " H2:" + (String)allData.secondBME_humid + " P2:" + (String)allData.secondBME_press  + " T3:" + (String)allData.thirdBME_temp + " H3:" + (String)allData.thirdBME_humid + " P3:" + (String)allData.thirdBME_press  + " W1-2=" + (String)water_col_1 + " W3-2=" + (String)water_col_2 + " Power=" + (String)Power + " rel=" + (String)Relay_run + "\0";
            
            //Serial.print(currentData);
 
            //bot.sendMessage("705803812", (String)(millis()/1000) + " " + (String)Temp_meas + " " + (String)allData.firstBME_temp + " " + (String)allData.firstBME_humid + " " + (String)allData.firstBME_press + " " + (String)allData.secondBME_temp + " " + (String)allData.secondBME_humid + " " + (String)allData.secondBME_press + " " + (String)allData.thirdBME_temp + " " + (String)allData.thirdBME_humid + " " + (String)allData.thirdBME_press + " " + (String)water_col_1 + " " + (String)water_col_2 + " " + (String)Power + " " + (String)Relay_run , "");
            bot.sendMessage(users_id, (String)(millis()/1000) + " " + (String)Temp_meas + " " + (String)allData.firstBME_temp + " " + (String)allData.firstBME_humid + " " + (String)allData.firstBME_press + " " + (String)allData.secondBME_temp + " " + (String)allData.secondBME_humid + " " + (String)allData.secondBME_press + " " + (String)allData.thirdBME_temp + " " + (String)allData.thirdBME_humid + " " + (String)allData.thirdBME_press + " " + (String)water_col_1 + " " + (String)water_col_2 + " " + (String)Power + " " + (String)Relay_run , "");

            flag1 = true;
        }

        ///if ((millis() - time_BOT_SEND) > PERIOD_BOT_SEND)                             // Отправляем все данные о работе в телеграмм
        //{
        //   time_BOT_SEND = millis();

        //    bot.sendMessage("705803812", currentData, "");
        // }

        if ((millis() - time_sensors_display) > PERIOD_SENSORS_DISPLAY && flag1)
        {
            time_sensors_display = millis();

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

                it = 4;

                break;

             case 4:
                myOLED.setCursor(5, 20);
                myOLED.print("W1-2: " + (String)water_col_1);
                myOLED.setCursor(5, 40);
                myOLED.print("W3-2: " + (String)water_col_2);
                myOLED.setCursor(5, 60);
                myOLED.print("Rel: " + (String)Relay_run);

                it = 1;

                break;    
            }
        }

        if (millis() < period_min_drying)
        {                                                                                                             
            regulator.setpoint = Temp_task;                                                       // сообщаем регулятору температуру, которую он должен поддерживать
        }
        else
        {
            regulator_stop = 1;
            regulator_run = 0;
            
            digitalWrite(PIN_FAN, LOW);
            digitalWrite(RELAY_PIN, LOW);
        }

        if (button_on == true)
        {                                                                                       //запуск нагрева          
            if (((millis() - Heat_last) > HEAT_INTERVAL) && button_on)
            {                                                                                     // пришло время начать греть // включение реле каждые HEAT_INTERVAL секунд 
                Heat_last = millis();                                                             // запоминаем время включения
                digitalWrite(RELAY_PIN, HIGH);                                                    // включаем реле
                Relay_on = true;                                                                  // устанавливаем флаг "реле включено" 
            }
            // выключение реле через время Relay_run
            if (((millis() - Heat_last) > Relay_run) && Relay_on)                                    // пришло время выключить реле
            {
                digitalWrite(RELAY_PIN, LOW);                                                     // выключаем реле
                Relay_on = false;                                                                 // сбрасываем флаг "реле включено" 
                Power = Power + (float)((float)Relay_run * (float)MAX_POWER) / (float)HEAT_INTERVAL;  // добавляем потраченную энергию (в Ваттах в секунду)
            }
        }
        else
        {
            Relay_on = false;
            digitalWrite(RELAY_PIN, LOW);                                                         // выключаем реле
        }
    }
    
    if (regulator_stop)
    {
        digitalWrite(PIN_FAN, LOW);
        digitalWrite(RELAY_PIN, LOW);
    }    
}

float calc_wap_press(float T_air)
{
    return (float)6.1121 * exp((double)(18.678 - T_air / 234.5) * (T_air / (257.14 + T_air)));
}

float calc_water(float T_hot, float H_hot, float P_hot, float T_cold, float H_cold, float P_cold)
{
    float Psi = calc_wap_press(T_cold);                                                     //расчет давления насыщеного пара холодного воздуха
    float Pso = calc_wap_press(T_hot);                                                      //расчет давления насыщеного пара горячего воздуха

    float d_i = 622 * H_cold / 100 * Psi / (P_cold / 100 - H_cold / 100 * Psi);                                 //расчет влагосодержания холодного воздуха с учетом что влажность - в %
    float d_o = 622 * H_hot / 100 * Pso / (P_hot / 100 - H_hot / 100 * Pso);                                    //расчет влагосодержания горячего воздуха с учетом что влажность - в %

    return d_o - d_i;                                                                       // расчет уносимой влаги в граммах на килограмм воздуха
}

void SetAdress(uint8_t enum_adress)
{
    Wire.beginTransmission(0x70);
    Wire.write(1 << enum_adress);
    Wire.endTransmission();
}

void Bot_EchoMessages()
{
    int first_space = -1;   // место первого пробела

    String bot_command_body;
    String first_param = "";
    String second_param = "";
    
    for (int i = 0; i < numNewMessages; i++) 
    { 
      String bot_command = bot.messages[i].text; 
      Serial.println(bot_command);
      String bot_chat_id = bot.messages[i].chat_id; 
      if (bot_command.startsWith("/"))
      {
          int first_space = bot_command.indexOf(" "); // находим первый побел
          if (first_space != -1)
          {
              bot_command_body = bot_command;

              first_param = bot_command.substring(first_space+1, bot_command.length());
              bot_command_body = bot_command.substring(0,first_space); // копируем тело команды 
          }
          else
          {
              bot_command_body = bot_command;
          }  

          int command_num = -1;
        
          for (int K = 0; K < arr_commands_length; K++)                                  // определяем номер команды в массиве для оператора switch  
          {
              if (bot_command_body == arr_commands[K])
              {
                  command_num = K;
                  break;
              }
          }

          switch (command_num)
          {
          case 0: // /start
            //bot.sendMessage(bot_chat_id, bot_command_body, "");
              bot.sendMessage(bot_chat_id, "Дегидратор готов к работе!", "");
                
              command_num = -1;
              break;

          case 1: // /help","/run","/stop","/monitor","/set_temp","/set_time
            //bot.sendMessage(bot_chat_id, bot_command_body, "");
              bot.sendMessage(bot_chat_id, "Доступные команды: ", "");
              bot.sendMessage(bot_chat_id, "/start", "");
              bot.sendMessage(bot_chat_id, "/help", "");
              bot.sendMessage(bot_chat_id, "/run", "");
              bot.sendMessage(bot_chat_id, "/stop", "");
              bot.sendMessage(bot_chat_id, "/monitor", "");
              bot.sendMessage(bot_chat_id, "/set_temp", "");
                
              command_num = -1;
              break;

          case 2: // /run
            //bot.sendMessage(bot_chat_id, bot_command_body, "");
              regulator_run = true;
              regulator_stop = false;

              if (first_param != "")
              {
                  period_min_drying = first_param.toInt() * 3600 * 1000;
              }
                
              bot.sendMessage(bot_chat_id, "Запускаем дегидратор", "");
              bot.sendMessage(bot_chat_id, "Установленная температура: " + (String)Temp_task, "");
              break;

          case 3:  // /stop
            //bot.sendMessage(bot_chat_id, bot_command_body, "");
              regulator_stop = true;
              regulator_run = false;
                
              bot.sendMessage(bot_chat_id, "Выключаем дегидратор", "");
              //myOLED.clear();
                
              command_num = -1;
              break;

          case 4:  // /monitor
            //bot.sendMessage(bot_chat_id, bot_command_body, "");
              bot.sendMessage(bot_chat_id, "Установленная температура: " + (String)Temp_task, "");
              bot.sendMessage(bot_chat_id, "Текущая температура: " + (String)Temp_meas, "");
              bot.sendMessage(bot_chat_id, "Значение регулятора: " + (String)Relay_run, "");
              bot.sendMessage(bot_chat_id, "Установленное время сушки: " + (String)(period_min_drying/3600/1000) + " ч.", "");
              bot.sendMessage(bot_chat_id, "Прошло: " + (String)(millis()/3600/1000) + " ч.", "");
              
              command_num = -1;
              break;

          case 5:  // /set_temp
            //bot.sendMessage(bot_chat_id, bot_command_body, "");
              Temp_task = first_param.toInt();
              
              //Serial.println(Temp_task);
                
              bot.sendMessage(bot_chat_id, "Установленная температура изменена на: " + (String)Temp_task, "");

              command_num = -1;
              break;
          }
       }
    }
 }

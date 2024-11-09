# monitoramento-sonoro










codigo do ESP

#include <WiFi.h>
#include <HTTPClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

const char* ssid = "SEU_SSID";
const char* password = "SUA_SENHA";

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", -10800, 60000);

const int micPin = 34;

int valorADC;
float tensao;
float nivelRMS;
float decibeis;

const float limiteDia = 55.0;
const float limiteNoite = 50.0;

String getData() {
  unsigned long epochTime = timeClient.getEpochTime();
  epochTime += 10800;

  int year = 1970;
  while (epochTime >= 31536000) {
    if ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)) {
      if (epochTime >= 31622400) {
        epochTime -= 31622400;
        year++;
      }
    } else {
      epochTime -= 31536000;
      year++;
    }
  }

  int month = 0;
  const int daysInMonth[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  int monthLength;

  for (month = 0; month < 12; month++) {
    monthLength = daysInMonth[month] * 86400;
    if (month == 1 && ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0))) {
      monthLength += 86400;
    }
    if (epochTime < monthLength) break;
    epochTime -= monthLength;
  }

  int day = epochTime / 86400 + 1;

  return String(day) + "/" + String(month + 1) + "/" + String(year);
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  pinMode(micPin, INPUT);

  WiFi.begin(ssid, password);
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConectado ao Wi-Fi!");

  timeClient.begin();
}

void loop() {
  timeClient.update();

  String horaAtual = timeClient.getFormattedTime();
  String dataAtual = getData();

  valorADC = analogRead(micPin);
  tensao = (valorADC / 4095.0) * 3.3;
  nivelRMS = sqrt(tensao * tensao);
  decibeis = 20 * log10(nivelRMS / 0.00631);

  int horas = timeClient.getHours();
  float limiteAtual = (horas >= 7 && horas < 22) ? limiteDia : limiteNoite;
  String status = (decibeis > limiteAtual) ? "Acima do limite" : "Dentro do limite";

  StaticJsonDocument<200> jsonDoc;
  jsonDoc["data"] = dataAtual;
  jsonDoc["hora"] = horaAtual;
  jsonDoc["decibeis"] = decibeis;
  jsonDoc["limite"] = limiteAtual;
  jsonDoc["status"] = status;

  String jsonData;
  serializeJson(jsonDoc, jsonData);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin("COLOCAR O IP DA MAQUINA:8000/userInterface/api/niveis_de_ruido/");
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonData);

    if (httpResponseCode > 0) {
      String resposta = http.getString();
      Serial.println("Resposta do servidor: " + resposta);
    } else {
      Serial.println("Erro ao enviar os dados: " + String(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("Erro: Wi-Fi desconectado");
  }

  Serial.print("Data: ");
  Serial.print(dataAtual);
  Serial.print(", Hora: ");
  Serial.print(horaAtual);
  Serial.print(", Nível: ");
  Serial.print(decibeis, 1);
  Serial.print(" dB, Limite: ");
  Serial.print(limiteAtual, 1);
  Serial.println(" dB");

  delay(60000);
}




##### ou esse 



#include <WiFi.h>
#include <HTTPClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include <WiFiManager.h>  // Biblioteca WiFiManager

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", -10800, 60000);

const int micPin = 34;

int valorADC;
float tensao;
float nivelRMS;
float decibeis;

const float limiteDia = 55.0;
const float limiteNoite = 50.0;

// Função para obter a data a partir do timestamp NTP
String getData() {
  unsigned long epochTime = timeClient.getEpochTime();
  epochTime += 10800;  // Ajuste de fuso horário (GMT-3)

  int year = 1970;
  while (epochTime >= 31536000) {
    if ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)) {
      if (epochTime >= 31622400) {
        epochTime -= 31622400;
        year++;
      }
    } else {
      epochTime -= 31536000;
      year++;
    }
  }

  int month = 0;
  const int daysInMonth[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  int monthLength;

  for (month = 0; month < 12; month++) {
    monthLength = daysInMonth[month] * 86400;  // Número de dias do mês em segundos
    if (month == 1 && ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0))) {
      monthLength += 86400;  // Ajuste para fevereiro em ano bissexto
    }
    if (epochTime < monthLength) break;
    epochTime -= monthLength;
  }

  int day = epochTime / 86400 + 1;

  return String(day) + "/" + String(month + 1) + "/" + String(year);
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  pinMode(micPin, INPUT);

  // Iniciar o WiFiManager
  WiFiManager wifiManager;

  // Tenta conectar ao Wi-Fi. Se não conseguir, cria um ponto de acesso
  if (!wifiManager.autoConnect("ESP32_AP")) {
    Serial.println("Falha ao conectar ao Wi-Fi.");
    ESP.restart();  // Reinicia o ESP32 se não conseguir conectar
  }

  Serial.println("Conectado ao Wi-Fi!");

  // Iniciar o cliente NTP
  timeClient.begin();
}

void loop() {
  timeClient.update();

  String horaAtual = timeClient.getFormattedTime();
  String dataAtual = getData();

  valorADC = analogRead(micPin);
  tensao = (valorADC / 4095.0) * 3.3;
  nivelRMS = sqrt(tensao * tensao);
  decibeis = 20 * log10(nivelRMS / 0.00631);

  int horas = timeClient.getHours();
  float limiteAtual = (horas >= 7 && horas < 22) ? limiteDia : limiteNoite;
  String status = (decibeis > limiteAtual) ? "Acima do limite" : "Dentro do limite";

  // Criar um objeto JSON para enviar os dados
  StaticJsonDocument<200> jsonDoc;
  jsonDoc["data"] = dataAtual;
  jsonDoc["hora"] = horaAtual;
  jsonDoc["decibeis"] = decibeis;
  jsonDoc["limite"] = limiteAtual;
  jsonDoc["status"] = status;

  String jsonData;
  serializeJson(jsonDoc, jsonData);

  // Enviar os dados via HTTP para o servidor Django
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin("http://IP DA MAQUINA:8000/userInterface/api/niveis_de_ruido/");  // Substitua o IP da máquina
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonData);

    if (httpResponseCode > 0) {
      String resposta = http.getString();
      Serial.println("Resposta do servidor: " + resposta);
    } else {
      Serial.println("Erro ao enviar os dados: " + String(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("Erro: Wi-Fi desconectado");
  }

  // Exibir os valores no monitor serial
  Serial.print("Data: ");
  Serial.print(dataAtual);
  Serial.print(", Hora: ");
  Serial.print(horaAtual);
  Serial.print(", Nível: ");
  Serial.print(decibeis, 1);
  Serial.print(" dB, Limite: ");
  Serial.print(limiteAtual, 1);
  Serial.println(" dB");

  delay(60000);  // Enviar os dados a cada 60 segundos
}

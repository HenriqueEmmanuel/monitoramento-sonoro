#include <WiFi.h>
#include <HTTPClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>
#include <time.h>  

const char* ssid = "nome";
const char* password = "senha";
const char* server_url = "http://ipdamaquina:8000/userInterface/api/niveis_de_ruido/";


WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", -10800, 60000);

const int micPin = 34;

int valorADC;
float tensao;
float nivelRMS;
float decibeis;

const float limiteDia = 55.0;
const float limiteNoite = 50.0;

String formatData(int day, int month, int year) {
  // Retorna a data no formato YYYY-MM-DD
  return String(year) + "-" + (month < 10 ? "0" : "") + String(month) + "-" + (day < 10 ? "0" : "") + String(day);
}

String formatHora(int hora, int minuto, int segundo) {
  // Retorna a hora no formato HH:MM:SS
  return (hora < 10 ? "0" : "") + String(hora) + ":" + (minuto < 10 ? "0" : "") + String(minuto) + ":" + (segundo < 10 ? "0" : "") + String(segundo);
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

  // Obter o tempo em segundos desde a época Unix (1970)
  unsigned long epochTime = timeClient.getEpochTime();

  // Converter o tempo Unix para a estrutura tm
  struct tm timeInfo;
  
  time_t rawTime = (time_t)epochTime;  // Cast para time_t

  // Agora podemos usar gmtime() ou localtime() sem erros
  gmtime_r(&rawTime, &timeInfo);  // Converte para UTC (Tempo Universal Coordenado)

  // Formatar a hora e a data
  String horaAtual = formatHora(timeInfo.tm_hour, timeInfo.tm_min, timeInfo.tm_sec);
  String dataAtual = formatData(timeInfo.tm_mday, timeInfo.tm_mon + 1, timeInfo.tm_year + 1900); // Ajuste para o formato de data (tm_mon começa em 0 e tm_year conta a partir de 1900)

  valorADC = analogRead(micPin);
  tensao = (valorADC / 4095.0) * 3.3;
  nivelRMS = sqrt(tensao * tensao);
  decibeis = 20 * log10(nivelRMS / 0.00631);

  int hora = timeInfo.tm_hour;
  float limiteAtual = (hora >= 7 && hora < 22) ? limiteDia : limiteNoite;
  bool status = (decibeis > limiteAtual);  // status será true (acima do limite) ou false (dentro do limite)

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
    http.begin("http://ipdamaquina:8000/userInterface/api/niveis_de_ruido/");
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonData);

    if (httpResponseCode > 0) {
      String resposta = http.getString();
      Serial.println("Resposta do servidor: " + resposta);
    } else {
      Serial.println("Erro ao enviar os dados: " + String(httpResponseCode));
    }

    http.end();  // Remover 'y' extra
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

  delay(30000);  
}

# monitoramento-sonoro










codigo do ESP

#include <WiFi.h>
#include <HTTPClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <ArduinoJson.h>

// Configurações da rede Wi-Fi
const char* ssid = "SEU_SSID";
const char* password = "SUA_SENHA";



// Configurações do cliente NTP
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", -10800, 60000); // GMT-3 (Brasília)

// Pino do ESP32 onde o microfone está conectado
const int micPin = 34;

// Variáveis para leitura dos valores
int valorADC;
float tensao;
float nivelRMS;
float decibeis;

// Limites de decibéis por horário
const float limiteDia = 55.0;   // Limite diurno (7h às 22h)
const float limiteNoite = 50.0; // Limite noturno (22h às 7h)

// Função para obter a data a partir do timestamp NTP
String getData() {
  unsigned long epochTime = timeClient.getEpochTime();
  
  // Ajuste de fuso horário (GMT-3)
  epochTime += 10800; // 3 horas para ajustar ao horário de Brasília sem horário de verão

  // Cálculo do dia, mês e ano
  int year = 1970;
  while (epochTime >= 31536000) { // Ano tem 31.536.000 segundos (sem considerar bissextos)
    if ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)) {
      if (epochTime >= 31622400) { // Ano bissexto tem 31.622.400 segundos
        epochTime -= 31622400;
        year++;
      }
    } else {
      epochTime -= 31536000;
      year++;
    }
  }

  // Meses do ano em segundos
  int month = 0;
  const int daysInMonth[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  int monthLength;

  for (month = 0; month < 12; month++) {
    monthLength = daysInMonth[month] * 86400; // Número de dias do mês em segundos
    if (month == 1 && ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0))) {
      monthLength += 86400; // Ajuste para fevereiro em ano bissexto
    }
    if (epochTime < monthLength) break;
    epochTime -= monthLength;
  }

  // Ajustar dia do mês
  int day = epochTime / 86400 + 1;

  return String(day) + "/" + String(month + 1) + "/" + String(year);
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  pinMode(micPin, INPUT);

  // Conectar ao Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nConectado ao Wi-Fi!");

  // Iniciar o cliente NTP
  timeClient.begin();
}

void loop() {
  // Atualizar a hora
  timeClient.update();

  // Obter a hora e data atuais
  String horaAtual = timeClient.getFormattedTime();
  String dataAtual = getData();

  // Ler o valor do ADC e calcular os decibéis
  valorADC = analogRead(micPin);
  tensao = (valorADC / 4095.0) * 3.3;
  nivelRMS = sqrt(tensao * tensao);
  decibeis = 20 * log10(nivelRMS / 0.00631); // Ajuste o valor de referência conforme necessário

  // Verificar o limite com base no horário
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

  // Enviar os dados ao servidor
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
   // http.begin(serverUrl);
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

  delay(60000); // Enviar os dados a cada 60 segundos
}
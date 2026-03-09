#include "secrets.h"

#define BLYNK_PRINT Serial
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

String app1 = "None", app2 = "None", app3 = "None";
int avgTime = 0;
bool needsRefresh = true;

void drawDashboard() {
  Serial.println("Updating OLED Screen...");
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);

  display.setCursor(0, 0);
  display.print("AVG: "); display.print(avgTime); display.println(" min");
  display.drawFastHLine(0, 10, 128, SSD1306_WHITE);

  display.setCursor(0, 20); display.print("1. "); display.println(app1);
  display.setCursor(0, 35); display.print("2. "); display.println(app2);
  display.setCursor(0, 50); display.print("3. "); display.println(app3);

  display.display(); 
}

void setup() {
  Serial.begin(115200);
  Wire.begin(2, 14); 

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("OLED NOT FOUND");
  }

  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
}

void loop() {
  Blynk.run();

  static unsigned long lastSync = 0;
  if (millis() - lastSync > 10000) {
    Blynk.syncVirtual(V10, V11, V12, V13);
    lastSync = millis();
  }

  if (needsRefresh) {
    drawDashboard();
    needsRefresh = false;
  }
}

BLYNK_WRITE(V10) { avgTime = param.asInt(); needsRefresh = true; }
BLYNK_WRITE(V11) { app1 = param.asStr(); needsRefresh = true; }
BLYNK_WRITE(V12) { app2 = param.asStr(); needsRefresh = true; }
BLYNK_WRITE(V13) { app3 = param.asStr(); needsRefresh = true; }
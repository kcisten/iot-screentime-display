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

String myApps[3] = {"---", "---", "---"};
int screenTime = 0;
bool needsRefresh = true;
const int LIMIT = 20; 

// for face animation
bool frame = false;
unsigned long lastTick = 0;

void updateScreen() {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(2); 
  display.setCursor(6, 22);
  
  if (screenTime >= LIMIT) {
    if (frame) display.print("T_T"); 
    else       display.print("u_u");
  } else {
    if (frame) display.print("^-^");
    else       display.print("^u^");
  }

  // right side: stats
  display.setTextSize(1);
  display.setCursor(65, 2);
  display.print(screenTime); display.print(" mins");
  display.drawFastHLine(65, 12, 58, SSD1306_WHITE);

  // apps
  for (int i = 0; i < 3; i++) {
    int y = 22 + (i * 14); 
    display.setCursor(65, y);
    display.print(myApps[i].substring(0, 8));
    
    // tiny progress bars
    int w = 45 - (i * 12); 
    display.drawFastHLine(65, y + 9, w, SSD1306_WHITE);
  }

  // separator line
  display.drawFastVLine(60, 0, 64, SSD1306_WHITE);
  display.display(); 
}

void setup() {
  Serial.begin(115200);
  Wire.begin(2, 14); 
  
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    while(1); 
  }
  
  display.clearDisplay();
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
}

void loop() {
  Blynk.run();

  // change the animation frame every 700ms
  if (millis() - lastTick > 700) {
    frame = !frame;
    lastTick = millis();
    needsRefresh = true;
  }

  if (needsRefresh) {
    updateScreen();
    needsRefresh = false;
  }
}

BLYNK_WRITE(V10) { screenTime = param.asInt(); needsRefresh = true; }
BLYNK_WRITE(V11) { myApps[0] = param.asStr(); needsRefresh = true; }
BLYNK_WRITE(V12) { myApps[1] = param.asStr(); needsRefresh = true; }
BLYNK_WRITE(V13) {
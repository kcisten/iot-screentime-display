# IoT Screen Time Monitor
## Project Overview

The purpose of this IoT device is to encourage digital well-being by providing a physical, real-time display of one’s daily screen time. By querying [ActivityWatch’s](https://activitywatch.net/) logs into a visual summary that can be viewed from one’s desk, the system helps bring awareness to the user’s overall screen time habits. Additionally, the application can send customized reminder messages to the user’s preferred Discord server to encourage them to take a break and log off of their computer.



---

## Hardware Components
The device utilizes the following components:

* **Microcontroller:** SparkFun ESP8266.
* **OLED Display:** SSD1306 OLED Display (128x64).
* **Wiring:** Breadboard, 2 alligator clips, 2 male-to-male jumper cables, and 2 female-to-female jumper cables.

### Software Libraries
* **ESP8266:** `ESP8266WiFi`, `BlynkSimpleEsp8266`.
* **Display:** `Adafruit_SSD1306`, `Adafruit_GFX`.

## Additional Components
* **ActivityWatch:** Used to monitor and log your screen time activity locally.
* **Blynk Cloud:** Acts as the bridge to send data from the Python script to your ESP8266 board.
* **Discord:** Used to send automated screentime reminder messages.



---

## Running the System

### 1. Prerequisites
* Ensure **ActivityWatch** is installed and running on your local machine.
* **Blynk Setup:**
    * Create a project in the [Blynk Console](https://blynk.cloud/).
    * Create a Template and assign **Virtual Pins V11, V12, and V13** to data type `String` (for app names).
    * Set **Virtual Pin V10** to data type `Integer` (to store screen time minutes).

### 2. Configure Credentials
* **Python Secrets:** Create a `.env` file in the root directory for your API tokens.
* **Arduino Secrets:** Create a `secrets.h` file in the `esp8266_firmware/` folder to add your Wi-Fi credentials and Blynk auth tokens.


### 3. Upload Hardware Firmware
1. Open `screentime-display.ino` in the Arduino IDE.
2. Ensure the **ESP8266 Board package** is installed in your IDE (via Board Manager).
3. Install the `Adafruit SSD1306` and `Adafruit GFX` libraries via the Library Manager.
4. Connect your ESP8266 via USB and upload the sketch.


### 4. Running the Python Script
1. Navigate to the project root directory via your terminal.
2. Install the required dependencies:
   ```bash
   pip install -r python_script/requirements.txt

3. Run main.py
4. The OLED display should now populate with your ActivityWatch data! 


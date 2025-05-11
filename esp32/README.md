# ESP32 Software

Here you can find a description of the "esp32" side components.

## Configuration

In the file `esp32.ino`, before compiling and flashing the code. You must set the `WLAN_SSID` and `WLAN_PASS` fields with your WiFi network configuration.
The `MQTT_BROkER` field must also be set before use with the Raspberry Pi IP.

You MUST use the correct versions of the library described in `requirements.txt` before compiling the code and flashing the ESP32 in the Arduino IDE.

### Requirements

The requirements are described in the file `requirements.txt`


#### Serial debugging

The esp32 sends messages through serial for debugging.
The messages are visible from the Arduino IDE when the esp32 is connected by USB.
To see these messages, you must set the Baud rate on your serial monitor at 115200 Bauds

##### Internal Workings

For more informations about the internal workings, check server/README.md for more informations.

# Project IOT

[![en](https://img.shields.io/badge/lang-en-red.svg)](./README.en.md)
[![fr](https://img.shields.io/badge/lang-fr-yellow.svg)](./README.md)

Here is [a programming project](https://github.com/GreengagePlum/Project-IOT) in **Arduino C** and **Python** that aims to create and monitor an network of IOT sensors. The subject paper for the project is [available here](./IOC_mode_projet%20–%20SESI.pdf) for more details.

This project uses:

* the [Flask](https://flask.palletsprojects.com/en/stable/) framework on the web server side
* the [Eclipse Paho](https://github.com/eclipse-paho/paho.mqtt.python?tab=readme-ov-file) library for the MQTT communications inside the server side MQTT client.
* [Mosquitto](https://mosquitto.org/) as the MQTT broker
* [SQLite](https://sqlite.org/index.html) for the database
* [Arduino IDE](https://www.arduino.cc/en/software/) for development on the ESP32s
* the [ESP32 Espressif](https://github.com/espressif/arduino-esp32) and the [MQTT Adafruit](https://docs.arduino.cc/libraries/adafruit-mqtt-library/) libraries

## A preview

_Under construction..._

![The material that was used, a Raspberry Pi 3 and an ESP32 board](./images/material.jpg)

## Authors

This programming project was carried out for the IOC (IOT) class of the Computer Science Master's first year, second semester (M1S2 2024/25) at Sorbonne Université by the following two fellow gentlemen.

* Efe ERKEN 21400542
* Sylvain PRANDO 21414666

## Language versions

### C

The Arduino variant of C is used along with the Arduino IDE (**v2.3.4**) as the compiler. The ESP32 library used along with the Arduino IDE is `esp32` by Espressif (**v2.0.17**) as well as the MQTT library by Adafruit (**v2.5.9**).

As one of us is working on a Mac computer (macOS **Sequoia 15.3.2**), the additional drivers required and their versions are as follows:

* CP210xVCPDriver (**v6.0.2**)
* CH34xVCPDriver (**v1.9**)

### Python

Right below are the different versions of Python we used for the web server as well as for the server side MQTT client:

```text
Python 3.11.3
```

## Usage

### How to build and execute?

* For instructions concerning the "server" components, see [the server README](./server/README.md#usage).
* For instructions concerning the ESP32s, see [the ESP32 README](./esp32/README.md).

## License

This project is under the ["MIT" license](./LICENSE).

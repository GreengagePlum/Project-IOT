# Projet IOC

[![en](https://img.shields.io/badge/lang-en-red.svg)](./README.en.md)
[![fr](https://img.shields.io/badge/lang-fr-yellow.svg)](./README.md)

Voici [un projet de programmation](https://github.com/GreengagePlum/Project-IOT) en **C Arduino** et **Python** qui vise à créer et surveiller un réseau de capteurs IOT. Le sujet du projet est [disponible ici](./IOC_mode_projet%20–%20SESI.pdf) pour plus de détails.

Ce projet utilise :

* le framework [Flask](https://flask.palletsprojects.com/en/stable/) côté serveur web
* la bibliothèque [Eclipse Paho](https://github.com/eclipse-paho/paho.mqtt.python?tab=readme-ov-file) pour les communications MQTT dans le client MQTT côté serveur.
* [Mosquitto](https://mosquitto.org/) comme le broker MQTT
* [SQLite](https://sqlite.org/index.html) pour la base de données
* [Arduino IDE](https://www.arduino.cc/en/software/) pour le développement sur les ESP32s
* la bibliothèque [ESP32 Espressif](https://github.com/espressif/arduino-esp32) et la bibliothèque [MQTT Adafruit](https://docs.arduino.cc/libraries/adafruit-mqtt-library/)

## Un aperçu

_En construction..._

![Le matériel qui a été utilisé, une Raspberry Pi 3 et une carte ESP32](./images/material.jpg)

## Auteurs

Ce projet de programmation a été réalisé pour l'UE IOC du M1S2 2024/25 Informatique à Sorbonne Université par les deux messieurs suivants.

* Efe ERKEN 21400542
* Sylvain PRANDO 21414666

## Versions des langages

### C

La variante Arduino de C est utilisée avec l'IDE Arduino (**v2.3.4**) comme compilateur. La bibliothèque ESP32 utilisée avec l'IDE Arduino est `esp32` par Espressif (**v2.0.17**) ainsi que la bibliothèque MQTT par Adafruit (**v2.5.9**).

Comme l'un de nous travaille sur un ordinateur Mac (macOS **Sequoia 15.3.2**), les pilotes supplémentaires requis et leurs versions sont les suivants :

* CP210xVCPDriver (**v6.0.2**)
* CH34xVCPDriver (**v1.9**)

### Python

Voici les différentes versions de Python que nous avons utilisées pour le serveur web ainsi que le client MQTT côté
serveur :

```text
Python 3.11.3
```

## Utilisation

### Comment construire et exécuter ?

* Pour les instructions concernant les composants "serveur", regarder [le README serveur](./server/README.md#usage).
* Pour les instructions concernant les ESP32, regarder [le README ESP32](./esp32/README.md).

## Licence

Ce projet est sous la licence ["MIT"](./LICENSE).

# Server side programs

Here you can find a description of the "server" side components of the system including the web server, the MQTT client
for the web server and more.

## Usage

Use the given `Makefile` to launch each program. `make help` should display a list of things you can do. This includes
launching the web server, the MQTT broker and the MQTT server side client. You should make sure to have **Python 3.9+**
along with the dependencies in `requirements.txt` installed via `pip` (preferably in a virtual environment). External
dependencies also include the programs `sqlite3` and `mosquitto`.

## Python Flask web server

_Under construction..._

## MQTT

This part describes the MQTT communications used to make the whole system come together. **MQTT v5** is considered for
use in this project.

### Channels

Here is an overview of the MQTT channels used between the ESP32s and the web server to relay all the necessary
information. See the next section to get a detailed view of the message payloads and the overall protocol of use for the
channels.

* `led/command` (QoS 1)

This channel is used to relay on/off commands from the web server to the ESP32s to switch on or off their LED.

* `led/status` (QoS 1)

This channel is used to provide status updates on the LED status on the ESP32s. ESP32s publish on this channel when their LED changes status to on or off to inform the web server.

* `button/status` (QoS 0)

ESP32s publish the button push/release events on this channel to inform the web server.

* `photoresistor/status` (QoS 0)

ESP32s publish at regular intervals on this channel the readings from their photoresistor.

* `state/join` (QoS 2)

ESP32s use this channel to notify the web server that they joined the network as a newcomer. This is to be used right after connecting to the broker and before publishing anything else.

* `state/leave` (QoS 2)

ESP32s use this channel to notify the web server that they are leaving the network. This should be done right before disconnecting from the broker. ESP32s should set an [LWT message](https://www.hivemq.com/blog/mqtt-essentials-part-9-last-will-and-testament/) on this channel upon their initial connection to guard against unexpected disconnections.

* `state/nameAssign` (QoS 2)

This channel is used by the web server to give a human readable name to a newly joined ESP32. This name will figure in
every published message to identify the ESP32 that is communicating. This message is published right after a join
message is received by the web server.

### Payload formats

All messages are prefixed with the name that the web server has assigned to the ESP32 to determine who is who. See the
next section on the protocol to grasp in which order to use each channel and in what cases should they be used.

* `led/command`

`<name>:<1|0>`

The payload is in two parts, first the assigned name, then a colon as the separator, and then a value of `1` or `0`. `1` indicates a request to turn the LED **ON**. `0` indicates a request to turn the LED **OFF**. Mind you there are no spaces to keep the message minimal.

Example: `capteur01:1`

* `led/status`

`<name>:<1|0>`

Same as before. But this time it is the ESP32s that publish this message whenever the state of their LED is changed.
This is necessary since multiple web server clients could issue commands to the same ESP32 and all of their UI needs to
be updated according to the latest state even if another client issued a command.

Example: `capteur02:0`

* `button/status`

`<name>:<1|0>`

`1` indicates a button **PUSH** event, whereas a `0` indicates a button **RELEASE** event.

Example: `optimus:1`

* `photoresistor/status`

`<name>:<0-100>`

At regular intervals ESP32s publish the value read from their photoresistor as a percentage. Thus the value after the
name is between and including 0 and 100.

Example: `capteur01:58`

* `state/join`

`<ip>`

The initial identifier for an ESP32 is its IP address in the same Wi-Fi network its connected to with the Raspberry Pi.
This is to ensure uniqueness in the name assignment period.

Example: `192.168.1.18`

* `state/leave`

`<name>`

Just the assigned name of the ESP32 is enough in this case to consider it unreachable on the web server side.

Example: `capteur01`

* `state/nameAssign`

`<ip:name>` or `<name>:<name>`

A new name assignment or a name change for an existing name.

The web server may assign any string as a name. Most likely the default will be something like `capteurXX` where `XX` is an incrementing number depending on the number of previously connected ESP32s. But it could also simply be a number (`1`, `54`) or a custom name most likely assigned by a web server client (`LeBron`).

Once received, this name should be stored by the ESP32s and used to identify themselves when publishing messages or when
subscribed to channels to determine if a message concerns them. It could also be considered for persistance in case of a
power loss to be able to be used back again when the ESP32 goes online again. This could ensure that the same ESP32,
whether it lost connection and rejoined the network at a later time, updates its own records on the database operated on
the server side and not some other ESP32's data considering the server also has the necessary persistance measures in
place or is assumed to never go offline.

The server can also issue a name change for a given ESP32 (most likely issued by a web server client from their
browser).

Example: `192.168.1.18:capteur01` or `capteur01:LeBron`

### Protocol/exchanges

This is the order in which channels should be used to form an applicative protocol. Make sure to respect quality of
service (QoS) levels described in the [channels](#channels) section when publishing.

#### ESP32

1. ESP32 connects to the broker via the IP of the Raspberry PI on the network on port 1883 (the default).
1. Once the connection is established (CONNACK), if the ESP32 doesn't have a previously stored name that came from `state/nameAssign` (otherwise skip to the next step)
   1. ESP32 publishes on `state/join` to indicate its fresh arrival.
   1. ESP32 listens on `state/nameAssign` that it already subscribed to before emitting a join notification.
   1. ESP32 receives a name and stores it for future use.
1. ESP32 keeps listening on `state/nameAssign` in parallel in case any name change concerning it is issued by the web server.
1. Usual operation starts here (in no particular order)
   1. `led/command`: ESP32 subscribes to this channel to receive on/off commands
   1. `led/status`: ESP32 publishes on this channel whenever its LED changes state
   1. `button/status`: ESP32 publishes on this channel whenever its button changes state
   1. `photoresistor/status`: ESP32 publishes on this channel at regular intervals sending readings from its photoresistor
1. ESP32 publishes on `state/leave` if it wants to leave the network for any reason. It should stop all publishing after
   emitting this notification.

#### Server side

The server has to do multiple things in parallel to accommodate dynamically connecting and disconnecting ESP32s. The
following is thus in no strict order.

1. The server subscribes to `state/join` to record any joins
   1. When there is a new join, the server publishes on `state/nameAssign` a unique name. `:` characters is restricted for name assignments since it is used as a separator inside message payloads.
1. The server subscribes to `state/leave` to record anyone leaving the network
   1. The used name for the leaving sensor is marked as already used and the sensor as disconnected.
1. If any name change request comes in from the web server, it is published on `state/nameAssign`
1. If any LED command comes in from the web server, it is published on `led/command`
1. All collected data is recorded to the database for channels `led/status`, `button/status`, `photoresistor/status`.

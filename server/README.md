# Server side programs

Here you can find a description of the "server" side components of the system including the web server, the MQTT client
for the web server and more. They are all organized into their own subfolders.

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

The keepalive interval has to be **strictly** lower than 6 seconds.

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

ESP32s use this channel to notify the web server that they joined the network as a newcomer. This is to be used right after connecting to the broker and before publishing anything else. This assigns an optimized name to the ESP32 that accelerates lookups on the server database side as well as a session id that helps distinguish disconnects.

* `state/leave` (QoS 2)

ESP32s use this channel to notify the web server that they are leaving the network. This should be done right before disconnecting from the broker. ESP32s must set an [LWT message](https://www.hivemq.com/blog/mqtt-essentials-part-9-last-will-and-testament/) on this channel upon their initial joining procedure to the application network to guard against unexpected disconnections (see how in the [protocols section](#protocolexchanges) further on.

* `state/nameAssign` (QoS 2)

This channel is used by the web server to give an optimized unique name to a newly joined ESP32. This name will figure in
every published message to identify the ESP32 that is communicating. It also gives a session id to be used along with
the name on all messages. This message is published right after a join
message is received by the web server.

### Payload formats

All messages are prefixed with the name and the session id that the web server has assigned to the ESP32 to determine who is who and what is when. See the
next section on the protocol to grasp in which order to use each channel and in what cases should they be used.

* `led/command`

`<name>;<session_id>;<1|0>`

The payload is in three parts, first the assigned name, then a semi colon as the separator, then the session_id, and then a value of `1` or `0`. `1` indicates a request to turn the LED **ON**. `0` indicates a request to turn the LED **OFF**. Mind you there are no spaces to keep the message minimal.

Example: `capteur01;1743946777.603371;1`

* `led/status`

`<name>;<session_id>;<1|0>`

Same as before. But this time it is the ESP32s that publish this message whenever the state of their LED is changed.
This is necessary since multiple web server clients could issue commands to the same ESP32 and all of their UI needs to
be updated according to the latest state even if another client issued a command.

Example: `capteur02;1743946777.603371;0`

* `button/status`

`<name>;<session_id>;<1|0>`

`1` indicates a button **PUSH** event, whereas a `0` indicates a button **RELEASE** event.

Example: `optimus;1743946777.603371;1`

* `photoresistor/status`

`<name>;<session_id>;<0-100>`

At regular intervals ESP32s publish the value read from their photoresistor as a percentage. Thus the value after the
name is between and including 0 and 100.

Example: `capteur01;1743946777.603371;58`

* `state/join`

`<@MAC>` or `<name>;<session_id>`

The initial identifier for an ESP32 is its MAC address. We assume that this value is unique among all devices participating in the applicative network. This is to ensure uniqueness in the name assignment period (to know who the name is destined to). If this assumption is not true (which is the case in practice), then our system is vulnerable to MAC address collisions or deliberate spoofing as more than one device could modify the records of a single device on the server side.

If the message is simply the MAC address, then this means the ESP32 is initiating a new session. Any messages from its
previous session that may be received by the server are now considered out of band and are to be discarded.

If the message is the assigned name and the assigned session id, then this means the ESP32 is starting the previously
created session. This session having replaced the old session upon creation is thus the current session. This means that
the ESP32 went through the reconnect procedure and was thus able to set up its LWT properly to track any sudden
disconnections on the server side. See the [protocol](#protocolexchanges) section below for more details on how all this
works.

Example: `61:EC:ED:3B:25:B1` or `capteur02;1743946777.603371`

* `state/leave`

`<name>;<session_id>`

Just the assigned name and session id of the ESP32 is enough in this case to consider it unreachable on the web server side.

Example: `capteur01;1743946777.603371`

* `state/nameAssign`

`<@MAC;name;session_id>`

A new name and session id assignment.

The web server may assign any string as a name (at most **30 characters** including the trailing zero). Most likely the default will be something like `capteurXX` where `XX` is an incrementing number depending on the number of previously connected ESP32s. But it could also simply be a number (`1`, `54`) or a custom name most likely assigned by a web server client (`LeBron`).

Once received, this name should be stored by the ESP32s and used to identify themselves when publishing messages or when
subscribed to channels to determine if a message concerns them.

As a reminder, for memory allocations on the ESP32s, a MAC address takes up 17 characters, a server assigned name takes up 29 characters + 1 trailing zero and a session id takes up 17 characters + 1 trailing zero. Thus the `<name;session_id>` couple used to identify each device should hold on 29 (name) + 1 (semi colon) + 17 (session id) + 1 (trailing zero) = 48 characters.

Example: `61:EC:ED:3B:25:B1;capteur01;1743946777.603371`

### Protocol/exchanges

This is the order in which channels should be used to form an applicative protocol. Make sure to respect quality of
service (QoS) levels described in the [channels](#channels) section when publishing.

#### ESP32

1. ESP32 boots
1. ESP32 connects to the broker via the IP of the Raspberry PI on the network on port 1883 (the default). The keepalive
   must be **strictly smaller than 6 seconds** (4, 5...)
1. Once the connection is established (CONNACK)
   1. ESP32 publishes its MAC address on `state/join` to indicate its fresh arrival.
   1. ESP32 listens on `state/nameAssign` that it already subscribed to before emitting a join notification to avoid
      missing a beat.
   1. ESP32 receives a name and a session id and stores it for future use in its messages.
1. ESP32 diconnects and reconnects to the broker setting up an LWT message on the `state/leave` channel including its
   received credentials.
1. ESP32 publishes its name and session id couple on `state/join` to indicate its starting the previously created session.
1. A session is started.
1. Usual operation starts here (in no particular order)
   1. `led/command`: ESP32 subscribes to this channel to receive on/off commands
   1. `led/status`: ESP32 publishes on this channel whenever its LED changes state
   1. `button/status`: ESP32 publishes on this channel whenever its button changes state
   1. `photoresistor/status`: ESP32 publishes on this channel at regular intervals sending readings from its photoresistor
1. ESP32 publishes on `state/leave` if it wants to leave the network for any reason. It should stop all publishing after
   emitting this notification. This is normally meant to happen via the LWT message set before on behalf of the ESP32
since generally the only way to shut it down is to unplug it from power. But optionally if some sort of graceful
shutdown is considered for implementation, a message could manually be published also.

If a reconnection is necessary to the broker due to disruptions in the network, restart the steps from step 2. This is
important especially to refresh the session id. This creates a new session and makes it possible to detect a spurious
disconnect.

ESP32s thus store no persistant state and either connection disruptions or reconnects due to the network or complete
failure, reboot or power loss should all require the same steps to become operational again. This stateless nature
should simplify ESP32 code and make them disposable.

#### Server side

The server has to do multiple things in parallel to accommodate dynamically connecting and disconnecting ESP32s. The
following is thus in no strict order.

1. The server subscribes to `state/join` to record any joins
   1. When there is a new join, the server publishes on `state/nameAssign` a unique name and a session id. `;` characters is restricted for name assignments since it is used as a separator inside message payloads.
   1. The server always assigns the same name to a device thanks to its MAC address that is assumed unique. This avoids duplicate entries in the database.
   1. Upon initial database record creation (truly initial connection of the ESP32) or later when only a MAC address is received to indicate new session creation, the device is considered disconnected and a new session id is generated, stored and also sent back. On a truly initial connection, the database record is created and timestamps are accordingly set.
   1. If a name and a session id is received on the other hand, this is checked against the database and if there is a
      match, the device is only then considered online/connected. Updates of timestamps happen here.
1. The server subscribes to `state/leave` to record anyone leaving the network
   1. The used name for the leaving sensor is marked as already used and the sensor as disconnected.
   1. If an out of band leave message comes in concerning a device, it is discarded thanks to its unmatching session_id
      be it another leave or sensor readings. This avoids unnecessary online/offline marking and weirdness in browser UI.
1. If any LED command comes in from the web server, it is published on `led/command`
1. All collected data is recorded to the database for channels `led/status`, `button/status`, `photoresistor/status`.
   1. Unless the session id doesn't match, in which case the updates are discarded.

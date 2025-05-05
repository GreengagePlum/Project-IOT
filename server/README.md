# Server side programs

Here you can find a description of the "server" side components of the system including the web server, the server side MQTT client
and more. They are all organized into their own subfolders. A list of the notable files and folders (including residual
files) is as follows:

* `db/`: Database schemas and configuration files
  * `db/models/`: Database schemas, dummy data for testing and the script to create the SQLite database
  * `db/db.sqlite3`: The SQLite database file (if you already created it)
* `mqtt/`: This is where the server side MQTT related components reside.
  * `mqtt/mqtt_client/`: server side MQTT client source files. It is a Python package.
  * `mqtt/mosquitto.conf`: `mosquitto` MQTT broker configuration file tailored for our project's needs
  * `mqtt/mosquitto.log`: `mosquitto` MQTT broker log file (if you launched it before)
* `web_server/`: Flask web server source files as well as frontend web UI files and assets.

When designing and implementing the server side components, certain assumptions were made to limit code complexity and
shorten development time. It is assumed that the server components are always online and without failure. They are
assumed to always have been launched before any ESP32 device starts running. And thus, from an ESP32 point of view, the
server components are always available. The design also assumes an MQTT keepalive time of 5 seconds for ESP32s and the use of LWT messages to properly keep track of any unintended disconnects. The design also considers the MQTT QoS values to be respected to properly function (see [further below](#mqtt-communications-specification)). And lastly it is assumed that between the moment the `/capteurs` page is requested from the web server and the moment the page loads and connects to the MQTT broker (the critical section), there are no ESP32 connection or disconnect events (so either before or after, otherwise the web UI can't update in real time without a refresh, see [further below](#python-flask-web-server)). These aspects could be circled back on later to improve the overall robustness of the whole system if need be by of course introducing more or less complexity and additional development time.

## Usage

Use the given `Makefile` to launch each program or "component". `make help` should display a list of things you can do. This includes
launching the web server, the MQTT broker and the MQTT server side client. You should make sure to have at least **Python 3.9+**
along with the dependencies in `requirements.txt` installed via `pip` (preferably in a virtual environment). **External
dependencies** also include the programs `sqlite3` and `mosquitto`.

One example of the suite of commands could be the following after having checked your Python version with `python
--version` (in this current `server/` directory):

```sh
python -m venv .venv # Create a Python virtual environment (optional)
. .venv/bin/activate # Activate the created virtual environment (optional)
python -m pip install --upgrade pip # Update `pip` to the latest version (optional but recommended)

pip install -r requirements.txt # Install all the necessary Python dependencies
make clean # Remove the SQLite database (just in case it was leftover, this removes all the data!)
make db # Create the SQLite database
```

Then you can either use 3 separate terminals or a tool like `screen` to multiplex a single terminal and put processes in
the background to launch the 3 core components of the "server" (make sure to have your virtual environment activated if
you created one before any of these commands)

```sh
make broker # Launches the `mosquitto` MQTT broker with our project's custom configuration
make client # Launches the server side Python MQTT client
make prod # Launches the Flask app with the production Python web server `gunicorn` on all IPs (port 8000)
```

There is also the following commands `make data` and `make debug` to insert some dummy (incoherent) data to the database for
testing purposes and also to launch the Flask debugging web server that binds only to the localhost IP for development
purposes respectively.

### Couple things to note

In general the database has to have been created before any component is launched except for the MQTT broker of course
which is a completely independent component. You don't have to recreate or reset the database every time but only when you
want to start fresh or after initial cloning of this Git repository of course.

As far as the order in which to launch the 3 components, you should at least launch the MQTT broker first before the
others and make sure it successfully launched and is running before moving on to the rest.

#### MQTT broker

* Make sure to have the ports 1883 and 9001 free and available on your machine. There could for example be a systemd
MQTT service running on this port (1883) in the background that you might need to stop.
* Make sure your machine's firewall is disabled to accept connections coming from the ESP32s to the MQTT broker from your local network.

#### MQTT client

* It is necessary to have the web server also running for the client to fully come online since otherwise it will block
  on opening the POSIX pipe for reading until a writer also opens it. This can be simulated via `exec 3> /tmp/IOC_ERKEN_PRANDO` to open
  the pipe for writing and to unblock the MQTT client if you only want to run it and not the other components. But since
  this is an MQTT client it at least needs the broker to be running to function. You can also use `exec 3>&-` to close
the pipe for writing and thus send an `EOF` to the client.

#### Web server

* It is necessary to have the MQTT client also running for the web server to fully come online since otherwise it will block
  on opening the POSIX pipe for writing until a reader also opens it. This can be simulated via `cat /tmp/IOC_ERKEN_PRANDO` to open
  the pipe for reading and to unblock the web server if you only want to run it and not the other components.
* Make sure to have the port 8000 (for the production server) or the port 5000 for the Flask debug server free and
available on your machine.

## Details on each "component"

### MQTT broker

A custom configuration file is created for the `mosquitto` MQTT broker. This includes:

* Logging to the file `mqtt/mosquitto.log` in parallel to `stderr`.
* A maximum allowed client keepalive value of 12 seconds.
* A maximum allowed packet size of 200 bytes.
* Disabling persistence of the broker.
* Creating listeners
  * A listener on the port 1883 (default) listening on all IPv4 and IPv6 addresses and not just localhost
  * A websocket listener on the port 9001 listening on all IPv4 and IPv6 addresses (?)
* Allowing anonymous connections (without providing a username)
* A global maximum connection limit of 20 connections.

This configuration was written regarding the needs of this project and it is recommended to launch `mosquitto` using the
provided `Makefile` so that it uses this configuration file.

### MQTT client

[Eclipse Paho](https://github.com/eclipse-paho/paho.mqtt.python?tab=readme-ov-file) library is used for MQTT
communications in this program.

`Python 3.11.3` was used during development but any version that is 3.9+ should normally work as well. Currently this program is written to use two threads (Python threads mind you) to handle MQTT communications in one hand and the incoming data from the web server via the POSIX pipe on another thread.

This MQTT client has multiple jobs and is a core component of the whole system working alongside the web server. It's
jobs are essentially:

* Listen on the MQTT messages to process any incoming "join" requests to assign a unique name (inside the application
network) to the joining device and create an initial database record for the device (ESP32).
* Listen on the MQTT messages relating to sensor value readings to record these into the database for the related
device.
* Record initial join and last seen timestamps for the devices on the application network.
* Assign unique session IDs to devices to be able to differentiate between each of their connections and safely discard
  any out of band data.
* Listen on any incoming LED control commands from the web server (via the POSIX pipe) and relay the command to the
related device (after some checks on its presence) to control its LED state.

So this is the main program (and only) that manages and writes to the database in the whole system.

### Python Flask web server

`Python 3.11.3` was used during development but any version that is 3.9+ should normally work as well. The [Flask](https://flask.palletsprojects.com/en/stable/) framework was used in the making.

The web server's roles are simple. Provide the dynamic web pages upon request, filled with data from the database.
Provide information from the database on a specific device upon request (AJAX GET requests from the web UI). As well as
relay any LED command that comes in via an AJAX GET request through the web UI to the MQTT client so that it can be
propagated to the related device via MQTT.

The web server is thus a solely read only client of the database.

The website requires JavaScript to properly function and if not displays a warning message urging you to enable this
functionality.

For the time being the "Changer d'agencement" (change layout) button on the pages `/capteurs` and `/historique` is not working and this functionality **hasn't been implemented** as it wasn't of high priority. The web UI is also **not fully responsive** and is thus only made for desktop/laptop devices. There was also a planned name change feature to assign familiar names to each device from the web UI via POST requests **which was scrapped** due to time constraints.

The web pages and their features are as follows:

* `/accueil` page

This page is to introduce the project with some photos and quick explanations on what it is for and what it does. Simply
for decorative purposes.

This page's content **hasn't been implemented** for the time being as it wasn't of high priority.

* `/capteurs` page (extra work, not asked for in the project paper)

This page is quite special in that it started as an experiment on the real time aspects that we could bring into this
project. After seeing the potential and success in its development, we decided to include it.

This page displays the devices that are *actively* connected to the application network. Meaning only the devices that
are currently communicating with the MQTT broker (sending regular updates on their sensor readings) are listed here and
not the ones that were previously active but not momentarily.

This page is designed to be completely real time and dynamic and it has some cool features to go for it. It makes use of a JavaScript MQTT client in the browser called [MQTT.js](https://github.com/mqttjs/MQTT.js/) to get direct access to the updates inside the application network. This allows for the page to automatically display devices when they join and remove them from the UI when they leave (or are disconnected) without refreshing the page.

This is the only page that makes use of an MQTT client on the whole website. It's also worth mentioning that MQTT is
only listened to in this page and is thus used read only. This page never publishes any messages to any channel, it just
listens for events to update the page's UI in real time.

This page shows for each connected device the state of its LED, push button and photoresistor in real time. When you push
the button, the UI updates almost instantly and readings at regular intervals from the photoresistor are displayed as a
real time chart (the last 10 readings) as new data comes in. The photoresistor values given in percentage indicate the amount of light, thus 100% meaning maximum light and
0% meaning maximum shadow. The timestamps in this chart are in your browser's local timezone. As for the LED part, it is not only used to display its
state but also to control it. One can easily turn the LED on or off for a specific active device.

When it comes to how controlling the LED works, the LED checkbox on the web UI is an HTML form with an event listener
which whenever the checkbox changes state (checked/unchecked), an AJAX GET request is made to a certain endpoint of the
web server in the background. This request from the browser doesn't expect any response but is used only to relay data to the web server.
The web server upon reception of this request than transmits it to the MQTT client via a POSIX pipe so that the LED
command can be relayed to the relative ESP32. This could have been a POST request too but given the simplicity of our
purpose, we chose a simple GET request instead. This could have also been achieved by bypassing the web server
completely and directly publishing on the relative MQTT channel to control the ESP32. This wasn't done for two purposes:
firstly the use of a POSIX pipe was required by the project paper and secondly, this type of shortcut would bypass any
checks done on the server side. This would also complicate state management more as there would be then an additional
MQTT publisher acting as a controller other than the server side MQTT client. This would also invalidate the read only
nature of the MQTT connectivity inside this page that keeps things simple.

Upon reception of a join message, one of two things happen to update the web UI. If the device with the received ID is
already being displayed, its session ID is updated accordingly to be able to discard out of band messages. Otherwise if
the device is not already being displayed (either a completely new device or recently disconnected from the network)
then its details are fetched via an AJAX GET request to a certain endpoint of the web server which responds with HTML
dynamically generated with the latest details of the requested device from the database. This HTML is dynamically
inserted into the DOM and is thus displayed without the necessity to refresh the page.

And lastly, and arguably the coolest part. There can be more than one client on the web UI. Yes, multiple people on multiple
computers can have this page open and control and view the devices simultaneously. As someone activates the LED, the
state will update on all the other people's browsers and same goes for the push button. And thus technically, people
could play a game where two or more people could spam the LED control each on their computers to see who wins!

There is also a local filtering functionality (a filter bar) on this page in case there are too many connected devices to only display
what you are looking for.

* `/historique` page

This is the required part of the project. This page displays the last 10 values recorded to the database for every
device (ESP32) that ever connected to the application network (thus also the currently inactive ones). 10 values being
the most recent on top to the oldest for each of LED activation/deactivation events, push button push/release events as
well as photoresistor readings. If no value has yet been recorded for a device's part, a message indicating this is
displayed in the relative box. The values are all prefixed with a UTC timestamp taken the moment it was recorded to the
database. The photoresistor values given in percentage indicate the amount of light, thus 100% meaning maximum light and
0% meaning maximum shadow.

This page also shows for each displayed device its "last seen" and "joined at" timestamps in UTC timezone.

The devices here are listed from the most recently "last seen" on top to the oldest "last seen".

There is also a local filtering functionality (a filter bar) on this page in case there are too many listed devices to only display
what you are looking for.

### SQLite database

The database is completely managed from Python via [SQLAlchemy](https://www.sqlalchemy.org/). This includes its
creation, its settings, the tables and the schemas as well as the insertion and retrieval of any data. There are
constraint triggers to validate any data to be recorded. The timestamps are kept in UTC timezone. All the data is mapped
to Python classes. The database isolation level is also set to `SERIALIZABLE` as SQLite doesn't support the actually
planned isolation level of `READ COMMITTED`. This kind of isolation level is necessary to ensure coherent display of
values on the web UI when for example there are ongoing join or leave transactions that have to happen atomically.

## MQTT communications specification

This part describes the MQTT communications used to make the whole system come together. **MQTT v5** is considered for
use in this project.

The keepalive interval has to be **strictly** lower than 12 seconds (initially was 6 but the Raspberry Pi 3 doesn't
allow for such a small value). It is recommended to **use a 5 second keepalive** inside the ESP32s to keep the responsiveness of the system against unintended disconnects.

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

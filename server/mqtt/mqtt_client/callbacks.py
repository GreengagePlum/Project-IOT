import logging
from .utils import *
from .constants import *
from .models.sensor import Sensor
from .models.sensor import LedStatus
from .models.sensor import ButtonStatus
from .models.sensor import PhotoresistorStatus

# TODO: Make checks more robust (sensor readings coming from a disconnected sensor)

log = logging.getLogger(LOGGER_name + ".callbacks")


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    log.info("Connected with result code [%s]", str(reason_code))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(CHANNEL_state_join)
    client.subscribe(CHANNEL_state_leave)
    client.subscribe(CHANNEL_led_status)
    client.subscribe(CHANNEL_button_status)
    client.subscribe(CHANNEL_pres_status)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    log.info(
        "Received following message without a specific handler defined [%s]",
        msg.topic + " " + str(msg.payload),
    )


# The callback for messages on join channel
def on_join(client, userdata, msg):
    log.debug("Received message on channel [%s]", CHANNEL_state_join)
    split = str(msg.payload, encoding="ascii").split(PAYLOAD_seperator)
    assert 1 <= len(split) <= 2, "Malformed message payload"
    # TODO: continue adding logs from here and then utils.py
    if len(split) == 1:  # case of an initial connection (only a MAC address received)
        mac = split[0]
        if sensor_exists_record(mac=mac):
            id, ssnid = sensor_create_session(mac=mac)
        else:
            id, ssnid = sensor_create_record(mac)
        sensor_assign_credentials(mac, str(id), ssnid)
    else:  # case of the second step of a network join (assigned name and session id received)
        name, ssnid = split
        id = int(name)

        # sussy situation if fails,
        # means that the RBPi 3 or at least this MQTT client is restarted (or somehow the database
        # got nuked during execution) while the application network was operational with ESP32s already
        # communicating. This is assumed to never happen since the server components are assumed to always be live.
        #
        # This case technically cannot occur unless the database is not persistant, queries did not persist yet before
        # the catastrophic restart or it just got deleted and we are starting fresh...
        assert sensor_exists_record(id), "Impossible edge case happened, good luck..."

        sensor_session(id, ssnid, start=True)


# The callback for messages on join channel
def on_leave(client, userdata, msg):
    log.debug("Received message on channel [%s]", CHANNEL_state_leave)
    split = str(msg.payload, encoding="ascii").split(PAYLOAD_seperator)
    assert len(split) == 2, "Malformed message payload received"
    id = int(split[0])
    ssnid = split[1]
    if sensor_exists_record(id):
        sensor_session(id, ssnid, start=False)


# The callback for messages on join channel
def on_led_status(client, userdata, msg):
    log.debug("Received message on channel [%s]", CHANNEL_led_status)
    split = str(msg.payload, encoding="ascii").split(PAYLOAD_seperator)
    assert len(split) == 3, "Malformed message payload received"

    id = int(split[0])
    ssnid = split[1]
    state = bool(int(split[2]))

    # TODO: Maybe also check if sensor status is online?
    if not sensor_exists_record(id) or not sensor_check_session(id, ssnid):
        return

    status = LedStatus(sensor_id=id, status=state)
    database_record(status)
    sensor_update_last_seen(id)


# The callback for messages on join channel
def on_button_status(client, userdata, msg):
    log.debug("Received message on channel [%s]", CHANNEL_button_status)
    split = str(msg.payload, encoding="ascii").split(PAYLOAD_seperator)
    assert len(split) == 3, "Malformed message payload received"

    id = int(split[0])
    ssnid = split[1]
    state = bool(int(split[2]))

    # TODO: Maybe also check if sensor status is online?
    if not sensor_exists_record(id) or not sensor_check_session(id, ssnid):
        return

    status = ButtonStatus(sensor_id=id, status=state)
    database_record(status)
    sensor_update_last_seen(id)


# The callback for messages on join channel
def on_pres_status(client, userdata, msg):
    log.debug("Received message on channel [%s]", CHANNEL_pres_status)
    split = str(msg.payload, encoding="ascii").split(PAYLOAD_seperator)
    assert len(split) == 3, "Malformed message payload received"

    id = int(split[0])
    ssnid = split[1]
    state = int(split[2])

    # TODO: Maybe also check if sensor status is online?
    if not sensor_exists_record(id) or not sensor_check_session(id, ssnid):
        return

    status = PhotoresistorStatus(sensor_id=id, status=state)
    database_record(status)
    sensor_update_last_seen(id)

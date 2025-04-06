from .utils import *
from .constants import *
from .models.sensor import Sensor
from .models.sensor import LedStatus
from .models.sensor import ButtonStatus
from .models.sensor import PhotoresistorStatus

# TODO: Insert logging calls to edge areas
# TODO: Make checks more robust (sensor readings coming from a disconnected sensor)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(CHANNEL_state_join)
    client.subscribe(CHANNEL_state_leave)
    client.subscribe(CHANNEL_led_status)
    client.subscribe(CHANNEL_button_status)
    client.subscribe(CHANNEL_pres_status)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


# The callback for messages on join channel
def on_join(client, userdata, msg):
    try:
        name = int(msg.payload)
    except ValueError:
        id = create_sensor_record()
        assign_name(str(msg.payload, encoding="ascii"), str(id))
    else:
        if sensor_record_exists(id=name):
            mark_as_online(id=name)
        else:
            create_sensor_record(id=name)


# The callback for messages on join channel
def on_leave(client, userdata, msg):
    try:
        name = int(msg.payload)
    except ValueError:
        return
    if sensor_record_exists(id=name):
        mark_as_offline(id=name)


# The callback for messages on join channel
def on_led_status(client, userdata, msg):
    part1, part2 = str(msg.payload, encoding="ascii").split(":", 1)
    try:
        id = int(part1)
    except ValueError:
        return
    if not sensor_record_exists(id):
        return

    try:
        state = int(part2)
    except ValueError:
        # malformed payload
        return

    status = LedStatus(sensor_id=id, status=state)
    record_database(status)


# The callback for messages on join channel
def on_button_status(client, userdata, msg):
    part1, part2 = str(msg.payload, encoding="ascii").split(":", 1)
    try:
        id = int(part1)
    except ValueError:
        return
    if not sensor_record_exists(id):
        return

    try:
        state = int(part2)
    except ValueError:
        # malformed payload
        return

    status = ButtonStatus(sensor_id=id, status=state)
    record_database(status)


# The callback for messages on join channel
def on_pres_status(client, userdata, msg):
    part1, part2 = str(msg.payload, encoding="ascii").split(":", 1)
    try:
        id = int(part1)
    except ValueError:
        return
    if not sensor_record_exists(id):
        return

    try:
        state = int(part2)
    except ValueError:
        # malformed payload
        return

    status = PhotoresistorStatus(sensor_id=id, status=state)
    record_database(status)

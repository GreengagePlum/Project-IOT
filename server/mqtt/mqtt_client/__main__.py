import os
import pickle
import signal
import logging
from . import mqttc
from .constants import *
from .callbacks import *
from .utils import sensor_send_led_command

log = logging.getLogger(LOGGER_name)


# Signal handler function
def handler(signum, frame):
    log.debug("Signal handler called with signal %d", signum)
    pickle.dump(FIFO_poison, interrupt_write)
    global is_interrupted
    is_interrupted = True


mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.message_callback_add(CHANNEL_state_join, on_join)
mqttc.message_callback_add(CHANNEL_state_leave, on_leave)
mqttc.message_callback_add(CHANNEL_led_status, on_led_status)
mqttc.message_callback_add(CHANNEL_button_status, on_button_status)
mqttc.message_callback_add(CHANNEL_pres_status, on_pres_status)


log.info("Initiating MQTT connection")
mqttc.connect("localhost", keepalive=5)

# Start the MQTT client on a background thread
mqttc.loop_start()

# Create and open fifo for reading
try:
    log.info("Trying to create read FIFO incoming from web server")
    os.mkfifo(FIFO_path)
except FileExistsError:
    log.info("Read FIFO already exists")
ws_to_mqtt = open(FIFO_path, mode="rb", buffering=0)

# Setup for graceful shutdown on C-c or SIGINT
interrupt_write = open(FIFO_path, mode="wb", buffering=0)
is_interrupted = False
signal.signal(signal.SIGINT, handler)

# Infinite loop (quit on C-c, SIGINT) to read and relay led command messages from the web server to the ESP32s
while not is_interrupted:
    try:
        led_command = pickle.load(ws_to_mqtt)
    except EOFError:
        # This happens if the web server (who opened the fifo in write mode) closes the fifo
        # We continue our loop hoping our oratar comes back
        log.debug(
            "The FIFO was either closed by its writer or a serialization error occured, attempting further reads"
        )
        continue
    assert type(led_command) == str
    if led_command == FIFO_poison and is_interrupted:
        # This happens if the SIGINT signal handler is called when we were blocked in a fifo read op
        break
    log.info("Received following command from server [%s]", led_command)
    split = led_command.split(PAYLOAD_seperator)
    assert len(split) == 3
    id = int(split[0])
    ssnid = split[1]
    cmd = int(split[2])
    sensor_send_led_command(id, ssnid, cmd)

# Close and try to remove the fifo
ws_to_mqtt.close()
interrupt_write.close()
try:
    log.info("Trying to remove read FIFO incoming from web server")
    os.unlink(FIFO_path)
except FileNotFoundError:
    pass

log.info("Gracefully exiting...")

# Stop the MQTT client background thread
mqttc.disconnect()

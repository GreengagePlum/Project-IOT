from . import mqttc
from .constants import *
from .callbacks import *
from .utils import send_led_command


mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.message_callback_add(CHANNEL_state_join, on_join)
mqttc.message_callback_add(CHANNEL_state_leave, on_leave)
mqttc.message_callback_add(CHANNEL_led_status, on_led_status)
mqttc.message_callback_add(CHANNEL_button_status, on_button_status)
mqttc.message_callback_add(CHANNEL_pres_status, on_pres_status)


mqttc.connect("localhost", keepalive=5)

mqttc.loop_start()

# FIFO create/check /tmp
# FIFO open

while True:
    # FIFO loop via selectors
    pass

# FIFO close

mqttc.loop_stop()

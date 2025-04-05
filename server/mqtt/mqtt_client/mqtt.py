import paho.mqtt.client as mqtt
import time
from threading import Thread


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("hello")


mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
# mqttc.suppress_exceptions = True
mqttc.on_connect = on_connect
# mqttc.on_message = on_message


# The callback for when a PUBLISH message is received from the server.
@mqttc.message_callback()
def on_message(client, userdata, msg):
    def op(client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        time.sleep(5)

    Thread(target=op, args=[client, userdata, msg]).start()


mqttc.connect("localhost", keepalive=5)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqttc.loop_forever()

import logging
import paho.mqtt.client as mqtt
from sqlalchemy import create_engine
from .constants import *

# TODO: Fine tune logging
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.enable_logger()
# mqttc.suppress_exceptions = True

engine = create_engine("sqlite:///db/db.sqlite3", echo=False, hide_parameters=False)

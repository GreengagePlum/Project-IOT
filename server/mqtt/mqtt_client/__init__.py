import logging
import paho.mqtt.client as mqtt
from sqlalchemy import create_engine
from .constants import *

__version__ = "0.1.0"

# Create the MQTT client
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.enable_logger()
# mqttc.suppress_exceptions = True


# Fine tune logging
console_full = logging.StreamHandler()
console_full.setFormatter(
    logging.Formatter(
        fmt="< %(asctime)-26s | %(name)-24s | %(levelname)-8s >\n%(message)s\n",
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )
)
logging.basicConfig(level=logging.INFO, handlers=[console_full])
package_logger = logging.getLogger(LOGGER_name)
package_logger.setLevel(logging.INFO)
package_logger.addHandler(console_full)
sqlalchemy_engine_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_engine_logger.setLevel(logging.INFO)
sqlalchemy_engine_logger.addHandler(console_full)
sqlalchemy_pool_logger = logging.getLogger("sqlalchemy.pool")
sqlalchemy_pool_logger.setLevel(logging.INFO)
sqlalchemy_pool_logger.addHandler(console_full)
paho_logger = mqttc.logger
paho_logger.setLevel(logging.INFO)
paho_logger.addHandler(console_full)


# Create the database connectivity via sqlalchemy
engine = create_engine(
    "sqlite:///db/db.sqlite3",
    echo=False,
    hide_parameters=False,
    execution_options={"isolation_level": "SERIALIZABLE"},
)

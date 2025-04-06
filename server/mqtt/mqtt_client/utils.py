from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional
from . import mqttc, engine
from .constants import *
from .models.sensor import Base, Sensor


def assign_name(existing_name: str, new_name: str):
    payload = existing_name + ":" + new_name
    mqttc.publish(topic=CHANNEL_state_name_assign, payload=payload, qos=2)


def mark_as_online(id: int):
    with Session(engine) as session:
        sensor = session.get(Sensor, id)
        sensor.status = True
        session.commit()


def mark_as_offline(id: int):
    with Session(engine) as session:
        sensor = session.get(Sensor, id)
        sensor.status = False
        session.commit()


def send_led_command(id: int, command: int):
    if command not in [1, 0]:
        # error out or log or smth
        return
    # check if id exists in db and is actively connected...
    payload = str(id) + ":" + command
    mqttc.publish(topic=CHANNEL_led_command, payload=payload, qos=1)


def record_database(model: Base):
    with Session(engine) as session:
        session.add(model)
        session.commit()


def sensor_record_exists(id: int) -> bool:
    with Session(engine) as session:
        return bool(session.get(Sensor, id))


def create_sensor_record(id: Optional[int] = None, name: Optional[str] = None) -> int:
    sensor = Sensor(id=id, name=name, status=True)
    with Session(engine) as session:
        session.add(sensor)
        session.commit()
        recent_id = sensor.id
    return recent_id

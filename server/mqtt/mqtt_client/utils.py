from time import time
from datetime import datetime
from datetime import timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from . import mqttc, engine
from .constants import *
from .models.sensor import Base, Sensor


def sensor_assign_credentials(mac: str, name: str, session_id: str):
    assert type(mac) == str
    assert type(name) == str
    assert type(session_id) == str
    payload = mac + PAYLOAD_seperator + name + PAYLOAD_seperator + session_id
    mqttc.publish(topic=CHANNEL_state_name_assign, payload=payload, qos=2)


def sensor_create_session(mac: str) -> (int, str):
    assert type(mac) == str
    with Session(engine) as session:
        sensor = session.scalar(select(Sensor).where(Sensor.mac_address == mac))
        new_ssnid = str(time())
        sensor.session_id = new_ssnid
        sensor.status = False
        session.commit()
        return (sensor.id, new_ssnid)


def sensor_session(id: int, session_id: str, start: bool) -> bool:
    assert type(id) == int
    assert type(session_id) == str
    assert type(start) == bool
    with Session(engine) as session:
        sensor = session.get(Sensor, id)
        if sensor.session_id != session_id:
            return False
        sensor.status = start
        sensor.last_seen = datetime.now(timezone.utc)
        session.commit()
        return True


def sensor_check_session(id: int, session_id: str) -> bool:
    assert type(id) == int
    assert type(session_id) == str
    with Session(engine) as session:
        sensor = session.get(Sensor, id)
        return sensor.session_id == session_id


def sensor_send_led_command(id: int, session_id: str, command: int):
    assert type(id) == int
    assert type(session_id) == str
    assert type(command) == int
    assert command in [1, 0]

    # check if id exists in db and is actively connected...
    assert sensor_exists_record(id)
    with Session(engine) as session:
        sensor = session.get(Sensor, id)
        if sensor.status == False or sensor.session_id != session_id:
            return

    payload = (
        str(id) + PAYLOAD_seperator + session_id + PAYLOAD_seperator + str(command)
    )
    mqttc.publish(topic=CHANNEL_led_command, payload=payload, qos=1)


def database_record(model: Base):
    assert issubclass(type(model), Base)
    with Session(engine) as session:
        session.add(model)
        session.commit()


def sensor_update_last_seen(id: int = None, mac: str = None) -> bool:
    assert type(id) in [int, type(None)]
    assert type(mac) in [str, type(None)]
    assert id or mac, "At least one parameter is required"
    with Session(engine) as session:
        if id and mac:
            sensor = session.scalar(
                select(Sensor).where(Sensor.id == id and Sensor.mac_address == mac)
            )
        elif id:
            sensor = session.get(Sensor, id)
        else:
            sensor = session.scalar(select(Sensor).where(Sensor.mac_address == mac))
        sensor.last_seen = datetime.now(timezone.utc)
        session.commit()


def sensor_exists_record(id: int = None, mac: str = None) -> bool:
    assert type(id) in [int, type(None)]
    assert type(mac) in [str, type(None)]
    assert id or mac, "At least one parameter is required"
    with Session(engine) as session:
        if id and mac:
            return bool(
                session.scalar(
                    select(Sensor).where(Sensor.id == id and Sensor.mac_address == mac)
                )
            )
        elif id:
            return bool(session.get(Sensor, id))
        return bool(session.scalar(select(Sensor).where(Sensor.mac_address == mac)))


def sensor_create_record(
    mac_address: str, id: Optional[int] = None, name: Optional[str] = None
) -> (int, str):
    assert type(mac_address) == str
    assert type(id) in [int, type(None)]
    assert type(name) in [str, type(None)]
    ssnid = str(time())
    sensor = Sensor(
        id=id, name=name, mac_address=mac_address, status=False, session_id=ssnid
    )
    with Session(engine) as session:
        session.add(sensor)
        session.commit()
        recent_id = sensor.id
    return (recent_id, ssnid)

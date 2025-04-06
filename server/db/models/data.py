"""Dummy data to be inserted into the database.

This data is actually incoherent and doesn't totally make sense. It is mainly for simple testing purposes and also to be
used during the web server development.
"""

from time import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sensor import *

if __name__ == "__main__":

    engine = create_engine("sqlite:///db.sqlite3", echo=True)

    with Session(engine) as session:
        s1 = Sensor(
            id=3,
            name="capteur01",
            status=True,
            mac_address="61:EC:ED:3B:25:B1",
            joined_at=datetime(2025, 3, 3),
            last_seen=datetime(2025, 4, 5),
            session_id=str(time()),
            led_status=[
                LedStatus(status=True, date=datetime(2025, 4, 4)),
                LedStatus(status=False, date=datetime(2025, 4, 5)),
            ],
            button_status=[
                ButtonStatus(status=False, date=datetime(2025, 4, 3)),
                ButtonStatus(status=True, date=datetime(2025, 4, 5, 23, 33, 54, 86)),
            ],
            pres_status=[PhotoresistorStatus(status=87)],
        )
        s2 = Sensor(
            name="capteur02",
            status=False,
            mac_address="53:D6:28:F1:E0:74",
            session_id=str(time()),
        )
        s3 = Sensor(
            name="LeBron",
            status=True,
            mac_address="22:D9:3C:16:19:8A",
            joined_at=datetime(2025, 4, 3),
            last_seen=datetime(2025, 4, 4),
            session_id=str(time()),
            led_status=[
                LedStatus(status=True, date=datetime(2025, 4, 3, 5)),
                LedStatus(status=False, date=datetime(2025, 4, 4)),
            ],
            button_status=[
                ButtonStatus(status=False, date=datetime(2025, 4, 3, 8)),
                ButtonStatus(status=True, date=datetime(2025, 4, 4, 23, 33, 54, 86)),
            ],
            pres_status=[PhotoresistorStatus(status=56)],
        )
        s4 = Sensor(
            id=1,
            name="optimus",
            status=True,
            mac_address="8C:BF:82:08:26:87",
            session_id=str(time()),
        )
        s5 = Sensor(
            status=True,
            mac_address="82:AC:AA:96:3D:41",
            session_id=str(time()),
        )

        session.add_all([s1, s2, s3, s4, s5])

        session.commit()

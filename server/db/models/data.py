from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from datetime import datetime
from sensor import *

if __name__ == "__main__":

    engine = create_engine("sqlite:///db.sqlite3", echo=True)

    with Session(engine) as session:
        s1 = Sensor(
            id=3,
            name="capteur01",
            status=True,
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
        s2 = Sensor(name="capteur02", status=False)
        s3 = Sensor(name="LeBron", status=True)
        s4 = Sensor(id=1, name="optimus", status=True)
        s5 = Sensor(status=True)

        session.add_all([s1, s2, s3, s4, s5])

        session.commit()

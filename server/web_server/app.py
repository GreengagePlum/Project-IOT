from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from sqlalchemy import select
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.sensor import Sensor
from models.sensor import LedStatus
from models.sensor import ButtonStatus

app = Flask(__name__)

# Create the database connectivity via sqlalchemy
engine = create_engine(
    "sqlite:///db/db.sqlite3",
    echo=False,
    hide_parameters=False,
    execution_options={"isolation_level": "SERIALIZABLE"},
)

# Subquery to get the latest LedStatus per sensor by ID
latest_led_id_subq = (
    select(LedStatus.id)
    .where(LedStatus.sensor_id == Sensor.id)
    .order_by(LedStatus.date.desc())
    .limit(1)
    .correlate(Sensor)
    .scalar_subquery()
)

# Subquery to get the latest ButtonStatus per sensor by ID
latest_btn_id_subq = (
    select(ButtonStatus.id)
    .where(ButtonStatus.sensor_id == Sensor.id)
    .order_by(ButtonStatus.date.desc())
    .limit(1)
    .correlate(Sensor)
    .scalar_subquery()
)


@app.route("/")
@app.route("/accueil")
def home_page():
    print(f"ip: {request.host.split(':')[0]}")
    print(f"ip: {request.host}")
    print(f"ip: {request.host_url}")
    print(f"ip: {request.root_url}")
    return render_template("index.html")


@app.route("/capteurs")
def sensors_page():
    with Session(engine) as session:

        # Main query: join Sensor + LedStatus + ButtonStatus filtered to only the latest per sensor
        stmt = (
            select(Sensor, LedStatus, ButtonStatus)
            .outerjoin(LedStatus, LedStatus.id == latest_led_id_subq)
            .outerjoin(ButtonStatus, ButtonStatus.id == latest_btn_id_subq)
            .where(Sensor.status == True)
        )
        results = session.execute(stmt).all()

        sensors = []
        for sensor, led, button in results:
            if led != None:
                sensor.led_status = [led]
            else:
                sensor.led_status = []
            if button != None:
                sensor.button_status = [button]
            else:
                sensor.button_status = []
            sensors.append(sensor)

        return render_template("capteurs.html", sensors=sensors)


@app.route("/historique")
def history_page():
    with Session(engine) as session:
        sensors = session.scalars(select(Sensor)).all()
        return render_template("historique.html", sensors=sensors)


if __name__ == "__main__":
    app.run(debug=True)
    # app.run()

import os
import pickle
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
from models.sensor import PhotoresistorStatus

FIFO_path = "/tmp/IOC_ERKEN_PRANDO"
PAYLOAD_seperator = ";"

# Create and open fifo for writing
try:
    print("Trying to create read FIFO incoming from web server")
    os.mkfifo(FIFO_path)
except FileExistsError:
    print("Read FIFO already exists")
print("Opening FIFO...")
ws_to_mqtt = open(FIFO_path, mode="wb", buffering=0)

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
    return render_template("index.html")


@app.route("/capteurs")
def sensors_page():
    public_ip = request.host.split(":")[0]
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

        return render_template("capteurs.html", sensors=sensors, ip=public_ip)


@app.route("/historique")
def history_page():
    with Session(engine) as session:

        sensors = session.scalars(
            select(Sensor).order_by(Sensor.last_seen.desc(), Sensor.id)
        ).all()

        for sensor in sensors:
            latest_led = (
                select(LedStatus)
                .where(LedStatus.sensor_id == sensor.id)
                .order_by(LedStatus.date.desc())
                .limit(10)
            )
            latest_btn = (
                select(ButtonStatus)
                .where(ButtonStatus.sensor_id == sensor.id)
                .order_by(ButtonStatus.date.desc())
                .limit(10)
            )
            latest_pres = (
                select(PhotoresistorStatus)
                .where(PhotoresistorStatus.sensor_id == sensor.id)
                .order_by(PhotoresistorStatus.date.desc())
                .limit(10)
            )
            sensor.led_status = session.scalars(latest_led).all()[:10]
            sensor.button_status = session.scalars(latest_btn).all()[:10]
            sensor.pres_status = session.scalars(latest_pres).all()[:10]

        return render_template("historique.html", sensors=sensors)


@app.route("/led/<int:id>")
def led_command(id):
    try:
        cmd = int(request.args["cmd"])
    except ValueError:
        abort(400)
    ssnid = request.args["ssnid"]
    msg = str(id) + PAYLOAD_seperator + ssnid + PAYLOAD_seperator + str(cmd)
    pickle.dump(msg, ws_to_mqtt)
    return ("", 204)


@app.route("/sensor/<int:id>")
def sensor_article(id):
    with Session(engine) as session:
        sensor = session.get(Sensor, id)
        return render_template("components/sensor.html", sensor=sensor)


if __name__ == "__main__":
    app.run(debug=True)

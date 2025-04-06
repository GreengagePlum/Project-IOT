.PHONY: help clean debug prod broker client db data

help:
	@echo ""
	@echo "make target"
	@echo ""
	@echo "      target :	help	this message"
	@echo " 		clean	remove the sqlite database file"
	@echo " 		debug	run the development server in debug mode"
	@echo " 		prod	run the production server"
	@echo " 		broker	run the MQTT broker"
	@echo " 		client	run the server side MQTT client"
	@echo " 		db	create the sqlite database"
	@echo " 		data	insert dummy data into the database"
	@echo ""

debug:
	python -m flask --app web_server/app run --debug

prod:
	gunicorn -w 4 'web_server.app:app'

broker:
	cd mqtt/ && mosquitto -c mosquitto.conf

client:
	python -m mqtt.mqtt_client

db: db/db.sqlite3

db/db.sqlite3:
	cd db/ && python models/main.py

data:
	cd db/ && python models/data.py

clean:
	rm -f db/db.sqlite3

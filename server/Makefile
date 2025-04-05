.PHONY: help debug prod broker client

help:
	@echo ""
	@echo "make target"
	@echo ""
	@echo "      target :	help	this message"
	@echo " 		debug	run the development server in debug mode"
	@echo " 		prod	run the production server"
	@echo " 		broker	run the MQTT broker"
	@echo " 		client	run the server side MQTT client"
	@echo ""

debug:
	python -m flask run --debug

prod:
	gunicorn -w 4 'app:app'

broker:
	mosquitto -c mosquitto.conf

client:
	python mqtt_client/mqtt.py

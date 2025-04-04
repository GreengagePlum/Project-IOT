.PHONY: all debug prod help clean

help:
	@echo ""
	@echo "make target"
	@echo ""
	@echo "      target :	help	this message"
	@echo " 		debug	run the development server in debug mode"
	@echo " 		prod	run the production server"
	@echo ""

debug:
	python -m flask run --debug

prod:
	gunicorn -w 4 'app:app'

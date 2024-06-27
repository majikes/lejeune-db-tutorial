all: normal
.PHONY: clean

clean:
	rm -f ../../static/slides/*

PYLINTFLAGS = -rn
PYLINTFILES := reveal.py ReadPowerPointPDF.py updateReveal.py

# Create a target pylint that is dependent on .pylint.app, .pylint.appgames, etc
pylint: $(patsubst %.py,.pylint.%,$(PYLINTFILES))

# Create a target .pylint.app that is dependent on app.py, update .pylint.app when done
.pylint.%: %.py
	pylint $(PYLINTFLAGS) $*.py | tee .pylint.$*

dev:
	@echo Update tmd files to md files and deploy server
	python3 reveal.py deploy=1

normal:
	# Update tmd files to md files and do NOT deploy the server
	(cd ../..; $(MAKE))
	python3 reveal.py deploy=0

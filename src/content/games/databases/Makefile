all: pylint ../../../game-university.json ../../../static/dbs/game-university.game00.sqlite

.PHONY: clean
clean:
	rm -f game-university*.sqlite *.json ../../../static/dbs/game-university\*.sqlite ../../../game-university.json
	rm -f crime*.sqlite *.json ../../../static/dbs/crime\*.sqlite ../../../game-crime.json
	rm -f game*.sqlite ../../../static/dbs/game\*.sqlite ../../../game-nuclear.json

PYLINTFLAGS = -rn
PYLINTFILES := $(wildcard *.py)

# Create a target pylint that is dependent on .pylint.app, .pylint.appgames, etc
pylint: $(patsubst %.py,.pylint.%,$(PYLINTFILES))

# Create a target .pylint.app that is dependent on app.py, update .pylint.app when done
.pylint.%: %.py
	pylint $(PYLINTFLAGS) $*.py | tee .pylint.$*


game-university.game00.sqlite game-university.json: game-university.py
	./game-university.py

../../../game-university.json ../../../static/dbs/game-university.game00.sqlite: game-university.json game-university.game00.sqlite
	@echo Copying databases out to static and home directories
	touch ../game-university-*.tmd
	rm -f ../../../static/dbs/game-universityity.game*sqlite ../../../game-university.json
	cp game-university.game*sqlite ../../../static/dbs
	cp game-university.json ../../../
	cp game-university-schema.png ../../../static/images/


all: pylint ../../../game-nuclear.json ../../../static/dbs/game-nuclear00.sqlite \
	../../../game-university.json ../../../static/dbs/game-university.game00.sqlite \
	../../../game-crime.json ../../../static/dbs/crime00.sqlite
	@echo Making games/databases

.PHONY: clean
clean:
	rm -f game-university*.sqlite *.json ../../../static/dbs/game-university\*.sqlite ../../../game-university.json
	rm -f crime*.sqlite *.json ../../../static/dbs/crime\*.sqlite ../../../game-crime.json
	rm -f game*.sqlite ../../../static/dbs/game\*.sqlite ../../../game-nuclear.json

PYLINTFLAGS = -rn
PYLINTFILES := game-nuclear.py game-crime.py game-university.py

# Create a target pylint that is dependent on .pylint.app, .pylint.appgames, etc
pylint: $(patsubst %.py,.pylint.%,$(PYLINTFILES))

# Create a target .pylint.app that is dependent on app.py, update .pylint.app when done
.pylint.%: %.py
	pylint $(PYLINTFLAGS) $*.py | tee .pylint.$*

game-sailors-1.sqlite game-sailors-2.sqlite: game-sailors.py
	@echo
	@echo Making $@
	-pylint game-sailors.py
	./game-sailors.py
	cp game-sailors-1.sqlite game-sailors-2.sqlite ../../../static/dbs
	touch ../game-sailors-*.tmd

crime00.sqlite game-crime.json: game-crime.py
	@echo creating crime databases
	-pylint game-crime.py
	./game-crime.py

./../../game-crime.json ../../../static/dbs/crime00.sqlite: game-crime.json crime00.sqlite
	@echo Copying crime databases out to static and home directories
	rm -f ../../../static/dbs/crime*sqlite ../../../game-crime.json
	touch ../game-crime-*.tmd
	cp crime*sqlite ../../../static/dbs
	cp game-crime.json ../../../
	cp game-crime-schema.png ../../../static/images/

game-nuclear00.sqlite game-nuclear.json: game-nuclear.py
	./game-nuclear.py

../../../game-nuclear.json ../../../static/dbs/game-nuclear00.sqlite: game-nuclear.json game-nuclear00.sqlite
	@echo Copying databases out to static and home directories
	touch ../game-nuclear-*.tmd
	rm -f ../../../static/dbs/nuclear*sqlite ../../../game-nuclear.json
	cp game-nuclear*sqlite ../../../static/dbs
	cp game-nuclear.json ../../../
	cp game-nuclear-schema.png ../../../static/images/


game-university.game00.sqlite game-university.json: game-university.py
	./game-university.py

../../../game-university.json ../../../static/dbs/game-university.game00.sqlite: game-university.json game-university.game00.sqlite
	@echo Copying databases out to static and home directories
	touch ../game-university-*.tmd
	rm -f ../../../static/dbs/game-universityity.game*sqlite ../../../game-university.json
	cp game-university.game*sqlite ../../../static/dbs
	cp game-university.json ../../../
	cp game-university-schema.png ../../../static/images/


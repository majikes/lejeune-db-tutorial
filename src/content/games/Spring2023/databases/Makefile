all: game-sailors-1.sqlite game-sailors-2.sqlite crime00.sqlite game-crime.json game-nuclear.json

.PHONY: clean
clean:
	rm -f crime*.sqlite *.json ../../../static/dbs/crime\*.sqlite ../../../game-crime.json
	rm -f game*.sqlite ../../../static/dbs/game\*.sqlite ../../../game-nuclear.json

game-sailors-1.sqlite game-sailors-2.sqlite: game-sailors.py
	@echo
	@echo Making $@
	-pylint game-sailors.py
	./game-sailors.py
	cp game-sailors-1.sqlite game-sailors-2.sqlite ../../../static/dbs
	touch ../game-sailors-*.tmd

crime00.sqlite game-crime.json ../../../game-crime.json: game-crime.py
	-pylint game-crime.py
	./game-crime.py
	touch ../game-crime-*.tmd
	rm -f ../../../static/dbs/crime*sqlite ../../../game-crime.json
	cp crime*sqlite ../../../static/dbs
	cp game-crime.json ../../../
	cp game-crime-schema.png ../../../static/images/
	touch ../game-crime-*

game-nuclear00.sqlite game-nuclear.json ../../../game-nuclear.json: game-nuclear.py
	-pylint game-nuclear.py
	./game-nuclear.py
	touch ../game-nuclear-*.tmd
	rm -f ../../../static/dbs/nuclear*sqlite ../../../game-nuclear.json
	cp game-nuclear*sqlite ../../../static/dbs
	cp game-nuclear.json ../../../
	cp game-nuclear-schema.png ../../../static/images/
	touch ../game-nuclear-* ../../worksheets/worksheet-game-nuclear-0*

all: StatesA.sqlite StatesB.sqlite worksheet-03.sqlite

PHONY: clean

clean:
	rm -f *sqlite
StatesA.sqlite StatesB.sqlite: States_Database_script.py
	echo 'Making the states database'
	./States_Database_script.py
	rsync StatesA.sqlite StatesB.sqlite ../static/dbs/

worksheet-03.sqlite: worksheet-03_Database_script.py
	echo 'Making the worksheet-03 database'
	./worksheet-03_Database_script.py
	rsync worksheet-03.sqlite ../static/dbs/


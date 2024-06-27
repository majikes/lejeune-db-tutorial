all: states-A.sqlite states-B.sqlite deploy

.PHONY: clean
clean:
	rm -f states-A.sqlite states-B.sqlite

states-A.sqlite states-B.sqlite: states_Database_script.py
	./states_Database_script.py

deploy: states-A.sqlite states-B.sqlite
	cp $+ ../../../static/dbs

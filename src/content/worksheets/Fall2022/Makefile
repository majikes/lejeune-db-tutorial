all: sailors.sqlite students-A.sqlite students-B.sqlite deploy books1.sqlite

.PHONY: clean
clean:
	rm -f students-A.sqlite students-B.sqlite sailors.sqlite sailors1.sqlite books1.sqlite

students-A.sqlite students-B.sqlite: worksheet-03_Database_script.py
	./worksheet-03_Database_script.py

sailors.sqlite: CreateData.py
	./CreateData.py

sailors1.sqlite: CreateSailors1.py
	./CreateSailors1.py

books1.sqlite books2.sqlite: CreateBooks.py
	./CreateBooks.py

deploy: students-A.sqlite students-B.sqlite sailors.sqlite sailors1.sqlite books1.sqlite books2.sqlite
	cp $+ ../../../static/dbs

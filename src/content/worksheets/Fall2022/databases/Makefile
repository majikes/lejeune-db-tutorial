all: students-A.sqlite students-B.sqlite sailors.sqlite sailors1.sqlite books1.sqlite books2.sqlite sailorsA.sqlite


.PHONY: clean
clean:
	@echo Removing sqlite files from worksheets and worksheets/databases directory
	@rm -f sailors.sqlite books2.sqlite sailorsA.sqlite
	@rm -f ../sailors.sqlite
	@rm -f students-A.sqlite students-B.sqlite sailors1.sqlite books1.sqlite sailors2.sqlite
	@rm -f ../students-A.sqlite ../students-B.sqlite 
	@rm -f sailors1.sqlite
	@rm -f ../sailors1.sqlite
	@rm -f books1.sqlite
	@rm -f ../books1.sqlite

students-A.sqlite students-B.sqlite: worksheet-03_Database_script.py
	@echo 
	@echo Making worksheet/database/$@
	./worksheet-03_Database_script.py
	cp students-A.sqlite students-B.sqlite ../../../static/dbs
	cp students-A.sqlite students-B.sqlite ../
	touch ../*tmd

sailorsA.sqlite: CreateSailorsWithoutPrimaryKey.py
	@echo 
	@echo Making worksheet/database/$@
	-pylint CreateSailorsWithoutPrimaryKey.py
	./CreateSailorsWithoutPrimaryKey.py
	cp sailorsA.sqlite ../../../static/dbs 
	cp sailorsA.sqlite ..
	cp sailorsA.json ../../..
	touch ../*tmd


sailors.sqlite: CreateData.py
	@echo 
	@echo Making worksheet/database/$@
	-pylint CreateData.py
	./CreateData.py
	cp sailors.sqlite ../../../static/dbs
	cp sailors.sqlite  ..
	cp sailors.sqlite sailors.json ../../games/
	cp sailors.json ../../..
	touch ../*tmd

sailors1.sqlite: CreateSailors1.py
	@echo 
	@echo Making worksheet/database/$@
	./CreateSailors1.py
	cp $@ ../../../static/dbs
	cp $@ ../
	touch ../*tmd

books1.sqlite books2.sqlite: CreateBooks.py
	@echo 
	@echo Making worksheet/database/$@
	rm -f books.json
	ln -s ../../../../../assignments/A5/books.json
	./CreateBooks.py
	cp $@ ../../../static/dbs
	cp $@ ../
	touch ../*tmd

aux_files = ../../../static/dbs/wkst.university1.sqlite \
		../../../wkst.university1.json \
		../../../static/dbs/wkst.university2.sqlite \
		../../../static/dbs/wkst.large.university1.sqlite ../../../static/dbs/wkst.large.university1.sqlite \
		../../../wkst.large.university1.json \
		../../../static/dbs/wkst.large.university2.sqlite ../../../static/dbs/wkst.large.university1.sqlite \

all: pylint $(aux_files)

PYLINTFLAGS = -rn
PYLINTFILES := $(wildcard *.py)

# Create a target pylint that is dependent on .pylint.app, .pylint.appgames, etc
pylint: $(patsubst %.py,.pylint.%,$(PYLINTFILES))

# Create a target .pylint.app that is dependent on app.py, update .pylint.app when done
.pylint.%: %.py
	pylint $(PYLINTFLAGS) $*.py | tee .pylint.$*


.PHONY: clean
clean:
	@echo Removing sqlite files from worksheets and worksheets/databases directory
	@rm -f $(aux_files)

wkst.university1.json wkst.university1.sqlite wkst.university2.sqlite: wkst.university.py
	@echo
	@echo Making $@
	./wkst.university.py

../../../wkst.university1.json ../../../static/dbs/wkst.university1.sqlite ../../../static/dbs/wkst.university2.sqlite: wkst.university1.sqlite wkst.university2.sqlite
	@echo
	@echo Copying $@ to static dbs
	touch $(shell find ../.. -name \*tmd | xargs grep -l wkst.university )
	cp wkst.university1.sqlite wkst.university2.sqlite ../../../static/dbs
	cp wkst.university1.json ../../../

worksheet-03.sqlite: worksheet-03.py
	@echo 
	@echo Making worksheet/database/$@
	./worksheet-03.py
	cp $@ ../../../static/dbs
	touch ../worksheet-03-A.tmd ../worksheet-03-B.tmd


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
	./CreateSailorsWithoutPrimaryKey.py
	cp sailorsA.sqlite ../../../static/dbs 
	cp sailorsA.sqlite ..
	cp sailorsA.json ../../..
	touch ../*tmd


wkst-ch5-sailors-2.sqlite wkst-ch5-sailors-1.sqlite: wkst-ch5-sailors.py
	@echo 
	@echo Making worksheet/database/$@
	./wkst-ch5-sailors.py
	cp wkst-ch5-sailors-1.sqlite wkst-ch5-sailors-2.sqlite ../../../static/dbs
	cp wkst-ch5-sailors-2.json ../../..
	touch ../worksheet-chapter-05-1-to-5-3.tmd*tmd

sailors.sqlite: CreateData.py
	@echo 
	@echo Making worksheet/database/$@
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


wkst.large.university1.json wkst.large.university1.sqlite wkst.large.university2.sqlite: wkst.large.university.py
	@echo
	@echo Making $@
	./wkst.large.university.py

../../../wkst.large.university1.json ../../../static/dbs/wkst.large.university1.sqlite ../../../static/dbs/wkst.large.university2.sqlite: wkst.large.university1.sqlite wkst.large.university2.sqlite
	@echo
	@echo Copying $@ to static dbs
	touch $(shell find ../.. -name \*tmd | xargs grep -l wkst.large.university )
	cp wkst.large.university1.sqlite wkst.large.university2.sqlite ../../../static/dbs
	cp wkst.large.university1.json ../../../


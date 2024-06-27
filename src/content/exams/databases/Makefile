all: pylint \
	../../../m1-dance-copy-agree-91.1.json \
	../../../static/dbs/m1-dance-copy-agree-91.1.sqlite ../../../static/dbs/m1-dance-copy-agree-91.2.sqlite \
     ../../../static/dbs/m1.university2.sqlite \
     m1.university1.sqlite m1.university1.json m1.university2.sqlite

PYLINTFLAGS = -rn
PYLINTFILES := $(wildcard *.py)

.PHONY: clean
clean:
	@echo Removing sqlite files from worksheets and worksheets/databases directory
	@rm -f *.sqlite
	@rm -f ../football*.sqlite

# Create a target pylint that is dependent on .pylint.app, .pylint.appgames, etc
pylint: $(patsubst %.py,.pylint.%,$(PYLINTFILES))

# Create a target .pylint.app that is dependent on app.py, update .pylint.app when done
.pylint.%: %.py
	pylint $(PYLINTFLAGS) $*.py | tee .pylint.$*


fe.university1.json fe.university1.sqlite fe.university2.sqlite: fe.university.py
	@echo
	@echo Making $@
	./fe.university.py

m2.university1.json m2.university1.sqlite m2.university2.sqlite: m2.university.py
	@echo
	@echo Making $@
	./m2.university.py


m1.university1.json m1.university1.sqlite m1.university2.sqlite: m1.university.py
	@echo
	@echo Making $@
	./m1.university.py


m1-dance-copy-agree-91.1.json m1-dance-copy-agree-91.1.sqlite m1-dance-copy-agree-91.2.sqlite: m1-dance-copy-agree-91.py
	@echo
	@echo Making $@
	./m1-dance-copy-agree-91.py

../../../fe.university1.json ../../../static/dbs/fe.university1.sqlite ../../../static/dbs/fe.university2.sqlite: fe.university1.sqlite fe.university2.sqlite
	@echo
	@echo Copying $@ to static dbs
	touch ../fe-dry-tube-kept-91.tmd
	cp fe.university1.sqlite fe.university2.sqlite ../../../static/dbs
	cp fe.university1.json ../../../

../../../m2.university1.json ../../../static/dbs/m2.university1.sqlite ../../../static/dbs/m2.university2.sqlite: m2.university1.sqlite m2.university2.sqlite
	@echo
	@echo Copying $@ to static dbs
	touch ../m2-he-am-study-33.tmd
	cp m2.university1.sqlite m2.university2.sqlite ../../../static/dbs
	cp m2.university1.json ../../../


../../../m1-dance-copy-agree-91.1.json ../../../static/dbs/m1-dance-copy-agree-91.1.sqlite ../../../static/dbs/m1-dance-copy-agree-91.2.sqlite: m1-dance-copy-agree-91.1.sqlite m1-dance-copy-agree-91.2.sqlite
	@echo
	@echo Copying $@ to static dbs
	touch ../m1-dance-copy-agree-91.tmd
	cp m1-dance-copy-agree-91.1.sqlite m1-dance-copy-agree-91.2.sqlite ../../../static/dbs
	cp m1-dance-copy-agree-91.1.json ../../../

../../../m1.university1.json ../../../static/dbs/m1.university1.sqlite ../../../static/dbs/m1.university2.sqlite: m1.university1.sqlite m1.university2.sqlite
	@echo
	@echo Copying $@ to static dbs
	touch ../m1-just-material-might-50.tmd
	cp m1.university1.sqlite m1.university2.sqlite ../../../static/dbs
	cp m1.university1.json ../../../

fe-sailors-1.sqlite fe-sailors-2.sqlite fe-sailors-1.json: fe-sailors.py
	@echo 
	@echo Making $@
	-pylint -rn fe-sailors.py
	./fe-sailors.py

../../../static/dbs/fe-sailors-1.sqlite ../../../static/dbs/fe-sailors-2.sqlite: fe-sailors-1.sqlite fe-sailors-2.sqlite
	cp fe-sailors-1.sqlite fe-sailors-2.sqlite ../../../static/dbs
	cp fe-sailors-1.json ../../..
	touch ../fe-mothball-midwife-granite-27.tmd


football-1.sqlite football-2.sqlite: Football.py
	@echo 
	@echo Making $@
	-pylint -rn Football.py
	./Football.py

../../../static/dbs/football-1.sqlite ../../../static/dbs/football-2.sqlite: football-1.sqlite football-2.sqlite
	@echo
	@echo Copying out $@
	cp football-1.sqlite football-2.sqlite ../../../static/dbs
	cp football-1.sqlite football-2.sqlite football-1.json ../
	cp football-1.json ../../../
	touch ../m1-body-group-it-70.tmd

fe-nc-legislature-1.sqlite fe-nc-legislature-2.sqlite: fe-nc-legislature.py
	@echo
	@echo Making $@
	-pylint -rn fe-nc-legislature.py
	./fe-nc-legislature.py

../../../static/dbs/fe-nc-legislature-1.sqlite ../../../static/dbs/fe-nc-legislature-2.sqlite: fe-nc-legislature-1.sqlite fe-nc-legislature-2.sqlite
	@echo
	@echo Copying $@ to static dbs
	cp fe-nc-legislature-1.sqlite fe-nc-legislature-2.sqlite ../../../static/dbs
	cp fe-nc-legislature-1.json ../../../
	touch ../fe-mothball-midwife-granite-27.tmd

fe_politicians1.sqlite fe_politicians2.sqlite fe_politicians1.json: Politicians.py
	@echo 
	@echo Making $@
	-pylint -rn Politicians.py
	./Politicians.py
	cp fe_politicians1.sqlite fe_politicians2.sqlite ../../../static/dbs
	cp fe_politicians1.json ../../..
	touch ../fe-root-necessary-serve-61.tmd

midterm2-nc-legislature-1.sqlite midterm2-nc-legislature-2.sqlite: NCLegislature.py
	@echo
	@echo Making $@
	-pylint -rn NCLegislature.py
	./NCLegislature.py

../../../static/dbs/midterm2-nc-legislature-1.sqlite ../../../static/dbs/midterm2-nc-legislature-2.sqlite: midterm2-nc-legislature-1.sqlite midterm2-nc-legislature-2.sqlite
	@echo
	@echo Copying $@ to static dbs
	cp midterm2-nc-legislature-1.sqlite midterm2-nc-legislature-2.sqlite ../../../static/dbs
	cp midterm2-nc-legislature-1.json ../../../
	touch ../m2-equate-paint-shoulder-30.tmd


midterm1-basketball-1.sqlite midterm1-basketball-2.sqlite: Basketball.py
	@echo
	@echo Making $@
	-pylint -rn Basketball.py
	./Basketball.py

../../../static/dbs/midterm1-basketball-1.sqlite ../../../static/dbs/midterm1-basketball-2.sqlite: midterm1-basketball-1.sqlite midterm1-basketball-2.sqlite
	@echo
	@echo Copying basketball to $@
	cp midterm1-basketball-1.sqlite midterm1-basketball-2.sqlite ../../../static/dbs
	touch ../../worksheets/worksheet-midterm-1.tmd ../m1-farm-example-scale-34.tmd

fe_sailors1.sqlite fe_sailors2.sqlite fe_sailors1.json: Sailors.py
	@echo 
	@echo Making $@
	-pylint -rn Sailors.py
	./Sailors.py
	cp fe_sailors1.sqlite fe_sailors2.sqlite ../../../static/dbs
	cp fe_sailors1.json ../../..
	touch ../fe-root-necessary-serve-61.tmd
	touch ../../worksheets/worksheet-13-C-boats.tmd

ex_movies-1.sqlite ex_movies-2.sqlite: Movies.py
	@echo 
	@echo Making $@
	@echo -pylint -rn Movies.py
	rm -rf title.ratings.tsv name.basics.tsv title.principals.tsv title.basics.tsv
	ln -s ../../../../../assignments/A4/title.ratings.tsv 
	ln -s ../../../../../assignments/A4/name.basics.tsv 
	ln -s ../../../../../assignments/A4/title.principals.tsv
	ln -s ../../../../../assignments/A4/title.basics.tsv
	./Movies.py
	cp ex_movies-1.sqlite ex_movies-2.sqlite ../../../static/dbs
	cp ex_movies-1.sqlite ex_movies-2.sqlite ex_movies.json ../
	cp ex_movies.json ../../../
	touch ../m2-store-cloudy-yogurt-26.tmd ../../worksheets/worksheet-12-C-query-plan.tmd


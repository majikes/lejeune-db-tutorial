all: fe_sailors1.sqlite fe_sailors2.sqlite ../../../static/dbs/midterm1-basketball-1.sqlite ../../../static/dbs/midterm1-basketball-2.sqlite ../../../static/dbs/midterm2-nc-legislature-1.sqlite ../../../static/dbs/midterm2-nc-legislature-2.sqlite ../../../static/dbs/fe-nc-legislature-1.sqlite ../../../static/dbs/fe-nc-legislature-2.sqlite ../../../static/dbs/fe-sailors-1.sqlite ../../../static/dbs/fe-sailors-2.sqlite

.PHONY: clean
clean:
	@echo Removing sqlite files from worksheets and worksheets/databases directory
	@rm -f *.sqlite
	@rm -f ../football*.sqlite

fe-sailors-1.sqlite fe-sailors-2.sqlite fe-sailors-1.json: fe-sailors.py
	@echo 
	@echo Making $@
	-pylint -rn fe-sailors.py
	./fe-sailors.py

../../../static/dbs/fe-sailors-1.sqlite ../../../static/dbs/fe-sailors-2.sqlite: fe-sailors-1.sqlite fe-sailors-2.sqlite
	cp fe-sailors-1.sqlite fe-sailors-2.sqlite ../../../static/dbs
	cp fe-sailors-1.json ../../..
	touch ../fe-mothball-midwife-granite-27.tmd

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

football-1.sqlite football-2.sqlite: Football.py
	@echo 
	@echo Making $@
	-pylint -rn Football.py
	./Football.py
	cp football-1.sqlite football-2.sqlite ../../../static/dbs
	cp football-1.sqlite football-2.sqlite football-1.json ../
	cp football-1.json ../../../
	touch ../m1-body-group-it-70.tmd

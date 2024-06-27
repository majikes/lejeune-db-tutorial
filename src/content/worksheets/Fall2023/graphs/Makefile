all: ../../../static/images/worksheet-14-01-dense.png ../../../static/images/worksheet-14-02-dense-dept_name.png \
	../../../static/images/worksheet-14-04-before-insert.png \
	../../../static/slides/chapter-6-car-insurance-company.png \
	../../../static/images/worksheet-14-04-after-insert.png
	@echo Making worksheets/graphs


.PHONY: clean
clean:
	@echo Removing png files from worksheets/graphs
	rm -f *.png


%.png:%.dot
	@echo 
	@echo Making worksheets/graphs/$@
	dot -Tpng -s $*.dot -o $*.png

# Copying png to static images and touch the worksheets
../../../static/images/worksheet-14-01-dense.png:worksheet-14-01-dense.png
	cp $(@F)  $@
	touch $(shell find ../.. -name \*tmd | xargs grep -l $(@F)) .gitignore

# Copying png to static images and touch the worksheets
../../../static/images/worksheet-14-02-dense-dept_name.png:worksheet-14-02-dense-dept_name.png
	cp $(@F)  $@
	touch $(shell find ../.. -name \*tmd | xargs grep -l $(@F)) .gitignore

# Copying png to static images and touch the worksheets
../../../static/images/worksheet-14-04-before-insert.png:worksheet-14-04-before-insert.png
	cp $(@F)  $@
	touch $(shell find ../.. -name \*tmd | xargs grep -l $(@F)) .gitignore

# Copying png to static images and touch the worksheets
../../../static/images/worksheet-14-04-after-insert.png:worksheet-14-04-after-insert.png
	cp $(@F)  $@
	touch $(shell find ../.. -name \*tmd | xargs grep -l $(@F)) .gitignore

# Copying png to static images and touch the worksheets
../../../static/slides/chapter-6-car-insurance-company.png: chapter-6-car-insurance-company.png
	cp $(@F)  $@
	touch $(shell find ../.. -name \*tmd | xargs grep -l $(@F)) .gitignore

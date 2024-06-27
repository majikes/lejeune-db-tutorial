# WARNING:
#  Updating .env file will cause it to get copied over to /var/www/mypoll
#  But UWSGI will not recognize the change until a `sudo systemctl restart uwsgi`
all: ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-classroom.0.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-classroom.1.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-classroom.2.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-classroom.3.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-pre-insert.0.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-post-insert.0.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-pre-insert.1.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-post-insert.1.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-pre-insert.2.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-post-insert.2.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-pre-insert.3.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-post-insert.3.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-delete.0.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-delete.1.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-delete.2.png \
     ../../../static/slides/fe-dry-tube-kept-92.b-plus-tree-delete.3.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-classroom.0.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-classroom.1.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-classroom.2.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-classroom.3.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-pre-insert.0.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-post-insert.0.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-pre-insert.1.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-post-insert.1.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-pre-insert.2.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-post-insert.2.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-pre-insert.3.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-post-insert.3.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-delete.0.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-delete.1.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-delete.2.png \
     ../../../static/slides/m2-he-am-study.b-plus-tree-delete.3.png
	@echo Making exams/graphs

.PHONY: clean
clean:
	@echo Removing png files from exams/graphs/
	rm -f *png

# Create a target .pylint.app that is dependent on app.py, update .pylint.app when done
%.png:%.dot
	@echo
	@echo Making $@
	dot -Tpng -s $*.dot -o $*.png

../../../static/slides/%.png: %.png
	@echo 
	@echo Copy to $@
	cp $< ../../../static/slides
	touch ../fe-dry-tube-kept-92.tmd

../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.%.png:m2-equate-paint-shoulder-30.valid-b-tree.%.png
	@echo
	@echo Copying to $@
	cp m2-equate-paint-shoulder-30.valid-b-tree.$*.png ../../../static/images/
	touch ../m2-equate-paint-shoulder-30.b_tree.itmd

../../../static/images/m2-equate-paint-shoulder-30.b_tree.png:m2-equate-paint-shoulder-30.b_tree.png
	@echo
	@echo Copying to $@
	cp m2-equate-paint-shoulder-30.b_tree.png ../../../static/images/
	touch ../$*.itmd

../../../static/slides/m2-he-am-study.b-plus-tree-classroom.0.png: m2-he-am-study.b-plus-tree-classroom.0.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-classroom)

../../../static/slides/m2-he-am-study.b-plus-tree-classroom.1.png: m2-he-am-study.b-plus-tree-classroom.1.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-classroom)

../../../static/slides/m2-he-am-study.b-plus-tree-classroom.2.png: m2-he-am-study.b-plus-tree-classroom.2.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-classroom)

../../../static/slides/m2-he-am-study.b-plus-tree-classroom.3.png: m2-he-am-study.b-plus-tree-classroom.3.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-classroom)

../../../static/slides/m2-he-am-study.b-plus-tree-pre-insert.0.png: m2-he-am-study.b-plus-tree-pre-insert.0.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-insert) .gitignore

../../../static/slides/m2-he-am-study.b-plus-tree-pre-insert.1.png: m2-he-am-study.b-plus-tree-pre-insert.1.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-insert) .gitignore


../../../static/slides/m2-he-am-study.b-plus-tree-pre-insert.2.png: m2-he-am-study.b-plus-tree-pre-insert.2.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-insert) .gitignore

../../../static/slides/m2-he-am-study.b-plus-tree-pre-insert.3.png: m2-he-am-study.b-plus-tree-pre-insert.3.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-insert) .gitignore

../../../static/slides/m2-he-am-study.b-plus-tree-post-insert.0.png: m2-he-am-study.b-plus-tree-post-insert.0.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-insert) .gitignore

../../../static/slides/m2-he-am-study.b-plus-tree-post-insert.1.png: m2-he-am-study.b-plus-tree-post-insert.1.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-insert) .gitignore

../../../static/slides/m2-he-am-study.b-plus-tree-post-insert.2.png: m2-he-am-study.b-plus-tree-post-insert.2.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-insert) .gitignore

../../../static/slides/m2-he-am-study.b-plus-tree-post-insert.3.png: m2-he-am-study.b-plus-tree-post-insert.3.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-insert) .gitignore

../../../static/slides/m2-he-am-study.b-plus-tree-delete.0.png: m2-he-am-study.b-plus-tree-delete.0.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-insert) .gitignore

../../../static/slides/m2-he-am-study.b-plus-tree-delete.1.png: m2-he-am-study.b-plus-tree-delete.1.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-insert) .gitignore


../../../static/slides/m2-he-am-study.b-plus-tree-delete.2.png: m2-he-am-study.b-plus-tree-delete.2.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-insert) .gitignore


../../../static/slides/m2-he-am-study.b-plus-tree-delete.3.png: m2-he-am-study.b-plus-tree-delete.3.png
	@echo
	@echo Copying to $@
	cp $(shell basename $@)  ../../../static/slides/
	touch $(shell find ../.. -name \*tmd | xargs grep -l m2-he-am-study.b-plus-tree-insert) .gitignore


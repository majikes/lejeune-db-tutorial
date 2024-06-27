all: deploy

PYLINTFLAGS = -rn
PYLINTFILES := $(wildcard *.py) 

# Create a target pylint that is dependent on .pylint.app, .pylint.appgames, etc
pylint: $(patsubst %.py,.pylint.%,$(PYLINTFILES))

# Create a target .pylint.app that is dependent on app.py, update .pylint.app when done
.pylint.%: %.py
	pylint $(PYLINTFLAGS) $*.py | tee .pylint.$*

.PHONY: clean
clean:
	rm -f *.png *.dot .pylint*

%.dot: %.yml btree.py
	@echo
	@echo Invoke btree generator against $<
	./btree.py -y $< -o $@

%.png: %.dot
	@echo
	@echo Invoke Graphiz dot against $<
	dot -Tpng $< > $@

../static/slides/%.png: %.png
	@echo
	@echo Copy $< to $@ to https://comp421.cs.unc.edu/static/slides/$<
	cp $< $@

deploy: pylint ../static/slides/chapter10-example.png \
	chapter10-example.png \
	../static/slides/Figure.14.14.Insertion.of.Adams.png \
	Figure.14.14.Insertion.of.Adams.png \
	../static/slides/Figure.14.9.Bplus.tree.for.instructor.png \
	Figure.14.9.Bplus.tree.for.instructor.png
	(cd ..; $(MAKE))

# WARNING:
#  Updating .env file will cause it to get copied over to /var/www/mypoll
#  But UWSGI will not recognize the change until a `sudo systemctl restart uwsgi`
all: ../../../static/images/worksheet-10-A-ISAM.tree.png ../../../static/images/worksheet-10-B-Btree.png

.PHONY: clean
clean:
	@echo Removing png files from worksheets/graphs/
	rm -f *png

GRAPHVISFILES := $(wildcard *.yml)

# Create a target graphvis that is dependent on .graphvis.app, .graphvis.appgames, etc
graphvis: $(patsubst %.yml,%.png,$(GRAPHVISFILES))

# Create a target .pylint.app that is dependent on app.py, update .pylint.app when done
%.dot:%.yml
	@echo
	@echo Making $@
	./btree.py $*.yml > $*.dot

%.png:%.dot
	@echo
	@echo Makeing $@
	dot -Tpng -s $*.dot -o $*.png

../../../static/images/worksheet-10-A-ISAM.tree.png:worksheet-10-A-ISAM.tree.png
	@echo
	@echo Copying $@ to static/images
	cp $*.png ../../../static/images/
	touch ../worksheet-10-A-ISAM.tmd

../../../static/images/worksheet-10-B-Btree.png:worksheet-10-B-Btree.png
	@echo
	@echo Copying $@ to static/images
	cp $< ../../../static/images/
	touch ../worksheet-10-B-Btree.tmd


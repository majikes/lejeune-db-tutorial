# WARNING:
#  Updating .env file will cause it to get copied over to /var/www/mypoll
#  But UWSGI will not recognize the change until a `sudo systemctl restart uwsgi`
all: ../../../static/images/m2-equate-paint-shoulder-30.b_tree.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.1.1.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.1.2.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.1.3.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.1.4.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.2.1.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.2.2.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.2.3.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.2.4.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.3.1.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.3.2.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.3.3.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.3.4.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.4.1.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.4.2.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.4.3.png ../../../static/images/m2-equate-paint-shoulder-30.valid-b-tree.4.4.png

old_all: m2-store-cloudy-yogurt-26.b_tree.insert.1.png m2-store-cloudy-yogurt-26.b_tree.insert.2.png m2-store-cloudy-yogurt-26.b_tree.insert.3.png m2-store-cloudy-yogurt-26.b_tree.insert.4.png  m2-store-cloudy-yogurt-26.b_tree.insert.var.png m2-store-cloudy-yogurt-26.b_tree.max.min.1.png m2-store-cloudy-yogurt-26.b_tree.max.min.2.png m2-store-cloudy-yogurt-26.b_tree.max.min.3.png m2-store-cloudy-yogurt-26.b_tree.max.min.4.png fe-root-necessary-serve-61.insert.1.png fe-root-necessary-serve-61.insert.2.png fe-root-necessary-serve-61.insert.3.png fe-root-necessary-serve-61.insert.4.png fe-root-necessary-serve-61.insert.var.png


.PHONY: clean
clean:
	@echo Removing png files from exams/graphs/
	rm -f *png

# Create a target .pylint.app that is dependent on app.py, update .pylint.app when done
%.png:%.dot
	@echo
	@echo Making $@
	dot -Tpng -s $*.dot -o $*.png

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

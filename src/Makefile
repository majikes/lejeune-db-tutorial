# WARNING:
#  Updating .env file will cause it to get copied over to /var/www/mypoll
#  But UWSGI will not recognize the change until a `sudo systemctl restart uwsgi`
all: deploy

PYLINTFLAGS = -rn
PYLINTFILES := $(wildcard app*.py) grade.py assessments.py regrade.py agenda.py db.py updateRubrics.py get_email.py

STUFF = *.ico *.py .env tools static views md-includes images content vendor visualization *.json

dev: pylint
	npm run build
	(cd content/worksheets/databases; $(MAKE))
	python3 updateRubrics.py
	python3 app.py

# Create a target pylint that is dependent on .pylint.app, .pylint.appgames, etc
pylint: $(patsubst %.py,.pylint.%,$(PYLINTFILES))

# Create a target .pylint.app that is dependent on app.py, update .pylint.app when done
.pylint.%: %.py
	pylint $(PYLINTFLAGS) $*.py | tee .pylint.$*

deploy: pylint
	# # minify static/js/mypoll.js static/js/monitorloading.js --output /tmp/
	npm run build
	(cd content/worksheets/databases; $(MAKE))
	rsync -a --delete $(STUFF) /var/www/lejeune/
	# # not needed rsync /tmp/static/js/mypoll.* /var/www/mypoll/static/js/
	# -timeout --preserve-status 3s npm run watch ; echo "" 
	python3 updateRubrics.py
	touch /tmp/lejeune.reload
	touch /tmp/lejeune2.reload

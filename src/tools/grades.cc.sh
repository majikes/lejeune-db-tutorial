#! /bin/bash

psql -c "\copy (select pid, name, G.lettergrade from roll R, grades G where R.onyen=G.onyen and section='001' and name not like '%tudent%')
	  to 'grades.001.csv' CSV HEADER " mypoll


#! /bin/bash

tables=( "grades" "roll" "worksheet_bonus" "assessments" )
for table in "${tables[@]}"
do
   psql -c "\copy (SELECT * FROM ${table} order by onyen) TO '${table}.csv' with csv header delimiter ',' " mypoll
done

echo Only get feedback from exams
psql -c "\copy (select onyen, P.key, score, points_total, cast(1000*score/points_total as integer)/10::float as percentage, msg 
                     from feedback F, post P, Rubrics R
                       where P.post_id=F.post_id AND
                             P.key=R.key AND
                             R.assessment_type in ('midterm1', 'midterm2', 'fe')
                             order by onyen asc, P.key ASC, P.time ASC, P.post_id ASC) TO 'exams.csv' with csv header delimiter ',' " mypoll

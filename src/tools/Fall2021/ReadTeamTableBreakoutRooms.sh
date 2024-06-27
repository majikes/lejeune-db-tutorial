#! /bin/bash

psql -c "\copy (SELECT team_number, T.onyen
                  FROM teams T, roll R
                  WHERE T.onyen = R.onyen 
                    and section='001'
                  ORDER BY team_number, member_number
                  ) to '001.csv' with csv header delimiter ',' " mypoll

psql -c "\copy (SELECT team_number, T.onyen
                  FROM teams T, roll R
                  WHERE T.onyen = R.onyen 
                    and section='002'
                  ORDER BY team_number, member_number
                  ) to '002.csv' with csv header delimiter ',' " mypoll


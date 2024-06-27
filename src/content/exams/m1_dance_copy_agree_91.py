
points_joins = 0
number_joins = 4

points_sql_queries_chapter_2 = 5
points_sql_queries_chapter_3 = 17.5
points_sql_queries_chapter_4 = 0
points_sql_queries = points_sql_queries_chapter_2 + points_sql_queries_chapter_3 + points_sql_queries_chapter_4
number_sql_queries = 4

points_chapter_1_review = 5
points_chapter_2_review = 15
number_chapter_review = 4
points_chapter_review = points_chapter_1_review + points_chapter_2_review

points_limit = points_sql_queries + points_chapter_review + points_joins
points_total = points_sql_queries * number_sql_queries + points_chapter_review * number_chapter_review + points_joins * number_joins

duration = 80
exam = True
exam = False
exceptions = dict()
maxpenalty  =  0.75
penalty  =  0.20

dbs = ['m1-dance-copy-agree-91.1.sqlite', 'm1-dance-copy-agree-91.2.sqlite']

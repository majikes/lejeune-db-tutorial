
points_joins = 20
number_joins = 4

points_sql_queries_chapter_2 = 25
points_sql_queries_chapter_3 = 30
points_sql_queries_chapter_4 = 10
points_sql_queries = points_sql_queries_chapter_2 + points_sql_queries_chapter_3 + points_sql_queries_chapter_4
number_sql_queries = 4

points_chapter_1_review = 10
points_chapter_2_review = 5
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

dbs = ['m1.university1.sqlite', 'm1.university2.sqlite']

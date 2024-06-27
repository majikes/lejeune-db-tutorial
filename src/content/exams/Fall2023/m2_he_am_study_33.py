
points_joins = 20
points_joins = 0
number_joins = 4

points_sql_queries_chapter_2 = 5
points_sql_queries_chapter_3 = 5
points_sql_queries_chapter_4 = 25
points_sql_queries = points_sql_queries_chapter_2 + points_sql_queries_chapter_3 + points_sql_queries_chapter_4
number_sql_queries = 4

points_chapter_1_review = 0
points_chapter_2_review = 0
points_chapter_14_review = 15
number_chapter_review = 4
points_chapter_review = points_chapter_1_review + points_chapter_2_review + points_chapter_14_review

points_b_plus_trees_general = 50
points_b_plus_trees = points_b_plus_trees_general
number_b_plus_trees = 4

points_limit = points_sql_queries + points_chapter_review + points_joins + points_b_plus_trees
points_limit = points_b_plus_trees + points_sql_queries + points_chapter_review
points_total = points_sql_queries * number_sql_queries + points_chapter_review * number_chapter_review + points_joins * number_joins + points_b_plus_trees * number_b_plus_trees

duration = 80
exam = False
exceptions = dict()
maxpenalty  =  0.75
penalty  =  0.20

dbs = ['m2.university1.sqlite', 'm2.university2.sqlite']

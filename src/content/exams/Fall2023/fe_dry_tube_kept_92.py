
points_joins = 20
points_joins = 0
number_joins = 4

points_sql_queries =  60
number_sql_queries = 4

points_chapter_1_review = 0
points_chapter_2_review = 0
points_chapter_14_review = 0
number_chapter_review = 4
points_chapter_review = points_chapter_1_review + points_chapter_2_review + points_chapter_14_review

points_b_plus_trees_general = 30
points_b_plus_trees = points_b_plus_trees_general
number_b_plus_trees = 4

points_query_processing = 20
number_query_processing = 4

points_limit = points_b_plus_trees + points_sql_queries + points_chapter_review + points_query_processing
points_total = points_sql_queries * number_sql_queries + points_chapter_review * number_chapter_review + points_joins * number_joins + points_b_plus_trees * number_b_plus_trees + points_query_processing * number_query_processing

assert points_total // number_b_plus_trees == points_total / number_b_plus_trees, f'points_total {points_total} number_b_plus_trees {number_b_plus_trees}'
points_max = points_total // number_b_plus_trees
points_limit = min(100, points_limit)

duration = 180
exam = True
exceptions = dict()
maxpenalty  =  0.75
penalty  =  0.20

dbs = ['fe.university1.sqlite', 'fe.university2.sqlite']

points_b_tree = 10
number_b_tree = 4
name_b_tree = 'B+ Trees'

points_sql_queries = 65
number_sql_queries = 4
name_sql_queries = 'SQL Queries'

points_evaluation = 35
number_evaluation = 4
name_evaluation = 'I/O Evaluations'

points_counting = 5
number_counting = number_evaluation
name_counting = 'Counting Relations'

points_sorting = 10
number_sorting = number_evaluation
name_sorting = 'Two way sort and external sort'

points_block_nested_loop = 10
number_block_nested_loop = number_evaluation
name_block_nested_loop = 'Block Nested Loop Joins'

points_index_nested_loop = 10
number_index_nested_loop = number_evaluation
name_index_nested_loop = 'Index Nested Loop Joins'


points_limit = points_b_tree + points_sql_queries + points_evaluation
points_total = points_b_tree * number_b_tree + points_sql_queries * number_sql_queries + points_evaluation * number_evaluation

duration = 185
due  =  '2022-12-06 19:10:00'
exam = True
needsSubmitCode = True
exceptions = dict(_003=dict(due='2022-12-01 00:00:00', needsSubmitCode=False),
                  wlan=dict(due='2022-12-06 19:40:00', duration=275),
                  ira01=dict(due='2022-12-06 19:40:00', duration=275),
                  andrew98=dict(due='2022-12-06 19:40:00', duration=275),
                  jdavis19=dict(due='2022-12-09 14:00:00', duration=275),
                  cjconnor=dict(due='2022-12-09 15:05:00'),
                  khan7=dict(due='2022-12-09 15:05:00'),
                  jiayify=dict(due='2022-12-09 15:05:00'),
                  ssofia=dict(due='2022-12-05 14:10:00'),
                  student1=dict(needsSubmitCode=False),
                  student2=dict(needsSubmitCode=False),
                  student3=dict(needsSubmitCode=False),
                  student4=dict(needsSubmitCode=False),
                  student5=dict(due='2022-12-09 15:05:00', needsSubmitCode=False),
                  )
possible_pages  =  ['questions', 'submit']
maxpenalty  =  0.75
penalty  =  0.20

sailors_dbs = ['fe_sailors1.sqlite', 'fe_sailors2.sqlite']
politicians_dbs = ['fe_politicians1.sqlite', 'fe_politicians2.sqlite']

points_b_tree = 5
number_b_tree = 4

points_book_sql_queries = 70
number_book_sql_queries = 4

points_external_sort = 20
number_external_sort = 4

points_evaluation = 15
number_evaluation = 4

points_limit = points_b_tree + points_book_sql_queries + points_external_sort + points_evaluation
points_limit = min(100, points_limit)
points_total = points_b_tree * number_b_tree + points_book_sql_queries * number_book_sql_queries + points_external_sort * number_external_sort + number_evaluation * points_evaluation

duration = 185
due  =  '2022-01-27 16:00:00'
exam = True
needsSubmitCode = True
exceptions = dict(simmi=dict(due='2021-12-07 16:10:00', duration=275),
                  makeda=dict(due='2021-12-07 16:10:00', duration=275),
                  lmohamm0=dict(due='2021-12-09 00:00:00', duration=9999),
                  gcaron=dict(due='2021-12-07 16:10:00', duration=275),
                  rebeccca=dict(due='2021-12-07 16:10:00', duration=275, needsSubmitCode=False),
                  jmajikes=dict(due='2021-12-07 17:43:00', duration=280000, needsSubmitCode=False),
                  gksrb32=dict(duration=185, due='2021-12-07 10:00:00', needsSubmitCode=False),
                  mapy=dict(duration=280000, due='2021-12-07 00:00:00', needsSubmitCode=False),
                  tanying=dict(duration=280000, due='2021-12-07 00:00:00', needsSubmitCode=False),
                  yiwk321=dict(duration=280000, due='2021-12-07 00:00:00', needsSubmitCode=False),
                  )
possible_pages  =  ['questions', 'submit']
maxpenalty  =  0.75
penalty  =  0.20

state_dbs = ['states-A.sqlite', 'states-B.sqlite']
book_dbs = ['books1.sqlite', 'books2.sqlite']
sailor_dbs = ['sailors1.sqlite', 'sailors.sqlite']

state_schema = '''
CREATE TABLE IF NOT EXISTS States
           (abbrev char(2) PRIMARY KEY,
            statename char(20),  -- May include territories
            population integer)

CREATE TABLE IF NOT EXISTS Politicians
           (bioid char(20),
            firstname char(20),
            lastname char(20),
            birthday date, -- YYYY-MM-DD format string
            gender char(1),
            PRIMARY KEY(bioid))

CREATE TABLE IF NOT EXISTS Terms
   (termid INTEGER PRIMARY KEY AUTOINCREMENT,
    termtype char(20), -- Type of term elected; rep, sen, prez, viceprez
    startdate date,
    enddate date,
    party char(20), -- Political party affiliation
    how char(20),  -- Different ways to get into an office
    bioid char(20),
    -- Presidents & vice president aren't elected from districts or states
    -- Senators aren't elected from districts
    district integer,  -- Null for prez, viceprez, or sen
    state char(2),     -- Null for prez and viceprez
    FOREIGN KEY(bioid) REFERENCES Politicians(bioid))
'''
book_schema = f'''
CREATE TABLE Authors (
   login text primary key,
   email text,
   first_name text,
   last_name text
)

CREATE TABLE Books (
   id integer primary key autoincrement,
   title text,
   author text references authors(login),
   language text,
   created date
)

CREATE TABLE Photos (
   id integer primary key autoincrement,
   url text unique,
   width integer,
   height integer
)

CREATE TABLE Pages (
   book integer references books(id),
   number integer,
   photo integer references photos(id),
   caption text,
   primary key (book, number)
)

CREATE TABLE Categories (
   category text,
   book integer references books(id),
   unique (book, category)
)

CREATE VIEW PageCounts as
   select book, count(*) as count from pages group by book
'''

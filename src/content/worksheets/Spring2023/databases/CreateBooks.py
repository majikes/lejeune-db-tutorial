#!/usr/bin/env python


import sqlite3
import json

db1_fname = 'books1.sqlite'
db2_fname = 'books2.sqlite'

json_fname = 'books.json'

conns = []
cursors = []
for db_fname in [db1_fname, db2_fname]:
   conns.append(sqlite3.connect(db_fname))
   cursors.append(conns[-1].cursor())

# Write code here to create the tables
# use the db variable from above
for cursor in cursors:
   cursor.execute('''drop table if exists authors''')
   cursor.execute('''
      create table authors (
          login text primary key,
          email text,
          first_name text,
          last_name text    
      )
   ''')
   cursor.execute('''drop table if exists books''')
   cursor.execute('''
      create table books (
          id integer primary key autoincrement,
          title text,
          author text references authors(login),
          language text,
          created date
      )
   ''')
   cursor.execute('''drop table if exists photos''')
   cursor.execute('''
      create table photos (
          id integer primary key autoincrement,
          url text unique,
          width integer,
          height integer
      )
   ''')
   cursor.execute('''drop table if exists pages''')
   cursor.execute('''
      create table pages (
          book integer references books(id),
          number integer,
          photo integer references photos(id),
          caption text,
          primary key (book, number)
      )
   ''')

   cursor.execute('''drop table if exists categories''')
   cursor.execute('''
      create table categories (
          category text,
          book integer references books(id),
          unique (book, category)
      )
   ''')

   cursor.execute('''drop view if exists pagecounts''')
   cursor.execute('''
      create view pagecounts as
          select book, count(*) as count from pages group by book
   ''')




books = json.load(open(json_fname, encoding='UTF-8'))
for book in books:
    for cursor in cursors:
       # create author if necessary
       cursor.execute('SELECT login FROM Authors WHERE login = ?', [book['login']])
       r = cursor.fetchone()
       if not r:
           if cursor == cursors[0]:
              cursor.execute('SELECT COUNT(*) as count FROM Authors')
              count = cursor.fetchone()
              if count[0] > 9:
                  # Only allow 10 authors in the first book database
                  continue
              cursor.execute('SELECT COUNT(*) as count FROM Books WHERE language= ?', [book['language']])
              count = cursor.fetchone()
              if count[0] > 3:
                  # Only allow 3 books from one language in the first book database
                  continue
           cursor.execute('''
               insert into authors (login, email, first_name, last_name) values (?, ?, ?, ?)
           ''', [book['login'], book['email'], book['first_name'], book['last_name']])
       # add the book
       cursor.execute('''
           insert into books (title, author, language, created) values (?, ?, ?, ?)
       ''', [book['title'], book['login'], book['language'], book['created']])
       # get its id
       id = cursor.lastrowid
       # add the categories
       for category in book['categories']:
           cursor.execute('''
               insert into categories (category, book) values (?, ?)
           ''', [category, id])
       # insert the pages
       for i, page in enumerate(book['pages']):
           # check to see if we already have this photo
           r = cursor.execute('''select id from photos where url = ?''', [page['url']]).fetchone()
           if r:
               pid = r[0]
           else:
               # insert it
               cursor.execute('''
                   insert into photos (url, width, height) values (?, ?, ?)
               ''', [page['url'], page['width'], page['height']])
               pid = cursor.lastrowid
           # now I have the pid for this photo I can insert the page
           cursor.execute('''
               insert into pages (book, number, photo, caption) values (?, ?, ?, ?)
           ''', [id, i+1, pid, page['caption']])


# For final exam
# Ensure that Cuniculus verispellem salutat has 17 photos
cursors[0].execute(''' SELECT id FROM books where title='Cuniculus versipellem salutat' ''');
row = cursors[0].fetchone()
book_id = row[0]

cursors[0].execute(''' select max(photo) from pages where book=? ''', [book_id]);
row = cursors[0].fetchone()
photo_id = row[0]

cursors[0].execute(''' select max(number) from pages where book=? and photo=? ''', [book_id, photo_id]);
row = cursors[0].fetchone()
number_photos = row[0]

cursors[0].execute(''' SELECT MAX(C) FROM (SELECT COUNT(*) as C
                                            FROM Photos, Pages, Books
                                           WHERE Books.id=Pages.book AND
                                                 Photos.id=Pages.photo
                                           GROUP BY Pages.book)''')
row = cursors[0].fetchone()
max_number_photos = row[0]

# insert the pages
for i in range(number_photos, max_number_photos):
   cursors[0].execute('''INSERT INTO Pages (book, number, photo, caption) values (?, ?, ?, ?) ''',
                  [book_id, i+1, photo_id, f'John Majikes {i+1}'])


# For worksheet-fe-D
# Ensure there re 25 photos 500 x 375 and 500 x 333
cursors[0].execute('''UPDATE photos set height=333
                       WHERE url='/cache/images/06/357393306_bb325a5c92.jpg' AND
                             width=500 and height=332''')

# For final exam
# Ensure that My Favorite Things and Plurals: Canes, nomine Montius et Daisia have 5 categories
cursors[1].execute(''' SELECT id FROM books where title='My Favorite Things' ''');
row = cursors[1].fetchone()
book_id = row[0]
cursors[1].execute('''
   INSERT INTO categories (category, book) values ('John Majikes', ?)
           ''', [book_id])
cursors[1].execute('''
WITH C1 as (SELECT max(c) as max_count FROM (SELECT count(*) as c
                                             FROM categories
                                             GROUP BY book)),
C2 as (SELECT title, count(*) as cat_count
                FROM categories C, books B
               WHERE B.id=C.book
               GROUP BY book)
SELECT C2.title, C1.max_count
  FROM C1
    LEFT Join C2
      ON C1.max_count = C2.cat_count
''')
for row in cursors[1].fetchall():
    assert row[0] in ['My Favorite Things', 'Plurals: Canes, nomine Montius et Daisia']
    assert row[1] == 5

for conn in conns:
   conn.commit()

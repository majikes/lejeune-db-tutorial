#!/usr/bin/env python
'''Create the database for Database System Concepts by Silberschatz 7th edition'''

# pylint: disable=line-too-long, too-many-lines, invalid-name
import sqlite3


conn = sqlite3.connect("m1.joins.sqlite")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute('PRAGMA foreign_keys = ON')


# ORDER BY Null
cursor.execute("""DROP TABLE IF EXISTS AA""")
cursor.execute("""create table AA
                               (AA1 text,
                                AA2 integer)""")
cursor.execute("INSERT INTO AA (AA1, AA2) VALUES ('a', 1)")
cursor.execute("INSERT INTO AA (AA1, AA2) VALUES ('a', 9)")
cursor.execute("INSERT INTO AA (AA1     ) VALUES ('a')")
cursor.execute("INSERT INTO AA (AA1     ) VALUES ('z')")
cursor.execute("INSERT INTO AA (AA2     ) VALUES (1)")
cursor.execute("INSERT INTO AA (AA2     ) VALUES (2)")
cursor.execute('SELECT * FROM AA ORDER BY AA1, AA2')
print('SORT TABLE AA1, AA2')
for row in cursor.fetchall():
    print(*row)
cursor.execute('SELECT * FROM AA ORDER BY AA2, AA1')
print('SORT TABLE AA2, AA1')
for row in cursor.fetchall():
    print(*row)
print()

cursor.execute("""DROP TABLE IF EXISTS A""")
cursor.execute("""create table A
                               (A1 text not null,
                                A2 text not null,
                                A3 text not null,
                                A4 text not null)""")
cursor.execute("""DROP TABLE IF EXISTS B""")
cursor.execute("""create table B
                               (B1 text not null,
                                B2 text not null,
                                B3 text not null,
                                B4 text not null,
                                B5 text not null,
                                B6 text not null)""")
for x in range(3):
    cursor.execute("INSERT INTO A (A1, A2, A3, A4) VALUES (:a1, :a2, :a3, :a4)",
                   dict(a1=f'a1{x+1}', a2=f'a2{x+1}', a3=f'a3{x+1}', a4=f'a4{x+1}'))
for x in range(2):
    cursor.execute("INSERT INTO B (B1, B2, B3, B4, B5, B6) VALUES(:b1, :b2, :b3, :b4, :b5, :b6)",
                   dict(b1=f'b1{x+1}', b2=f'b2{x+1}', b3=f'b3{x+1}',
                        b4=f'a4{x+1}', b5=f'b5{x+1}', b6=f'b6{x+1}'))
print('Index 0')
print('Table A')
cursor.execute('SELECT * FROM A')
for row in cursor.fetchall():
    print(*row)


print('Table B')
cursor.execute('SELECT * FROM B')
for row in cursor.fetchall():
    print(*row)

query = '''
SELECT DISTINCT A2, B2, B5
 FROM A, B
ORDER BY A2, B2, B5'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)


query = '''
SELECT DISTINCT A2, B2, B5
 FROM A, B
WHERE A4 = B4 
ORDER BY A2, B2, B5'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)



query = '''
SELECT DISTINCT A2, B2, B5
 FROM A LEFT JOIN B
          ON A4 = B4 
ORDER BY A2, B2, B5'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)

query = '''
SELECT DISTINCT A2, B2, B5
 FROM A LEFT JOIN B
          ON A4 = B4 
UNION
SELECT DISTINCT A2, B2, B5
 FROM B LEFT JOIN A
          ON A4 = B4

ORDER BY A2, B2, B5'''
print('''SELECT DISTINCT A2, B2, B5
  FROM A FULL OUTER JOIN B
                ON A4 = B4
 ORDER BY A2, B2, B5''')
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)


###################################
# define tables
cursor.execute("""DROP TABLE IF EXISTS C""")
cursor.execute("""create table C
                               (C1 text not null,
                                C2 text not null,
                                C3 text not null,
                                C4 text not null,
                                C5 text not null,
                                C6 text not null)""")
cursor.execute("""DROP TABLE IF EXISTS D""")
cursor.execute("""create table D
                               (D1 text not null,
                                D2 text not null,
                                D3 text not null,
                                D4 text not null)""")
for x in range(3):
    cursor.execute("INSERT INTO C (C1, C2, C3, C4, C5, C6) VALUES (:c1, :c2, :c3, :c4, :c5, :c6)",
                   dict(c1=f'c1{x+1}', c2=f'c2{x+1}', c3=f'c3{x+1}',
                        c4=f'c4{x+1}', c5=f'c5{x+1}', c6=f'c6{x+1}'))
for x in range(2):
    cursor.execute("INSERT INTO D (D1, D2, D3, D4) VALUES(:d1, :d2, :d3, :d4)",
                   dict(d1=f'd1{x+1}', d2=f'd2{x+1}', d3=f'c3{x+1}', d4=f'd4{x+1}'))

print('Index 1')
print('Table C')
cursor.execute('SELECT * FROM C')
for row in cursor.fetchall():
    print(*row)


print('Table D')
cursor.execute('SELECT * FROM D')
for row in cursor.fetchall():
    print(*row)

query = '''
SELECT DISTINCT C4, D2, D4
 FROM C, D
ORDER BY C4, D2, D4'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)


query = '''
SELECT DISTINCT C4, D2, D4
 FROM C, D
WHERE C3 = D3
ORDER BY C4, D2, D4'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)



query = '''
SELECT DISTINCT C4, D2, D4
 FROM C LEFT JOIN D
          ON C3 = D3
ORDER BY C4, D2, D4'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)

query = '''
SELECT DISTINCT C4, D2, D4
 FROM C LEFT JOIN D
          ON C3 = D3
UNION
SELECT DISTINCT C4, D2, D4
 FROM D LEFT JOIN C
          ON C3 = D3
ORDER BY C4, D2, D4'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)



###################################
# define tables
cursor.execute("""DROP TABLE IF EXISTS E""")
cursor.execute("""create table E
                               (E1 text not null,
                                E2 text not null,
                                E3 text not null,
                                E4 text not null)""")
cursor.execute("""DROP TABLE IF EXISTS F""")
cursor.execute("""create table F
                               (F1 text not null,
                                F2 text not null,
                                F3 text not null,
                                F4 text not null,
                                F5 text not null,
                                F6 text not null)""")
for x in range(2):
    cursor.execute("INSERT INTO E (E1, E2, E3, E4) VALUES (:e1, :e2, :e3, :e4)",
                   dict(e1=f'e1{x+1}', e2=f'f2{x+1}', e3=f'e3{x+1}', e4=f'e4{x+1}'))
for x in range(3):
    cursor.execute("INSERT INTO F (F1, F2, F3, F4, F5, F6) VALUES(:f1, :f2, :f3, :f4, :f5, :f6)",
                   dict(f1=f'f1{x+1}', f2=f'f2{x+1}', f3=f'f3{x+1}',
                        f4=f'f4{x+1}', f5=f'f5{x+1}', f6=f'f6{x+1}'))

print()
print('Index 2')
print('Table E')
cursor.execute('SELECT * FROM E')
for row in cursor.fetchall():
    print(*row)


print('Table F')
cursor.execute('SELECT * FROM F')
for row in cursor.fetchall():
    print(*row)

query = '''
SELECT DISTINCT F1, F3, E3
 FROM F, E
ORDER BY F1, F3, E3'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)


query = '''
SELECT DISTINCT F1, F3, E3
 FROM F, E
WHERE E2 = F2
ORDER BY F1, F3, E3'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)



query = '''
SELECT DISTINCT F1, F3, E3
 FROM F LEFT JOIN E
          ON E2 = F2
ORDER BY F1, F3, E3'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)

query = '''
SELECT DISTINCT  F1, F3, E3
 FROM F LEFT JOIN E
          ON E2 = F2
UNION
SELECT DISTINCT F1, F3, E3
 FROM E LEFT JOIN F
          ON E2 = F2
ORDER BY F1, F3, E3'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)



###################################
# define tables
cursor.execute("""DROP TABLE IF EXISTS G""")
cursor.execute("""create table G
                               (G1 text not null,
                                G2 text not null,
                                G3 text not null,
                                G4 text not null,
                                G5 text not null,
                                G6 text not null)""")
cursor.execute("""DROP TABLE IF EXISTS H""")
cursor.execute("""create table H
                               (H1 text not null,
                                H2 text not null,
                                H3 text not null,
                                H4 text not null)""")
for x in range(2):
    cursor.execute("INSERT INTO G (G1, G2, G3, G4, G5, G6) VALUES (:g1, :g2, :g3, :g4, :g5, :g6)",
                   dict(g1=f'g1{x+1}', g2=f'h2{x+1}', g3=f'g3{x+1}', g4=f'g4{x+1}', g5=f'g5{x+1}', g6=f'g6{x+1}'))
for x in range(3):
    cursor.execute("INSERT INTO H (H1, H2, H3, H4) VALUES(:h1, :h2, :h3, :h4)",
                   dict(h1=f'h1{x+1}', h2=f'h2{x+1}', h3=f'h3{x+1}', h4=f'h4{x+1}'))
conn.commit()

print()
print('Index 2')
print('Table G')
cursor.execute('SELECT * FROM G')
for row in cursor.fetchall():
    print(*row)


print('Table H')
cursor.execute('SELECT * FROM H')
for row in cursor.fetchall():
    print(*row)

query = '''
SELECT DISTINCT H3, H4, G6
 FROM H, G
ORDER BY H3, H4, G6'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)


query = '''
SELECT DISTINCT H3, H4, G6
 FROM H, G
WHERE G2 = H2
ORDER BY H3, H4, G6'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)



query = '''
SELECT DISTINCT H3, H4, G6
 FROM H LEFT JOIN G
          ON G2 = H2
ORDER BY H3, H4, G6'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)

query = '''
SELECT DISTINCT H3, H4, G6
 FROM H LEFT JOIN G
          ON G2 = H2
UNION
SELECT DISTINCT H3, H4, G6
 FROM G LEFT JOIN H
          ON G2 = H2
ORDER BY H3, H4, G6'''
print(f'\n{query}')
cursor.execute(query)
for row in cursor.fetchall():
    print(*row)

#!/usr/bin/env python
'''Create the database for Database System Concepts by Silberschatz 7th edition'''

# pylint: disable=line-too-long
import json
import re
import sqlite3

DATABASE ='database.system.concepts.sqlite'
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()
cursor.execute('PRAGMA foreign_keys = ON')


# define tables
cursor.execute("""drop table if exists prereq""")
cursor.execute("""drop table if exists time_slot""")
cursor.execute("""drop table if exists advisor""")
cursor.execute("""drop table if exists takes""")
cursor.execute("""drop table if exists student""")
cursor.execute("""drop table if exists teaches""")
cursor.execute("""drop table if exists section""")
cursor.execute("""drop table if exists instructor""")
cursor.execute("""drop table if exists course""")
cursor.execute("""drop table if exists department""")
cursor.execute("""drop table if exists classroom""")

cursor.execute("""create table classroom
    	(building		varchar(15),
	 room_number		varchar(7),
	 capacity		numeric(4,0),
	 primary key (building, room_number)
	)""")

cursor.execute("""create table department
	(dept_name		varchar(20),
	 building		varchar(15),
	 budget		        numeric(12,2) check (budget > 0),
	 primary key (dept_name)
	)""")

cursor.execute("""create table course
	(course_id		varchar(8),
	 title			varchar(50),
	 dept_name		varchar(20),
	 credits		numeric(2,0) check (credits > 0),
	 primary key (course_id),
	 foreign key (dept_name) references department (dept_name)
		on delete set null
	)""")

cursor.execute("""create table instructor
	(ID			varchar(5),
	 name			varchar(20) not null,
	 dept_name		varchar(20),
	 salary			numeric(8,2) check (salary > 29000),
	 primary key (ID),
	 foreign key (dept_name) references department (dept_name)
		on delete set null
	)""")

cursor.execute("""create table section
	(course_id		varchar(8),
         sec_id			varchar(8),
	 semester		varchar(6)
		check (semester in ('Fall', 'Winter', 'Spring', 'Summer')),
	 year			numeric(4,0) check (year > 1701 and year < 2100),
	 building		varchar(15),
	 room_number		varchar(7),
	 time_slot_id		varchar(4),
	 primary key (course_id, sec_id, semester, year),
	 foreign key (course_id) references course (course_id)
		on delete cascade,
	 foreign key (building, room_number) references classroom (building, room_number)
		on delete set null
	)""")

cursor.execute("""create table teaches
	(ID			varchar(5),
	 course_id		varchar(8),
	 sec_id			varchar(8),
	 semester		varchar(6),
	 year			numeric(4,0),
	 primary key (ID, course_id, sec_id, semester, year),
	 foreign key (course_id, sec_id, semester, year) references section (course_id, sec_id, semester, year)
		on delete cascade,
	 foreign key (ID) references instructor (ID)
		on delete cascade
	)""")

cursor.execute("""create table student
	(ID			varchar(5),
	 name			varchar(20) not null,
	 dept_name		varchar(20),
	 tot_cred		numeric(3,0) check (tot_cred >= 0),
	 primary key (ID),
	 foreign key (dept_name) references department (dept_name)
		on delete set null
	)""")

cursor.execute("""create table takes
	(ID			varchar(5),
	 course_id		varchar(8),
	 sec_id			varchar(8),
	 semester		varchar(6),
	 year			numeric(4,0),
	 grade		        varchar(2),
	 primary key (ID, course_id, sec_id, semester, year),
	 foreign key (course_id, sec_id, semester, year) references section (course_id, sec_id, semester, year)
		on delete cascade,
	 foreign key (ID) references student (ID)
		on delete cascade
	)""")

cursor.execute("""create table advisor
	(s_ID			varchar(5),
	 i_ID			varchar(5),
	 primary key (s_ID),
	 foreign key (i_ID) references instructor (ID)
		on delete set null,
	 foreign key (s_ID) references student (ID)
		on delete cascade
	)""")

cursor.execute("""create table time_slot
	(time_slot_id		varchar(4),
	 day			varchar(1),
	 start_hr		numeric(2) check (start_hr >= 0 and start_hr < 24),
	 start_min		numeric(2) check (start_min >= 0 and start_min < 60),
	 end_hr			numeric(2) check (end_hr >= 0 and end_hr < 24),
	 end_min		numeric(2) check (end_min >= 0 and end_min < 60),
	 primary key (time_slot_id, day, start_hr, start_min)
	)""")

cursor.execute("""create table prereq
	(course_id		varchar(8),
	 prereq_id		varchar(8),
	 primary key (course_id, prereq_id),
	 foreign key (course_id) references course (course_id)
		on delete cascade,
	 foreign key (prereq_id) references course (course_id)
	)""")

# Fill tables
cursor.execute("""delete from prereq""")
cursor.execute("""delete from time_slot""")
cursor.execute("""delete from advisor""")
cursor.execute("""delete from takes""")
cursor.execute("""delete from student""")
cursor.execute("""delete from teaches""")
cursor.execute("""delete from section""")
cursor.execute("""delete from instructor""")
cursor.execute("""delete from course""")
cursor.execute("""delete from department""")
cursor.execute("""delete from classroom""")
cursor.execute("""insert into classroom values ('Packard', '101', '500')""")
cursor.execute("""insert into classroom values ('Painter', '514', '10')""")
cursor.execute("""insert into classroom values ('Taylor', '3128', '70')""")
cursor.execute("""insert into classroom values ('Watson', '100', '30')""")
cursor.execute("""insert into classroom values ('Watson', '120', '50')""")
cursor.execute("""insert into department values ('Biology', 'Watson', '90000')""")
cursor.execute("""insert into department values ('Comp. Sci.', 'Taylor', '100000')""")
cursor.execute("""insert into department values ('Elec. Eng.', 'Taylor', '85000')""")
cursor.execute("""insert into department values ('Finance', 'Painter', '120000')""")
cursor.execute("""insert into department values ('History', 'Painter', '50000')""")
cursor.execute("""insert into department values ('Music', 'Packard', '80000')""")
cursor.execute("""insert into department values ('Physics', 'Watson', '70000')""")
cursor.execute("""insert into course values ('BIO-101', 'Intro. to Biology', 'Biology', '4')""")
cursor.execute("""insert into course values ('BIO-301', 'Genetics', 'Biology', '4')""")
cursor.execute("""insert into course values ('BIO-399', 'Computational Biology', 'Biology', '3')""")
cursor.execute("""insert into course values ('CS-101', 'Intro. to Computer Science', 'Comp. Sci.', '4')""")
cursor.execute("""insert into course values ('CS-190', 'Game Design', 'Comp. Sci.', '4')""")
cursor.execute("""insert into course values ('CS-315', 'Robotics', 'Comp. Sci.', '3')""")
cursor.execute("""insert into course values ('CS-319', 'Image Processing', 'Comp. Sci.', '3')""")
cursor.execute("""insert into course values ('CS-347', 'Database System Concepts', 'Comp. Sci.', '3')""")
cursor.execute("""insert into course values ('EE-181', 'Intro. to Digital Systems', 'Elec. Eng.', '3')""")
cursor.execute("""insert into course values ('FIN-201', 'Investment Banking', 'Finance', '3')""")
cursor.execute("""insert into course values ('HIS-351', 'World History', 'History', '3')""")
cursor.execute("""insert into course values ('MU-199', 'Music Video Production', 'Music', '3')""")
cursor.execute("""insert into course values ('PHY-101', 'Physical Principles', 'Physics', '4')""")
cursor.execute("""insert into instructor values ('10101', 'Srinivasan', 'Comp. Sci.', '65000')""")
cursor.execute("""insert into instructor values ('12121', 'Wu', 'Finance', '90000')""")
cursor.execute("""insert into instructor values ('15151', 'Mozart', 'Music', '40000')""")
cursor.execute("""insert into instructor values ('22222', 'Einstein', 'Physics', '95000')""")
cursor.execute("""insert into instructor values ('32343', 'El Said', 'History', '60000')""")
cursor.execute("""insert into instructor values ('33456', 'Gold', 'Physics', '87000')""")
cursor.execute("""insert into instructor values ('45565', 'Katz', 'Comp. Sci.', '75000')""")
cursor.execute("""insert into instructor values ('58583', 'Califieri', 'History', '62000')""")
cursor.execute("""insert into instructor values ('76543', 'Singh', 'Finance', '80000')""")
cursor.execute("""insert into instructor values ('76766', 'Crick', 'Biology', '72000')""")
cursor.execute("""insert into instructor values ('83821', 'Brandt', 'Comp. Sci.', '92000')""")
cursor.execute("""insert into instructor values ('98345', 'Kim', 'Elec. Eng.', '80000')""")
cursor.execute("""insert into section values ('BIO-101', '1', 'Summer', '2017', 'Painter', '514', 'B')""")
cursor.execute("""insert into section values ('BIO-301', '1', 'Summer', '2018', 'Painter', '514', 'A')""")
cursor.execute("""insert into section values ('CS-101', '1', 'Fall', '2017', 'Packard', '101', 'H')""")
cursor.execute("""insert into section values ('CS-101', '1', 'Spring', '2018', 'Packard', '101', 'F')""")
cursor.execute("""insert into section values ('CS-190', '1', 'Spring', '2017', 'Taylor', '3128', 'E')""")
cursor.execute("""insert into section values ('CS-190', '2', 'Spring', '2017', 'Taylor', '3128', 'A')""")
cursor.execute("""insert into section values ('CS-315', '1', 'Spring', '2018', 'Watson', '120', 'D')""")
cursor.execute("""insert into section values ('CS-319', '1', 'Spring', '2018', 'Watson', '100', 'B')""")
cursor.execute("""insert into section values ('CS-319', '2', 'Spring', '2018', 'Taylor', '3128', 'C')""")
cursor.execute("""insert into section values ('CS-347', '1', 'Fall', '2017', 'Taylor', '3128', 'A')""")
cursor.execute("""insert into section values ('EE-181', '1', 'Spring', '2017', 'Taylor', '3128', 'C')""")
cursor.execute("""insert into section values ('FIN-201', '1', 'Spring', '2018', 'Packard', '101', 'B')""")
cursor.execute("""insert into section values ('HIS-351', '1', 'Spring', '2018', 'Painter', '514', 'C')""")
cursor.execute("""insert into section values ('MU-199', '1', 'Spring', '2018', 'Packard', '101', 'D')""")
cursor.execute("""insert into section values ('PHY-101', '1', 'Fall', '2017', 'Watson', '100', 'A')""")
cursor.execute("""insert into teaches values ('10101', 'CS-101', '1', 'Fall', '2017')""")
cursor.execute("""insert into teaches values ('10101', 'CS-315', '1', 'Spring', '2018')""")
cursor.execute("""insert into teaches values ('10101', 'CS-347', '1', 'Fall', '2017')""")
cursor.execute("""insert into teaches values ('12121', 'FIN-201', '1', 'Spring', '2018')""")
cursor.execute("""insert into teaches values ('15151', 'MU-199', '1', 'Spring', '2018')""")
cursor.execute("""insert into teaches values ('22222', 'PHY-101', '1', 'Fall', '2017')""")
cursor.execute("""insert into teaches values ('32343', 'HIS-351', '1', 'Spring', '2018')""")
cursor.execute("""insert into teaches values ('45565', 'CS-101', '1', 'Spring', '2018')""")
cursor.execute("""insert into teaches values ('45565', 'CS-319', '1', 'Spring', '2018')""")
cursor.execute("""insert into teaches values ('76766', 'BIO-101', '1', 'Summer', '2017')""")
cursor.execute("""insert into teaches values ('76766', 'BIO-301', '1', 'Summer', '2018')""")
cursor.execute("""insert into teaches values ('83821', 'CS-190', '1', 'Spring', '2017')""")
cursor.execute("""insert into teaches values ('83821', 'CS-190', '2', 'Spring', '2017')""")
cursor.execute("""insert into teaches values ('83821', 'CS-319', '2', 'Spring', '2018')""")
cursor.execute("""insert into teaches values ('98345', 'EE-181', '1', 'Spring', '2017')""")
cursor.execute("""insert into student values ('00128', 'Zhang', 'Comp. Sci.', '102')""")
cursor.execute("""insert into student values ('12345', 'Shankar', 'Comp. Sci.', '32')""")
cursor.execute("""insert into student values ('19991', 'Brandt', 'History', '80')""")
cursor.execute("""insert into student values ('23121', 'Chavez', 'Finance', '110')""")
cursor.execute("""insert into student values ('44553', 'Peltier', 'Physics', '56')""")
cursor.execute("""insert into student values ('45678', 'Levy', 'Physics', '46')""")
cursor.execute("""insert into student values ('54321', 'Williams', 'Comp. Sci.', '54')""")
cursor.execute("""insert into student values ('55739', 'Sanchez', 'Music', '38')""")
cursor.execute("""insert into student values ('70557', 'Snow', 'Physics', '0')""")
cursor.execute("""insert into student values ('76543', 'Brown', 'Comp. Sci.', '58')""")
cursor.execute("""insert into student values ('76653', 'Aoi', 'Elec. Eng.', '60')""")
cursor.execute("""insert into student values ('98765', 'Bourikas', 'Elec. Eng.', '98')""")
cursor.execute("""insert into student values ('98988', 'Tanaka', 'Biology', '120')""")
cursor.execute("""insert into takes values ('00128', 'CS-101', '1', 'Fall', '2017', 'A')""")
cursor.execute("""insert into takes values ('00128', 'CS-347', '1', 'Fall', '2017', 'A-')""")
cursor.execute("""insert into takes values ('12345', 'CS-101', '1', 'Fall', '2017', 'C')""")
cursor.execute("""insert into takes values ('12345', 'CS-190', '2', 'Spring', '2017', 'A')""")
cursor.execute("""insert into takes values ('12345', 'CS-315', '1', 'Spring', '2018', 'A')""")
cursor.execute("""insert into takes values ('12345', 'CS-347', '1', 'Fall', '2017', 'A')""")
cursor.execute("""insert into takes values ('19991', 'HIS-351', '1', 'Spring', '2018', 'B')""")
cursor.execute("""insert into takes values ('23121', 'FIN-201', '1', 'Spring', '2018', 'C+')""")
cursor.execute("""insert into takes values ('44553', 'PHY-101', '1', 'Fall', '2017', 'B-')""")
cursor.execute("""insert into takes values ('45678', 'CS-101', '1', 'Fall', '2017', 'F')""")
cursor.execute("""insert into takes values ('45678', 'CS-101', '1', 'Spring', '2018', 'B+')""")
cursor.execute("""insert into takes values ('45678', 'CS-319', '1', 'Spring', '2018', 'B')""")
cursor.execute("""insert into takes values ('54321', 'CS-101', '1', 'Fall', '2017', 'A-')""")
cursor.execute("""insert into takes values ('54321', 'CS-190', '2', 'Spring', '2017', 'B+')""")
cursor.execute("""insert into takes values ('55739', 'MU-199', '1', 'Spring', '2018', 'A-')""")
cursor.execute("""insert into takes values ('76543', 'CS-101', '1', 'Fall', '2017', 'A')""")
cursor.execute("""insert into takes values ('76543', 'CS-319', '2', 'Spring', '2018', 'A')""")
cursor.execute("""insert into takes values ('76653', 'EE-181', '1', 'Spring', '2017', 'C')""")
cursor.execute("""insert into takes values ('98765', 'CS-101', '1', 'Fall', '2017', 'C-')""")
cursor.execute("""insert into takes values ('98765', 'CS-315', '1', 'Spring', '2018', 'B')""")
cursor.execute("""insert into takes values ('98988', 'BIO-101', '1', 'Summer', '2017', 'A')""")
cursor.execute("""insert into takes values ('98988', 'BIO-301', '1', 'Summer', '2018', null)""")
cursor.execute("""insert into advisor values ('00128', '45565')""")
cursor.execute("""insert into advisor values ('12345', '10101')""")
cursor.execute("""insert into advisor values ('23121', '76543')""")
cursor.execute("""insert into advisor values ('44553', '22222')""")
cursor.execute("""insert into advisor values ('45678', '22222')""")
cursor.execute("""insert into advisor values ('76543', '45565')""")
cursor.execute("""insert into advisor values ('76653', '98345')""")
cursor.execute("""insert into advisor values ('98765', '98345')""")
cursor.execute("""insert into advisor values ('98988', '76766')""")
cursor.execute("""insert into time_slot values ('A', 'M', '8', '0', '8', '50')""")
cursor.execute("""insert into time_slot values ('A', 'W', '8', '0', '8', '50')""")
cursor.execute("""insert into time_slot values ('A', 'F', '8', '0', '8', '50')""")
cursor.execute("""insert into time_slot values ('B', 'M', '9', '0', '9', '50')""")
cursor.execute("""insert into time_slot values ('B', 'W', '9', '0', '9', '50')""")
cursor.execute("""insert into time_slot values ('B', 'F', '9', '0', '9', '50')""")
cursor.execute("""insert into time_slot values ('C', 'M', '11', '0', '11', '50')""")
cursor.execute("""insert into time_slot values ('C', 'W', '11', '0', '11', '50')""")
cursor.execute("""insert into time_slot values ('C', 'F', '11', '0', '11', '50')""")
cursor.execute("""insert into time_slot values ('D', 'M', '13', '0', '13', '50')""")
cursor.execute("""insert into time_slot values ('D', 'W', '13', '0', '13', '50')""")
cursor.execute("""insert into time_slot values ('D', 'F', '13', '0', '13', '50')""")
cursor.execute("""insert into time_slot values ('E', 'T', '10', '30', '11', '45 ')""")
cursor.execute("""insert into time_slot values ('E', 'R', '10', '30', '11', '45 ')""")
cursor.execute("""insert into time_slot values ('F', 'T', '14', '30', '15', '45 ')""")
cursor.execute("""insert into time_slot values ('F', 'R', '14', '30', '15', '45 ')""")
cursor.execute("""insert into time_slot values ('G', 'M', '16', '0', '16', '50')""")
cursor.execute("""insert into time_slot values ('G', 'W', '16', '0', '16', '50')""")
cursor.execute("""insert into time_slot values ('G', 'F', '16', '0', '16', '50')""")
cursor.execute("""insert into time_slot values ('H', 'W', '10', '0', '12', '30')""")
cursor.execute("""insert into prereq values ('BIO-301', 'BIO-101')""")
cursor.execute("""insert into prereq values ('BIO-399', 'BIO-101')""")
cursor.execute("""insert into prereq values ('CS-190', 'CS-101')""")
cursor.execute("""insert into prereq values ('CS-315', 'CS-101')""")
cursor.execute("""insert into prereq values ('CS-319', 'CS-101')""")
cursor.execute("""insert into prereq values ('CS-347', 'CS-101')""")
cursor.execute("""insert into prereq values ('EE-181', 'PHY-101')""")

conn.commit()

cursor.execute('''SELECT sql
                    FROM sqlite_schema
                   WHERE type='table' ''')
schema = re.sub("\n  *",
                "\n     ",
                "\n".join([x[0] for x in cursor.fetchall()]))
with open(DATABASE.replace('.sqlite', '.json'), 'w', encoding='utf-8') as fid:
    json.dump(schema, fid)

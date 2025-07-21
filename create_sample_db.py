import sqlite3 as sq3

con = sq3.connect("./databases/sample_1.db")

con.executescript("""
CREATE TABLE Professor (
    IDProfessor INTEGER PRIMARY KEY,
    Name        TEXT
);

CREATE TABLE Courses (
    IDCourse     INTEGER PRIMARY KEY,
    IDProfessor  INTEGER REFERENCES Professor(IDProfessor),
    Name         TEXT
);

CREATE TABLE Session (
    IDSession INTEGER PRIMARY KEY,
    Hours     INTEGER,
    IDCourse  INTEGER REFERENCES Courses(IDCourse)
);

CREATE TABLE CdS (
    IDCdS       INTEGER PRIMARY KEY,
    NameCdS     TEXT,
    NumStudents INTEGER
);

CREATE TABLE CourseCdS (
    IDCourse INTEGER,
    IDCdS    INTEGER,
    PRIMARY KEY (IDCourse, IDCdS),
    FOREIGN KEY (IDCourse) REFERENCES Courses(IDCourse),
    FOREIGN KEY (IDCdS)    REFERENCES CdS(IDCdS)
);

CREATE TABLE Rooms (
    IDRoom   INTEGER PRIMARY KEY,
    Capacity INTEGER,
    Name     TEXT
);
""")

con.commit()

con.executescript(
    """
PRAGMA foreign_keys = ON;

/* ----------  Professor  ---------- */
INSERT INTO Professor (IDProfessor, Name) VALUES
  (1, 'Prof 1'),
  (2, 'Prof 2'),
  (3, 'Prof 3');

/* ----------  Courses  ---------- */
INSERT INTO Courses (IDCourse, IDProfessor, Name) VALUES
  (101, 1, 'ANALISI 1'),
  (102, 2, 'PROGRAMMAZIONE'),
  (103, 2, 'SISTEMI OPERATIVI'),
  (104, 3, 'GEOMETRIA'),
  (105, 3, 'ANALISI 2');

/* ----------  Session  ---------- */
INSERT INTO Session (IDSession, Hours, IDCourse) VALUES
  (1, 2, 101),
  (2, 3, 101),
  (3, 3, 102),
  (4, 4, 102),
  (5, 2, 103),
  (6, 2, 103),
  (7, 2, 103),
  (8, 3, 104),
  (9, 2, 104),
  (10, 3, 105);


/* ----------  CdS (degree programmes)  ---------- */
INSERT INTO CdS (IDCdS, NameCdS, NumStudents) VALUES
  (201, 'AIDA',   80),
  (202, 'MATEMATICA', 40),
  (203, 'INGEGNERIA INFORMATICA',  70);

/* ----------  CourseCdS (junction table)  ---------- */
INSERT INTO CourseCdS (IDCourse, IDCdS) VALUES
  (101, 201),
  (101, 202),
  (101, 203),

  (102, 201),
  (102, 203),

  (103, 203),

  (104, 201),
  (104, 202),

  (105, 202);

/* ----------  Rooms  ---------- */
INSERT INTO Rooms (IDRoom, Capacity, Name) VALUES
  (301, 120, 'Aula Morin'),
  (302,  60, 'Aula 4B H2 Bis'),
  (303,  200, 'Aula Ciamician'),
  (304,  30, 'Laboratorio Informatico'),
  (305,  100, 'Aula Magna H3'),
  (306,  10, 'Edificio Economo Aula 1'),
  (307,  80, 'Aula 3A H2 Bis'),
  (308,  80, 'Aula I Edificio Tutankhamon');
"""
)

con.close()
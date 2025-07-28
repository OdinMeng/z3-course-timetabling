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

CREATE TABLE SCHEDULE(
    Timeslot INTEGER,
    Session INTEGER,
    Room INTEGER,
    FOREIGN KEY (Session) REFERENCES Session(IDSession),
    FOREIGN KEY (Room) REFERENCES Rooms(IDRoom),
    PRIMARY KEY(Timeslot, Session, Room)
);

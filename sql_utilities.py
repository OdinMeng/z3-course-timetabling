import sqlite3 as sq3
from typing import Dict, List

class SQLUtility():
    def __init__(self, fname):
        self.fname = fname 
        self.con = None

    def start(self):
        self.con = sq3.connect(f"./databases/{self.fname}.db")

        TABLE_DDLS = {
    "Professor": """
        CREATE TABLE Professor (
            IDProfessor INTEGER PRIMARY KEY,
            Name        TEXT
        );
    """,
    "Courses": """
        CREATE TABLE Courses (
            IDCourse     INTEGER PRIMARY KEY,
            IDProfessor  INTEGER REFERENCES Professor(IDProfessor),
            Name         TEXT
        );
    """,
    "Session": """
        CREATE TABLE Session (
            IDSession INTEGER PRIMARY KEY,
            Hours     INTEGER,
            IDCourse  INTEGER REFERENCES Courses(IDCourse)
        );
    """,
    "CdS": """
        CREATE TABLE CdS (
            IDCdS       INTEGER PRIMARY KEY,
            NameCdS     TEXT,
            NumStudents INTEGER
        );
    """,
    "CourseCdS": """
        CREATE TABLE CourseCdS (
            IDCourse INTEGER,
            IDCdS    INTEGER,
            PRIMARY KEY (IDCourse, IDCdS),
            FOREIGN KEY (IDCourse) REFERENCES Courses(IDCourse),
            FOREIGN KEY (IDCdS)    REFERENCES CdS(IDCdS)
        );
    """,
    "Rooms": """
        CREATE TABLE Rooms (
            IDRoom   INTEGER PRIMARY KEY,
            Capacity INTEGER,
            Name     TEXT
        );
    """
            }
        for table_name in ["Professor", "Courses", "Session", "CdS", "CourseCdS", "Rooms"]:
            try:
                self.con.execute(f"SELECT 1 FROM {table_name} LIMIT 1;")
            except sq3.OperationalError as e:
                if "no such table" in str(e):
                    print(f"| /!\\ [WARNING] /!\\ | Table '{table_name}' not found. The table has been automatically created.")
                    self.con.execute(TABLE_DDLS[table_name])

    def check(self):
        try:
            self.con.execute("SELECT 1;")
        except sq3.ProgrammingError:
            raise Exception("no")
        
        if not self.con:
            raise Exception("no")

    def end(self):
        self.check()
        self.con.close()

    def get_course(self, session) -> int:
        self.check()
        # return COURSE only (unique!)

        query = self.con.execute("SELECT IDCourse FROM Session WHERE IDSession = ?", (session,))
        return query.fetchone()[0]

    def get_total_students(self, course) -> int:
        self.check()
        # return integer with number of students

        query = self.con.execute("""
                                 SELECT sum(CdS.NumStudents) 
                                 FROM Courses, CdS, CourseCdS T 
                                 WHERE 
                                    Courses.IDCourse = ? AND
                                    T.IDCourse = Courses.IDCourse AND
                                    T.IDCdS = CdS.IDCdS;
                                 """,
                                 (course,))
        return query.fetchone()[0]

    def get_sessions(self, course) -> List:
        self.check()
        # return sessions of a cours

        query = self.con.execute("""
            SELECT IDSession
            FROM Session
            WHERE IDCourse = ?
                                  """,
            (course, ))
        return [i[0] for i in query.fetchall()]

    def get_other_session_courses(self, session) -> List:
        self.check()
        # return sessions of other courses of the same CdS, excluding the course of the input session (note: ad hoc function)

        query = self.con.execute("""
            SELECT DISTINCT S2.IDSession
            FROM    Session S1, Courses C1, CourseCdS T1,
                    Session S2, Courses C2, CourseCdS T2
            WHERE
                S1.IDSession = ?            AND
                S1.IDCourse  = C1.IDCourse       AND
                C1.IDCourse  = T1.IDCourse       AND
                T1.IDCdS     = T2.IDCdS          AND
                T2.IDCourse = C2.IDCourse       AND
                C2.IDCourse <> C1.IDCourse       AND
                C2.IDCourse  = S2.IDCourse;
                                 """,
            (session,))
        return [i[0] for i in query.fetchall()]

    def get_professor(self, session) -> int:
        self.check()
        #return the professor of the session's course

        query = self.con.execute("""
            SELECT DISTINCT IDProfessor 
            FROM Courses, Session
            WHERE
                Courses.IDCourse = Session.IDCourse AND
                Session.IDSession = ?;
                                 """,
            (session, ))
        return query.fetchone()[0] 

    def get_capacity(self, room) -> int:
        self.check()
        # get capacity of a room
        query = self.con.execute("""
            SELECT DISTINCT Capacity 
            FROM Rooms
            WHERE
                IDRoom = ?;
                                """,
            (room, ))
        return query.fetchone()[0] 

    def get_ids(self) -> Dict:
        self.check()
        # return dictionary with keys Sessions, Courses, CdS, Professors, Rooms each containing a list with primary keys
        RETDICT = {}

        s_sessions = self.con.execute("SELECT IDSession FROM Session;")
        s_courses = self.con.execute("SELECT IDCourse FROM Courses;")
        s_professors = self.con.execute("SELECT IDProfessor FROM Professor;")
        s_cds = self.con.execute("SELECT IDCdS FROM CdS;")
        s_rooms = self.con.execute("SELECT IDRoom FROM Rooms;")

        RETDICT['Sessions'] = [i[0] for i in s_sessions.fetchall()]
        RETDICT['Courses'] = [i[0] for i in s_courses.fetchall()]
        RETDICT['Professors'] = [i[0] for i in s_professors.fetchall()]
        RETDICT['CdS'] = [i[0] for i in s_cds.fetchall()]
        RETDICT['Rooms'] = [i[0] for i in s_rooms.fetchall()]

        return RETDICT

    # sono tutte delle SELECT o robe strane bruh
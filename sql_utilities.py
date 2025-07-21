import sqlite3 as sq3
from typing import Dict, List

global con 
con = None

def start(fname):
    con = sq3.connect(f"./databases/{fname}.db")

def end():
    if not con:
        raise Exception("no")
    con.close()

def get_course(session) -> int:
    check()
    # return COURSE only (unique!)
    pass

def get_total_students(course) -> int:
    check()
    # return integer with number of students
    pass

def get_sessions(course) -> List:
    check()
    # return sessions of a course
    pass

def get_other_session_courses(session) -> List:
    check()
    # return sessions of other courses of the same CdS, excluding the course of the input session (note: ad hoc function)
    pass 

def get_professor(session) -> int:
    #return the professor of the session's course
    pass 

def get_capacity(room) -> int:
    check()
    # get capacity of a room
    pass

def get_ids(fname) -> Dict:
    check()
    # return dictionary with keys Sessions, Courses, CdS, Professors, Rooms each containing a list with primary keys
    RETDICT = {}

    s_sessions = con.execute("SELECT IDSession FROM Session;")
    s_courses = con.execute("SELECT IDCourse FROM Courses;")
    s_professors = con.execute("SELECT IDProfessor FROM Professor;")
    s_cds = con.execute("SELECT IDCdS FROM CdS;")
    s_rooms = con.execute("SELECT IDRoom FROM Rooms;")

    RETDICT['Sessions'] = [i[0] for i in s_sessions.fetchall()]
    RETDICT['Courses'] = [i[0] for i in s_courses.fetchall()]
    RETDICT['Professors'] = [i[0] for i in s_professors.fetchall()]
    RETDICT['CdS'] = [i[0] for i in s_cds.fetchall()]
    RETDICT['Rooms'] = [i[0] for i in s_rooms.fetchall()]

    return RETDICT

def check():
    if not con:
        raise Exception("no")

# sono tutte delle SELECT o robe strane bruh
PRAGMA foreign_keys = ON;

/* ----------  Professor  ---------- */
INSERT INTO Professor (IDProfessor, Name) VALUES
  (1, 'John Smith'),
  (2, 'Andrea Garfields'),
  (3, 'John Doe'),
  (4, 'Jane Doe');

/* ----------  Courses  ---------- */
INSERT INTO Courses (IDCourse, IDProfessor, Name) VALUES
    (1, 1, "Maths 101"),
    (2, 1, "Introduction to Wizardry"),
    (3, 2, "Reading 102"),
    (4, 3, "Musical Analysis"),
    (5, 2, "Advanced English"),
    (6, 4, "Tennis 101");

/* ----------  Session  ---------- */
INSERT INTO Session (IDSession, Hours, IDCourse) VALUES
    (1, 2, 1),
    (2, 2, 1),
    (3, 3, 2),
    (4, 1, 3),
    (5, 2, 3),
    (6, 2, 4),
    (7, 5, 4),
    (8, 2, 5),
    (9, 1, 6);

/* ----------  CdS (degree programmes)  ---------- */
INSERT INTO CdS (IDCdS, NameCdS, NumStudents) VALUES
    (1, "Maths and Reading", 50),
    (2, "Music and Sports", 30),
    (3, "Maths and Music", 60);

/* ----------  CourseCdS (junction table)  ---------- */
INSERT INTO CourseCdS (IDCourse, IDCdS) VALUES
    (1, 1),
    (3, 1),
    (5, 1),
    (4, 2),
    (6, 2),
    (2, 2),
    (1, 3),
    (4, 3); 

/* ----------  Rooms  ---------- */
INSERT INTO Rooms (IDRoom, Capacity, Name) VALUES
    (1, 200, "Big Room"),
    (2, 100, "Medium Room"),
    (3, 50, "Small Room"),
    (4, 10, "Very Small Room");
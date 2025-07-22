PRAGMA foreign_keys = ON;

/* ----------  Professor  ---------- */
INSERT INTO Professor (IDProfessor, Name) VALUES
  (1, "V.R."),
  (2, "C.G."),
  (3, "A.R.V."),
  (4, "S.C."),
  (5, "A.P."),
  (6, "R.S."),
  (7, "C.N."),
  (8, "boh"),
  (9, "boh 2"),
  (10, "boh 3");

/* ----------  Courses  ---------- */
INSERT INTO Courses (IDCourse, IDProfessor, Name) VALUES
  (1100, 1, "LINGUA E LETTERATURA ITALIANA"),
  (1201, 2, "PRIMA LINGUA STRANIERA (INGLESE)"),
  (1202, 3, "SECONDA LINGUA STRANIERA (TEDESCO)"),
  (1203, 4, "TERZA LINGUA STRANIERA (RUSSO)"),
  (1301, 5, "STORIA"),
  (1302, 5, "FILOSOFIA"),
  (1401, 6, "MATEMATICA"),
  (1402, 6, "FISICA"),
  (1403, 7, "SCIENZE NATURALI"),
  (1303, 8, "STORIA DELL'ARTE"),
  (1501, 9, "SCIENZE E MOTORIE SPORTIVE"),
  (1601, 10, "RELIGIONE CATTOCIA O ATTIVITA' ALTERNATIVE"),

  (2100, 1, "LINGUA E LETTERATURA ITALIANA"),
  (2201, 2, "PRIMA LINGUA STRANIERA (INGLESE)"),
  (2202, 3, "SECONDA LINGUA STRANIERA (TEDESCO)"),
  (2203, 4, "TERZA LINGUA STRANIERA (RUSSO)"),
  (2301, 5, "STORIA"),
  (2302, 5, "FILOSOFIA"),
  (2401, 6, "MATEMATICA"),
  (2402, 6, "FISICA"),
  (2403, 7, "SCIENZE NATURALI"),
  (2303, 8, "STORIA DELL'ARTE"),
  (2501, 9, "SCIENZE E MOTORIE SPORTIVE"),
  (2601, 10, "RELIGIONE CATTOCIA O ATTIVITA' ALTERNATIVE"),
  
  (3100, 1, "LINGUA E LETTERATURA ITALIANA"),
  (3201, 2, "PRIMA LINGUA STRANIERA (INGLESE)"),
  (3202, 3, "SECONDA LINGUA STRANIERA (TEDESCO)"),
  (3203, 4, "TERZA LINGUA STRANIERA (RUSSO)"),
  (3301, 5, "STORIA"),
  (3302, 5, "FILOSOFIA"),
  (3401, 6, "MATEMATICA"),
  (3402, 6, "FISICA"),
  (3403, 7, "SCIENZE NATURALI"),
  (3303, 8, "STORIA DELL'ARTE"),
  (3501, 9, "SCIENZE E MOTORIE SPORTIVE"),
  (3601, 10, "RELIGIONE CATTOCIA O ATTIVITA' ALTERNATIVE");

  
/* ----------  Session  ---------- */
INSERT INTO Session (IDSession, Hours, IDCourse) VALUES


/* ----------  CdS (degree programmes)  ---------- */
INSERT INTO CdS (IDCdS, NameCdS, NumStudents) VALUES
  (1, 'CLASSE 3B', 20),
  (2, 'CLASSE 4B', 22),
  (3, 'CLASSE 5B',  18);

/* ----------  CourseCdS (junction table)  ---------- */
INSERT INTO CourseCdS (IDCourse, IDCdS) VALUES


/* ----------  Rooms  ---------- */
INSERT INTO Rooms (IDRoom, Capacity, Name) VALUES
  (1, 9999, "ANNO III"),
  (2, 9999, "ANNO IV"),
  (3, 9999, "ANNO V");
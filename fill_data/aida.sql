PRAGMA foreign_keys = ON;

/* ----------  Professor  ---------- */
INSERT INTO Professor (IDProfessor, Name) VALUES
  (1, 'D.D.S.'),
  (2, 'M.G.'),
  (3, 'G.C.'),
  (4, 'L.M.'),
  (5, 'T.N.'),
  (6, 'L.B.'),
  (7, 'A.P.'),
  (8, 'R.G.A.'),
  (9, 'T.P.'),
  (10, 'A.O.');

/* ----------  Courses  ---------- */
INSERT INTO Courses (IDCourse, IDProfessor, Name) VALUES
-- Anno I (matricole)
    (255, 1, 'ANALISI 1'),
    (285, 2, 'ALGEBRA LINEARE ED ELEMENTI DI GEOMETRIA'),
    (286, 3, 'INTRODUZIONE ALLA PROGRAMMAZIONE E LABORATORIO'),
    (287, 4, 'ARCHITETTURE DEGLI ELABORATORI'),
-- Anno II (esclusivi)
    (264, 5, 'INFERENZA STATISTICA'),
    (265, 6, 'ALGORITMI E STRUTTURE DATI'),
    (267, 7, 'COMPUTABILITà, COMPLESSITà E LOGICA'),


-- Corsi condivisi tra il II e III anno
    (270, 4, 'PROGRAMMAZIONE AVANZATA E PARALLELA'),

-- Anno III (esclusivi)
    (271, 8, 'INTRODUZIONE AL MACHINE LEARNING'),
    (272, 9, 'INTRODUZIONE ALL INTELLIGENZA ARTIFICIALE'),
    (290, 10, 'SISTEMI COMPLESSI');

/* ----------  Session  ---------- */
INSERT INTO Session (IDSession, Hours, IDCourse) VALUES
    (1, 2, 255),
    (2, 2, 255),
    (3, 2, 255),
    
    (4, 2, 285),
    (5, 2, 285),
    (6, 2, 285),
    
    (7, 3, 286),
    (8, 2, 286),
    (9, 3, 286),
    (10, 4, 286),

    (11, 3, 287),

    (12, 2, 264),
    (13, 2, 264),
    (14, 2, 264),

    (15, 2, 265),
    (16, 2, 265),
    (17, 2, 265),

    (18, 2, 267),
    (19, 2, 267),
    (20, 2, 267),

    (21, 2, 270),
    (22, 2, 270),
    (23, 2, 270),

    (24, 2, 271),
    (25, 2, 271),
    (26, 2, 271),

    (27, 3, 272),
    (28, 2, 272),
    (29, 2, 272),

    (30, 3, 290),
    (31, 2, 290);


/* ----------  CdS (degree programmes)  ---------- */
INSERT INTO CdS (IDCdS, NameCdS, NumStudents) VALUES
  (1, 'AIDA - PRIMO ANNO', 100),
  (2, 'AIDA - SECONDO ANNO', 50),
  (3, 'AIDA - TERZO ANNO',  30);

/* ----------  CourseCdS (junction table)  ---------- */
INSERT INTO CourseCdS (IDCourse, IDCdS) VALUES
    (255, 1),
    (285, 1),
    (286, 1),
    (287, 1),
    
    (264, 2),
    (265, 2),
    (267, 2),

    (270, 2),
    (270, 3),

    (271, 3),
    (272, 3),
    (290, 3);



/* ----------  Rooms  ---------- */
INSERT INTO Rooms (IDRoom, Capacity, Name) VALUES
    (1, 172, 'H2 Bis, 2A MORIN'),
    (2, 76, 'H2 Bis, 3B'),
    (3, 47, 'H2 Bis, 4C'),
    (4, 39, 'H2 Bis, 5A'),
    (5, 47, 'H2 Bis, 5B'),
    (6, 38, 'H2 Bis, 5C'),

    (7, 267, 'H3, 1A'),
    (8, 250, 'H3, 1B'),
    (9, 80, 'H3, 1C'),
    (10, 151, 'H3, 2A'),
    (11, 136, 'H3, 2B'),
    (12, 74, 'H3, 2C');

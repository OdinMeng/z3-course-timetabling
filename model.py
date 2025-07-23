"""File for defining the model with base constraints (note: the user can additionally add other constraints!)"""

from z3 import * 
import itertools
from sql_utilities import SQLUtility

class TimetableScheduler():
    def __init__(self, fname: str, timeslots_per_day: int):
        self.timeslots_per_day = timeslots_per_day
        self.fname = fname

        self.solver = Solver()
        self.model = None

        self.X = dict()
        self.Y = dict()
        self.indexes = dict()
        self.T = list(range(timeslots_per_day*6)) # Ammettiamo che si facciano lezioni dal lunedì al sabato (se non vuole che si faccia il sabato basta aggiungere manualmente ulteriori vincoli)

        self.database = None

        self.started = False
        self.posed = False

    def start(self):
        self.database = SQLUtility(self.fname)
        self.database.start()
        self.indexes = self.database.get_ids()

        # fill variables with indexes
        for (S,T,R) in itertools.product(self.indexes["Sessions"], self.T, self.indexes["Rooms"]):
            idx_string = f"{S}%{T}%{R}"
            self.X[S,T,R] = Bool(f'X_{idx_string}')
            self.Y[S,T,R] = Bool(f'Y_{idx_string}')

        self.started = True

    def add_constraints(self):
        if not self.check():
            return -1

        # C1: No more than two sessions in the same room, C2: Sessions must be contiguous
        # C7: A session happens only in one room
        for (S,T, R) in itertools.product(self.indexes["Sessions"], self.T, self.indexes["Rooms"]):
            self.solver.assert_and_track(
                Implies(
                    self.X[S,T,R], 
                    And([Not(self.X[Si, T, R]) for Si in self.indexes["Sessions"] if Si != S])
                    ),
                    f'C1-{S}%{T}%{R}'
                )
            
            # C7
            self.solver.assert_and_track(
                Implies(
                    self.X[S, T, R],
                    And( [ Not(self.X[S, T, Ai]) for Ai in self.indexes['Rooms'] if Ai != R ] )
                ),
                f"C7-{S}%{T}%{R}"
            )
            
            # C2: modified
            S_h = self.database.get_hours(S)

            if T+S_h-1 > max(self.T) or ((T+S_h-1) // self.timeslots_per_day) != (T//self.timeslots_per_day):
                self.solver.assert_and_track(
                        Not(self.Y[S,T,R]),
                    f"noC2-{S}%{T}%{R}"
                )
            else:
                self.solver.assert_and_track(
                    Implies(
                        self.Y[S,T,R],
                        And(
                            [ self.X[S,T+k, R] for k in range(0, S_h) ]
                        )
                    ),
                        f"C2-{S}%{T}%{R}"
                )

        # C3: A professor can have only one session at the same time
        # C4: There cannot be >=2 sessions of courses belonging to the same CdS in the same timeslot (and any room) 
        for (S,T) in itertools.product(self.indexes['Sessions'], self.T):
            self.solver.assert_and_track(
                Implies(
                    Or( [ self.X[S, T, A] for A in self.indexes['Rooms'] ]),
                    And([ Not(self.X[Si, T, Ai]) for (Si, Ai) in itertools.product(self.indexes['Sessions'], self.indexes['Rooms']) if (Si != S and self.database.get_professor(S) == self.database.get_professor(Si)) ])
                ),
                f'C3-{S}%{T}'
            )
            

            self.solver.assert_and_track(
                Implies(
                    Or(
                        [ self.X[S,T,A] for A in self.indexes['Rooms'] ]
                    ),
                    And(
                        ([ Not(self.X[Si, T, Ai]) for (Si, Ai) in itertools.product(self.database.get_other_session_courses(S), self.indexes['Rooms'])  ])
                    )),
                f'C4-{S}%{T}'
            )       
            

        # C5: Rooms must be able to accomodate all students
        for (S,A) in itertools.product(self.indexes['Sessions'], self.indexes['Rooms']):
            self.solver.assert_and_track(
                Implies(
                    Or( [ self.X[S,T,A] for T in self.T ] ),
                    self.database.get_total_students(self.database.get_course(S)) <= self.database.get_capacity(A)
                ),
                f'c5-{S}%{A}'
            )

        # C6: Every session must be organized exactly only one time (i.e. the amount of hours are exactly right)
        for S in self.indexes['Sessions']:
            self.solver.assert_and_track(
                AtMost( *[self.Y[S, T, R] for (T,R) in itertools.product(self.T, self.indexes['Rooms'])], 1),
                f'A-C6-{S}'
            )
            self.solver.assert_and_track(
                AtLeast( *[self.Y[S, T, R] for (T,R) in itertools.product(self.T, self.indexes['Rooms'])], 1),
                f'B-C6-{S}'
            )

        self.posed = True

    def end(self):
        if not self.check():
            return -1 
         
        self.database.end()

    def solve(self):
        if not self.check or not self.posed:
            return -1
        
        c = self.solver.check()
        if c == sat:
            print("TIME TABLE SUCCESSFULLY CREATED")
            self.model = self.solver.model()
    
        elif c == unsat:
            print("TIME TABLE FAILED")

    def check(self):
        if not self.started():
            print("[ERROR] Database not started yet. Please call the .start() method.")
            return -1


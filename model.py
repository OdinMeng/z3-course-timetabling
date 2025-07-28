"""File for defining the model with base constraints (note: the user can additionally add other constraints!)"""

from z3 import * 
import itertools
from sql_utilities import SQLUtility
import numpy as np 
import pandas as pd 

class TimetableScheduler():
    def __init__(self, fname: str, timeslots_per_day: int, t_start = 8, t_end = None):
        self.timeslots_per_day = timeslots_per_day
        self.fname = fname
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

        if t_end == None:
            t_end = t_start + timeslots_per_day

        if t_end - t_start < 0 or t_end - t_start != timeslots_per_day or not(t_start in range(0, 24)) or not (t_end in range(0,24)):
            print("WARNING: INVALID INPUT DETECTED WITH T_START AND T_END. ROLLING BACK TO DEFAULT PARAMETERS")
            t_start = 8
            t_end = 8 + timeslots_per_day

        self.hours = []
        for i in range(t_start, t_end):
            self.hours.append(f"{str(i).zfill(2)}:00 - {str(i+1).zfill(2)}:00")

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

            print("Saving the schedule in the SQL Database...")
            
            self.database.create_schedule()

            for t in self.T:
                for (S, A) in itertools.product(self.indexes['Sessions'], self.indexes['Rooms']):
                    if self.model.evaluate(self.X[S,t,A], model_completion=True):
                        self.database.insert_entry(S,t,A)

            print("Schedule saved")

        elif c == unsat:
            print("TIME TABLE FAILED")

    def print_schedule_df(self):
        """print the schedule in pandas dataframe format"""

        raw_schedule = self.database.get_schedule()
        ptr_raw = 0

        if raw_schedule == []:
            raise Exception("SCHEDULE NOT FOUND")
        
        processed_schedule = []

        for t in self.T: 
            t_i = []

            flag = False
            if ptr_raw >= len(raw_schedule):
                flag = True   

            if not flag:
                entry = raw_schedule[ptr_raw]
            while entry[0] == t and not flag:
                t_i.append(f"{entry[1]} [{entry[2]}]")
                ptr_raw += 1
                
                if ptr_raw >= len(raw_schedule):
                    break 

                entry = raw_schedule[ptr_raw]

            if t_i == []:
                t_i = ["NO LECTURES / ACTIVITIES"]

            processed_schedule.append(" > " + "\n> ".join(t_i))

        np_schedule = np.array(processed_schedule, dtype=object)
        np_schedule = np_schedule.reshape(6, self.timeslots_per_day)

        df = pd.DataFrame(np_schedule, columns=self.hours, index=self.days)

        return df.T




    def check(self):
        if not self.started:
            print("[ERROR] Database not started yet. Please call the .start() method.")
            return False
        return True
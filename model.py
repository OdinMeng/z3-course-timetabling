"""File for defining the model with base constraints (note: the user can additionally add other constraints!)"""

from z3 import * 
import itertools
from sql_utilities import SQLUtility
import numpy as np 
import pandas as pd 
from typing import Literal
from weekplot import plotSchedule

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

        self.t_start = t_start

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


            """
            # tries to improve schedule by adding an optional constraint: a session of a course can happen only once per day (e.g. a lecture of Maths can happen at most once on sunday)
            for (S,T) in itertools.product(self.indexes['Sessions'], self.T):
                self.solver.add(
                    Implies(
                        Or( [self.X[S,T,A] for A in self.indexes['Rooms']] ),
                        And( [Not(self.X[Si, Ti, Ai]) for (Si, Ti, Ai) in 
                              itertools.product(self.database.get_sessions(self.database.get_course(S)), 
                                                range(T//self.timeslots_per_day, T//self.timeslots_per_day+self.timeslots_per_day),
                                                self.indexes['Rooms']) if Si != S] )
                    )
                )
            """

            for (i,j) in itertools.product(self.indexes['Courses'], [0,1,2,3,4,5]):
                self.solver.add(
                    AtMost(
                        *[self.Y[S,T,V] for (S,T,V) in itertools.product(self.database.get_sessions(i), range(j*self.timeslots_per_day, j*self.timeslots_per_day+self.timeslots_per_day), self.indexes['Rooms'])],
                        1
                    )
                ) 

            print("TRYING TO IMPROVE THE MODEL...")

            c2 = self.solver.check()
            if c2 == sat:
                print("TIME TABLE IMPROVED")
                self.model = self.solver.model()

                print("Saving the improved schedule in the SQL Database...")
                
                self.database.create_schedule()

                for t in self.T:
                    for (S, A) in itertools.product(self.indexes['Sessions'], self.indexes['Rooms']):
                        if self.model.evaluate(self.X[S,t,A], model_completion=True):
                            self.database.insert_entry(S,t,A)
                            
            elif c2 == unsat:
                print("TIME TABLE COULD NOT BE IMPROVED")

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

    def draw_calendar(self, name: str, by: Literal['cds', 'prof', 'course', 'room'], id: int):
        if by not in ['cds', 'prof', 'course', 'room']:
            raise Exception("no")
        self.check()
        # Prints calendar with matplotlib.
        # NOTE: To make this simpler, I must guarantee the uniqueness of the events in the graphical representation (otherwise it would be too technically delicate with Matplotlib and I wouldn't be going too far for this).
        # So users can draw the calendar by various methods:
        # - By CdS (view the sessions of a CdS)
        # - By professor (view the sessions of a professor)
        # - By Course (view sessions)
        # - By room (view the occupancy of each room)

        # TODO: implement some weird sql queries
        # !!! : I MIGHT HAVE TO USE THE Y VARIABLES INSTEAD OF X SO I CAN PROPERLY CALCULATE HOURS  
        # OR HOW CAN I HANDLE CONTIGUITY? WITH A CTR??? IDK MAN

        schedule = self.database.get_schedule_subset(by, id)
        
        map_start = {} # T -> Starting hour
        map_end = {}  # T -> Ending hour
        map_courses_idx = {} # Maps a course ID to an unique index from 0 to len(colormap).

        names = self.database.get_names()

        courses_name = names['Courses']
        rooms_name = names['Rooms']
        cds_name = names['CdS']
        prof_name = names['Professors']

        colormap = [
            'gray', 'sienna', 'lightgoldenrodyellow', 'mediumspringgreen', 'deepskyblue', 'darkorchid',
            'silver', 'sandybrown', 'olivedrab', 'lightseagreen', 'aliceblue', 'plum',
            'rosybrown', 'bisque', 'olivedrab', 'lightseagreen', 'slategray', 'mediumvioletred',
            'firebrick', 'moccasin', 'chartreuse', 'paleturquoise', 'royalblue', 'palevioletred',
            'red', 'gold', 'palegreen', 'paleturquoise', 'navy', 
            'darksalmon', 'darkkhaki', 'darkgreen', 'darkcyan', 'blue',
            'seagreen', 'darkturquoise', 'mediumpurple'
        ]

        i = 0
        for (T, C, A) in schedule:
            if not (C in map_courses_idx):
                if i > len(colormap):
                    raise Exception("too many colours")
                
                map_courses_idx[C] = i
                i += 1

        for t in self.T:
            map_start[t] = self.t_start + (t % self.timeslots_per_day)
            map_end[t] = self.t_start + (t % self.timeslots_per_day) + 1

        # create .txt calendar and fill events entry by entry
        current_course = None
        current_room = None
        t_s = None 
        t_f = None
        with open(fname := f"./timetables/{name}_{by}_{id}.txt", 'w') as f:
            for (T, C, A) in schedule:
                # base case: current_course and current_room is different from the currently iterated one
                # write:
                # - name
                # - day
                if current_course != C or current_room != A or T - t_f > 1:
                    if current_course != None or current_room != None:
                        f.write(f"{str(map_start[t_s]).zfill(2)}:00 - {str(map_end[t_f]).zfill(2)}:00\n")
                        f.write(f"{colormap[map_courses_idx[current_course]]}\n")
                        f.write("\n")

                    t_s = T
                    t_f = T
                    current_course = C
                    current_room = A 
                    day_i = (T // self.timeslots_per_day)
                    day = self.days[day_i][:3]

                    f.write(f"{courses_name[C]} [{rooms_name[A]}]\n")
                    f.write(f"{day}\n")
                else:
                    t_f = T

            else:
                    t_f = T

                    f.write(f"{str(map_start[t_s]).zfill(2)}:00 - {str(map_end[t_f]).zfill(2)}:00\n")
                    f.write(f"{colormap[map_courses_idx[C]]}\n")
                    f.write("\n")

        
        if by == 'cds':
            plotSchedule(fname, f"Course in {cds_name[id]}")
        if by == 'prof':
            plotSchedule(fname, f"Prof. {prof_name[id]}")
        if by == 'course':
            plotSchedule(fname, f"Lectures for {courses_name[id]}")
        if by == 'room':
            plotSchedule(fname, f"Room {rooms_name[id]}")


    def check(self):
        if not self.started:
            print("[ERROR] Database not started yet. Please call the .start() method.")
            return False
        return True
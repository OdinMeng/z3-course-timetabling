"""
Auxiliary file to print a weekly calendar using Matplotlib.
This is a modified version of another user's project. Original code available in the following link: https://github.com/utkuufuk/weekplot
"""

import yaml
from math import ceil
import matplotlib.pyplot as plt
from dataclasses import dataclass
from textwrap import wrap

DAYS = ['Monday','Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

@dataclass
class Event:
    name: str 
    days: int # note: in my modified version it's intended that each event happens ONLY IN ONE DAY (for my z3 timetable scheduling project)
    startH: int
    startM: int 
    endH: int 
    endM: int 
    color: int

def getDay(prefix):
    for d in DAYS:
        if d.startswith(prefix):
            return d
    raise UserWarning("Invalid day: {0}".format(prefix))

def parseYml(filename):
    with open(filename, 'r') as stream:
        try:
            items = yaml.safe_load(stream)
        except yaml.YAMLError as err:
            raise UserWarning("Invalid YML file: {0}".format(err))
    events = []
    latest = 0
    earliest = 24
    for event in items:
        for ocr in event["occurances"]:
            sh = ocr["start"] // 60
            sm = ocr["start"] % 60
            eh = ocr["end"] // 60
            em = ocr["end"] % 60
            days = [getDay(d) for d in ocr["days"]]
            events.append(Event(event["name"], days, sh, sm, eh, em, event["color"]))
            earliest = sh if sh < earliest else earliest
            latest = eh + 1 if eh > latest else latest
    return events, earliest, latest + 1

def parseTxt(fname):
    with open(fname) as fp:
        lines = fp.readlines()
    index = 0
    latest = 0
    earliest = 24
    events = [Event('', '', '', '', '', '', '')]
    for line in lines:
        line = line.rstrip()
        index += 1
        if index == 1:
            events[-1].name = line
        elif index == 2:
            events[-1].days = [getDay(d) for d in line.replace(' ', '').split(',')]
        elif index == 3:
            hours = line.replace(' ', '').split('-')
            start = hours[0].split(':')
            end = hours[1].split(':')
            events[-1].startH = int(start[0])
            events[-1].startM = int(start[1])
            events[-1].endH = int(end[0])
            events[-1].endM = int(end[1])
            earliest = events[-1].startH if events[-1].startH < earliest else earliest
            latest = events[-1].endH + 1 if events[-1].endH > latest else latest
        elif index == 4:
            events[-1].color = line
        elif index == 5 and line == '':
            events.append(Event('', '', '', '', '', '', ''))
            index = 0
        else:
            raise UserWarning("Invalid text input format.")
    return events, earliest, latest + 1

def plotEvent(e, label_list): #TODO: REMOVE LABEL LIST
    for day in e.days:
        d = DAYS.index(day) + 0.52
        start = float(e.startH) + float(e.startM) / 60
        end = float(e.endH) + float(e.endM) / 60

        plt.fill_between([d, d+0.96], [start, start], [end, end], color=e.color)
        plt.text(d + 0.02, start + 0.02, '{0}:{1:0>2}'.format(e.startH, e.startM), va='top', fontsize=8, wrap=True)
        plt.text(d + 0.48, (start + end) * 0.502, '\n'.join(wrap(e.name, 30)), ha='center', va='center', fontsize=8, wrap=True)

def plotSchedule(fname, title):
    try:
        open(fname)
    except:
        raise Exception("FILE NOT FOUND")
    
    events, earliest, latest = parseTxt(fname)    
    
    label_list = []

    fig, ax = plt.subplots(figsize=(18, 9))
    for e in events:
        plotEvent(e, label_list)

    plt.title(f'Weekly Schedule of {title}', y=1, fontsize=14)

    ax.set_xlim(0.5, len(DAYS) + 0.5)
    ax.set_xticks(range(1, len(DAYS) + 1))
    ax.set_xticklabels(DAYS)
    ax.set_ylim(latest, earliest)
    ax.set_yticks(range(ceil(earliest), ceil(latest)))
    ax.set_yticklabels(["{0}:00".format(h) for h in range(ceil(earliest), ceil(latest))])
    ax.grid(axis='y', linestyle='--', linewidth=0.5)

    plt.show()
import sys
import re
import os

def get_sport(user_input):
    sport = 'unknown'
    baseball_teams = [('braves','baseball'),('pirates','baseball'),('cubs','baseball'),('yankees','baseball'),('orioles','baseball')]
    football_teams = [('falcons','football'),('saints','football'),('giants','football'),('jets','football'),('patriots','football')]
    teams = baseball_teams + football_teams
    match = re.match(r"^(?:i\slike\s)?(?:the\s)?(.*)$",user_input,re.IGNORECASE)
    if match:
        for team in teams:
            if team[0] in user_input.lower():
                sport = team[1]
                team = team[0].capitalize()
                break
        if sport == 'unknown':
            team = match.group(1)
    return {'string':sport,'team':team}


def mark_unknown(team):
    return {'extras':{'success':True}}

from fuzzywuzzy import fuzz
from . import utils
import string
import json
import sys
import re
import os

curdir = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(curdir, 'data/yesno.json')) as json_yesno_data:
    yesno_data = json.load(json_yesno_data)
with open(os.path.join(curdir, 'data/verb.json')) as json_verb_data:
    verb_data = json.load(json_verb_data)


def check_input(user_input):
    user_input = utils.remove_punctuation(user_input).upper()
    user_input += " "
    cutoff_ratio = 100
    for yesno in sorted(yesno_data['yesno'], key = lambda yesno: len(yesno['alias']), reverse = True):
        match_ratio = fuzz.partial_ratio(yesno['alias'] + " ", user_input)
        if len(user_input) < 2:
            return {'result': None}
        if match_ratio >= cutoff_ratio:
            if user_input.find(yesno['alias']) <= 1:
                user_input = user_input.replace(yesno['alias'] + " ", '', 1)
            user_input = user_input.rstrip()
            if user_input == "" or user_input == " ":
                if yesno['meaning'] == 'YES':
                    return {'result': 'yes'}
                else:
                    return {'result': 'no'}
            for verb in verb_data['verb']:
                match_r = fuzz.partial_ratio(verb, user_input)
                if match_r >= cutoff_ratio:
                    if yesno['meaning'] == 'YES':
                        return {'result': 'yes_prime', 'user_input': user_input}
                    else:
                        return {'result': 'no_prime', 'user_input': user_input}
            if yesno['meaning'] == 'YES':
                return {'result': 'yes', 'user_input': user_input}
            else:
                return {'result': 'no', 'user_input': user_input}
    return {'result': None}

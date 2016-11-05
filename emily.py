from pandas.io.json import json_normalize
from conf import emily_config as config
from modules import run_command
from fuzzywuzzy import fuzz
from fnmatch import fnmatch
import pandas as pd
import logging
import socket
import string
import random
import json
import sys
import re
import os

pd.options.mode.chained_assignment = None  # default='warn'

logfile = "{}/emily.log".format(config.log_file_path)
logging_level = config.logging_level
numeric_level = getattr(logging, logging_level.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: {}'.format(logging_level))

logging.basicConfig(filename=logfile, filemode='w', format='%(asctime)s | %(levelname)-8s | %(funcName)-15s | %(message)s', datefmt='%H:%M:%S', level=numeric_level)


# Internal Functions

def __load_data__():
    brain_dir = 'brain'
    brain_files = os.listdir(brain_dir)
    print("Loading brain files:\n{}".format(brain_files))
    with open('{}/default.json'.format(brain_dir),'r') as f:
        data = json.loads(f.read())
    results = json_normalize(data['topics'],'categories',['topic'])
    for filename in brain_files:
        if filename != 'default.json':
            with open('{}/{}'.format(brain_dir,filename),'r') as f:
                data = json.loads(f.read())
            results = results.append(json_normalize(data['topics'],'categories',['topic']))
    results = results.reset_index(drop=True)
    logging.log(55,"Loaded {} brain files: {}".format(len(brain_files),brain_files))
    print("-- DATA LOADED --\n")
    return results


def __remove_punctuation__(input_string):
    # string.punctuation evaluates to:
    #   !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    return input_string.translate(string.maketrans("",""),string.punctuation)


# Core Logic

def match_input(user_input,brain,session_vars):
    if session_vars['TOPIC'] != 'NONE':
        match_topics = brain[brain.topic == session_vars['TOPIC']]
        match_patterns = match_topics[match_topics.apply(lambda x: fnmatch(user_input.upper(),x['pattern']),axis=1)]
        if not match_patterns.empty:
            match_patterns['ratio'] = match_patterns.pattern.apply(fuzz.ratio,args=(user_input.upper(),))
            match = match_patterns.loc[match_patterns.ratio.idxmax()]
            logging.debug("Matched: {}".format(match.pattern))
            session_vars = check_stars(match.pattern,user_input,session_vars)
            response,session_vars = parse_template(match.template,brain,session_vars)
            return response,session_vars
    match_topics = brain[brain.topic == 'NONE']
    match_patterns = match_topics[match_topics.apply(lambda x: fnmatch(user_input.upper(),x['pattern']),axis=1)]
    if not match_patterns.empty:
        match_patterns['ratio'] = match_patterns.pattern.apply(fuzz.ratio,args=(user_input.upper(),))
        match = match_patterns.loc[match_patterns.ratio.idxmax()]
        logging.debug("Matched: {}".format(match.pattern))
        session_vars = check_stars(match.pattern,user_input,session_vars)
        response,session_vars = parse_template(match.template,brain,session_vars)
        return response,session_vars
    else:
        return "I'm sorry, I don't know what you're asking.",session_vars


def check_stars(pattern,user_input,session_vars):
    if re.search(r"\*",pattern):
        match_stars = re.compile(r"^{}$".format(pattern.replace('*','([A-Za-z0-9\s]*)')),re.IGNORECASE)
        rematch = match_stars.match(user_input)
        for i in range(1,match_stars.groups+1):
            session_vars['STAR{}'.format(i)] = rematch.group(i)
            logging.debug("Set '{}' to '{}'".format('STAR{}'.format(i),rematch.group(i)))
    return session_vars


def parse_template(template,brain,session_vars):
    has_vars = re.compile(r"^.*\{\{.*\}\}.*$", re.IGNORECASE)
    if template['type'] == 'V':
        # Direct Response
        if 'vars' in template:
            session_vars = set_vars(session_vars,template)
        if has_vars.match(template['response']):
            response = replace_vars(session_vars,template['response'])
        else:
            response = template['response']
        if 'reset' in template:
            session_vars = reset_vars(session_vars,template)
        return response,session_vars
    elif template['type'] == 'U':
        # Redirect
        if 'vars' in template:
            session_vars = set_vars(session_vars,template)
        redirect = replace_vars(session_vars,template['redirect'])
        logging.info("Redirecting with: {}".format(redirect))
        response,session_vars = match_input(redirect,brain,session_vars)
        if 'reset' in template:
            session_vars = reset_vars(session_vars,template)
        return response,session_vars
    elif template['type'] == 'W':
        # Run command
        command = replace_vars(session_vars,template['command'])
        logging.debug("Running Command: {}".format(command))
        if 'presponse' in template:
            presponse = replace_vars(session_vars,template['presponse'])
            printlog(presponse,'EMILY',presponse=True)
        command_result = run_command.run(command)
        logging.debug("Command Result: {}".format(command_result))
        if 'vars' in template:
            session_vars = set_vars(session_vars,template,command_result)
        response = replace_vars(session_vars,template['response'],command_result)
        if 'reset' in template:
            session_vars = reset_vars(session_vars,template)
        return response,session_vars
    elif template['type'] == 'E':
        # Pick random template
        logging.info("Choosing random response")
        template = template['responses'][random.randint(0,len(template['responses'])-1)]
        response,session_vars = parse_template(template,brain,session_vars)
        return response,session_vars
    elif template['type'] == 'WU':
        # Run command with redirect
        command = replace_vars(session_vars,template['command'])
        logging.debug("Running Command: {}".format(command))
        if 'presponse' in template:
            presponse = replace_vars(session_vars,template['presponse'])
            printlog(presponse,'EMILY',presponse=True)
        command_result = run_command.run(command)
        logging.debug("Command Result: {}".format(command_result))
        if 'vars' in template:
            session_vars = set_vars(session_vars,template,command_result)
        redirect = replace_vars(session_vars,template['redirect'],command_result)
        logging.info("Redirecting with: {}".format(redirect))
        response,session_vars = match_input(redirect,brain,session_vars)
        if 'reset' in template:
            session_vars = reset_vars(session_vars,template)
        return response,session_vars
    elif template['type'] == 'Y':
        # Condition
        condition_matched = False
        if 'var' in template:
            if template['var'] in session_vars:
                for condition in template['conditions']:
                    if fnmatch(session_vars[template['var']],condition['condition']):
                        response,session_vars = parse_template(condition['template'],brain,session_vars)
                        condition_matched = True
                        break
        else:
            for condition in template['conditions']:
                check = replace_vars(session_vars,condition['condition'])
                if re.search(r"\{\{.*\}\}",check):
                    break
                if eval(check):
                    response,session_vars = parse_template(condition['template'],brain,session_vars)
                    condition_matched = True
                    break
        if not condition_matched:
            response,session_vars = parse_template(template['fallback'],brain,session_vars)
        return response,session_vars
    else:
        return "ERROR: malformed response template",session_vars


def set_vars(session_vars,template,command_result=None):
    for var in template['vars']:
        if command_result:
            value = replace_vars(session_vars,var['value'],command_result)
        else:
            value = replace_vars(session_vars,var['value'])
        session_vars[var['name']] = value
        logging.info("Set '{}' to '{}'".format(var['name'],value))
    return session_vars


def reset_vars(session_vars,template):
    try:
        for var in template['reset']:
            if var == 'TOPIC':
                session_vars[var] = 'NONE'
                logging.info("Reset 'TOPIC' to 'NONE'")
            else:
                popped_value = session_vars.pop(var)
                logging.info("Removed session variable '{}' with value '{}'".format(var,popped_value))
    except:
        pass
    finally:
        return session_vars


def replace_vars(session_vars,response,command_result=None):
    try:
        replace_results = re.findall(r"\{\{\}\}",response)
        for result in replace_results:
            response = response.replace("{{}}",str(command_result))
        replace_stars = re.findall(r"\{\{(\d*)\}\}",response)
        for star in replace_stars:
            response = response.replace("".join(["{{",star,"}}"]),session_vars["STAR{}".format(star)])
        replace_these = re.findall(r"\{\{([A-Za-z0-9]*)\}\}",response)
        for var in replace_these:
            response = response.replace("".join(["{{",var,"}}"]),session_vars[var])
        return response
    except KeyError:
        return response


def clear_stars(session_vars):
    for key in session_vars.keys():
        if re.search(r"STAR\d*",key):
            null = session_vars.pop(key)
    return session_vars


def printlog(response,speaker,presponse=False):
    if speaker.upper() == 'EMILY':
        if presponse:
            print("\n{}>  {}".format('Emily'.ljust(10),response))
        else:
            print("\n{}>  {}\n".format('Emily'.ljust(10),response))
    logging.info("")
    logging.info("{}: {}".format(speaker.upper(),response))
    logging.info("")

# Main Driver

def start_emily(web_socket=False):
    brain = __load_data__()
    topic = 'NONE'
    session_vars = { 'TOPIC':'NONE' }
    if web_socket:
        session_vars['SOCKET'] = True
        s = socket.socket()
        logging.debug("Socket successfully created")
        port = 8000
        s.bind(('', port))
        logging.debug("socket bound to {}".format(port))
        s.listen(5)
        logging.debug("socket is listening")
    else:
        s = None
    while True:
        if web_socket:
            c, addr = s.accept()
            user_input = c.recv(4096)
            printlog(user_input,'USER')
            response,session_vars = match_input(__remove_punctuation__(user_input),brain,session_vars)
            logging.info("EMILY: {}".format(response))
            c.send(response)
            c.close()
        else:
            if 'NAME' not in session_vars.keys():
                username = 'User'
            else:
                username = session_vars['NAME']
            user_input = raw_input('{}>  '.format(username.ljust(10)))
            printlog(user_input,'USER')
            response,session_vars = match_input(__remove_punctuation__(user_input),brain,session_vars)
            printlog(response,'EMILY')

        session_vars = clear_stars(session_vars)
        if logging_level == 'DEBUG':
            logging.debug("Session Variables:")
            for var in session_vars:
                logging.debug(" * {}: {}".format(var,session_vars[var]))

        if user_input.upper() in ['QUIT','Q','EXIT']:
            if web_socket:
                s.close()
            break


if __name__ == '__main__':
    if len(sys.argv) == 2:
        start_emily(sys.argv[1])
    else:
        start_emily()
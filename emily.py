from pandas.io.json import json_normalize
from emily_conf import emily_config as config
from emily_modules import emily_sessions
from emily_modules import run_command
from datetime import datetime
from fuzzywuzzy import fuzz
from fnmatch import fnmatch
import pandas as pd
import threading
import urlparse
import logging
import socket
import string
import random
import json
import sys
import re
import os

pd.options.mode.chained_assignment = None  # default='warn'


class Emily(threading.Thread):
    def __init__(self,more_brains=[],more_vars={},disable_emily_defaults=False):
        super(Emily, self).__init__()
        try:
            self.s = socket.socket()
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind(('',config.emily_port))
            self.s.listen(5)
            self.already_started = False
            logging = __init_logging__()
            logging.debug("Socket successfully created and listening on port {}".format(config.emily_port))
        except socket.error,err:
            if err.errno == 48:
                logging = __init_logging__(already_started=True)
                logging.debug("Emily already started")
                self.already_started = True
            else:
                print(err)
        finally:
            self.brain = __load_data__(more_brains,disable_emily_defaults)
            self.more_vars = more_vars


    def run(self):
        default_session_vars = config.default_session_vars
        for key in self.more_vars.keys():
            default_session_vars[key] = self.more_vars[key]
        if not self.already_started:
            while True:
                c,addr = self.s.accept()
                user_input = c.recv(4096)
                user_input = json.loads(user_input)
                printlog(user_input['message'],'USER')
                emily_start_time = datetime.now()
                session_id = user_input['session_id']
                if not session_id:
                    session_id = emily_sessions.create_new_session(default_session_vars=default_session_vars)
                    logging.info("New session ID: {}".format(session_id))
                session_vars = emily_sessions.get_session_vars(session_id=session_id)
                # Apply optional filters before sending to brain
                intent,new_input = apply_input_filters(user_input=str(user_input['message']))
                if new_input:
                    response,session_vars = match_input(user_input=__remove_punctuation__(new_input),brain=self.brain,session_vars=session_vars,intent=intent,noprint=True)
                else:
                    response,session_vars = match_input(user_input=__remove_punctuation__(str(user_input['message'])),brain=self.brain,session_vars=session_vars,intent=intent,noprint=True)
                printlog(response,'EMILY',noprint=True)
                c.send(json.dumps({'response':response,'session_id':session_id}))
                c.close()

                emily_response_time = datetime.now() - emily_start_time
                logging.debug("Emily Response Time: {} seconds".format("%.3f" % emily_response_time.total_seconds()))

                session_vars = clear_stars(session_vars)
                if config.logging_level.upper() == 'DEBUG':
                    logging.debug("Session Variables:")
                    for var in session_vars:
                        logging.debug(" * {}: {}".format(var,session_vars[var]))

                if user_input['message'].upper() in ['Q','QUIT','EXIT','BYE']:
                    emily_sessions.remove_session(session_id=session_id)
                    logging.info("Removed session: {}".format(session_id))
                    if emily_sessions.get_session_count() == 0:
                        self.s.close()
                        break
                else:
                    emily_sessions.set_session_vars(session_id=session_id,session_vars=session_vars)

    def send(self,message,session_id=None):
        new_s = socket.socket()
        port = config.emily_port
        new_s.connect(('localhost',port))
        new_s.send(json.dumps({'message':message,'session_id':session_id}))
        response = new_s.recv(4096)
        response = json.loads(response)
        new_s.close()
        return response['response'],response['session_id']


# Internal Functions

def __load_data__(more_brains=[],disable_emily_defaults=False):
    curdir = os.path.dirname(__file__)
    brain_dir = os.path.join(curdir, config.brain_dir)
    if disable_emily_defaults:
        brain_files = more_brains
    else:
        brain_files = ["{}/{}".format(brain_dir,file) for file in os.listdir(brain_dir)]
        brain_files = brain_files + more_brains
    logging.info("Loading brain files: {}".format(brain_files))
    with open('{}/default.json'.format(brain_dir),'r') as f:
        data = json.loads(f.read())
    brain = json_normalize(data['topics'],'categories',['topic'])
    brain['intent'] = data['intent']
    for filename in brain_files:
        if filename != '{}/default.json'.format(brain_dir) and fnmatch(filename,'*.json'):
            try:
                with open(filename,'r') as f:
                    data = json.loads(f.read())
                temp_df = json_normalize(data['topics'],'categories',['topic'])
                temp_df['intent'] = data['intent']
                brain = brain.append(temp_df)
            except:
                print("Failed to load {}".format(filename))
                logging.error("Failed to load {}".format(filename))
                print("Reason: {} - {}".format(sys.exc_info()[0],sys.exc_info()[1]))
                logging.error("Reason: {} - {}".format(sys.exc_info()[0],sys.exc_info()[1]))
    if 'utterances' in brain.columns:
        brain = __expand_utterances__(brain)
    brain = brain.reset_index(drop=True)
    logging.info("Loaded {} brain files".format(len(brain_files)))
    return brain


def __expand_utterances__(brain):
    rows = []
    brain.loc[brain['utterances'].isnull(),['utterances']] = brain.loc[brain['utterances'].isnull(),'utterances'].apply(lambda x: [])
    _ = brain.apply(lambda row: [rows.append([row['intent'],utterance,{'type':'U','redirect':row['pattern']},row['topic'],[]]) for utterance in row.utterances], axis=1)
    brain = brain.append(pd.DataFrame(rows, columns=['intent','pattern','template','topic','utterances']))
    brain.drop('utterances',axis=1,inplace=True)
    return brain


def __init_logging__(already_started=False):
    curdir = os.path.dirname(__file__)
    logfile = os.path.join(curdir, config.log_file)
    logging_level = config.logging_level
    numeric_level = getattr(logging, logging_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(logging_level))
    
    if not already_started:
        logging.basicConfig(filename=logfile, filemode='w', format='%(asctime)s | %(levelname)-8s | %(funcName)-15s | %(message)s', datefmt='%H:%M:%S', level=numeric_level)
    else:
        logging.basicConfig(filename=logfile, format='%(asctime)s | %(levelname)-8s | %(funcName)-15s | %(message)s', datefmt='%H:%M:%S', level=numeric_level)
    return logging


def __remove_punctuation__(input_string):
    # string.punctuation evaluates to:
    #   !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    return input_string.translate(string.maketrans("",""),string.punctuation)


# Core Logic

def match_input(user_input,brain,session_vars,intent=None,noprint=False):
    if intent:
        intent_brain = brain[(brain.intent == intent) | (brain.intent == 'DEFAULT')]
    else:
        intent_brain = brain
    if session_vars['topic'] != 'NONE':
        match_topics = intent_brain[intent_brain.topic == session_vars['topic']]
        match_patterns = match_topics[match_topics.apply(lambda x: fnmatch(user_input.upper(),x['pattern']),axis=1)]
        if match_patterns.empty:
            match_topics = intent_brain[intent_brain.topic == 'NONE']
            match_patterns = match_topics[match_topics.apply(lambda x: fnmatch(user_input.upper(),x['pattern']),axis=1)]
    else:
        match_topics = intent_brain[intent_brain.topic == 'NONE']
        match_patterns = match_topics[match_topics.apply(lambda x: fnmatch(user_input.upper(),x['pattern']),axis=1)]
    if match_patterns.empty:
        response = "I'm sorry, I don't know what you're asking."
        return response,session_vars
    match_patterns['ratio'] = match_patterns.pattern.apply(fuzz.ratio,args=(user_input.upper(),))
    match = match_patterns.loc[match_patterns.ratio.idxmax()]
    logging.debug("Matched: {}".format(match.pattern))
    session_vars = check_stars(match.pattern,user_input,session_vars)
    response,session_vars = parse_template(template=match.template,brain=intent_brain,session_vars=session_vars,noprint=noprint)
    return response,session_vars



def check_stars(pattern,user_input,session_vars):
    if re.search(r"\*",pattern):
        match_stars = re.compile(r"^{}$".format(pattern.replace('*','([A-Za-z0-9\s!\.\':]*)')),re.IGNORECASE)
        rematch = match_stars.match(user_input)
        for i in range(1,match_stars.groups+1):
            session_vars['star{}'.format(i)] = rematch.group(i)
            logging.debug("Set '{}' to '{}'".format('star{}'.format(i),rematch.group(i)))
    return session_vars


def parse_template(template,brain,session_vars,noprint=False):
    has_vars = re.compile(r"^.*\{\{.*\}\}.*$", re.IGNORECASE)
    if template['type'] == 'V':
        # Direct Response
        if 'vars' in template:
            session_vars = set_vars(session_vars,template)
        if 'preset' in template:
            session_vars = reset_vars(session_vars,template,key='preset')
        if has_vars.match(template['response']):
            response = replace_vars(session_vars,template['response'])
        else:
            response = template['response']
        if 'reset' in template:
            session_vars = reset_vars(session_vars,template,key='reset')
        return response,session_vars
    elif template['type'] == 'U':
        # Redirect
        if 'vars' in template:
            session_vars = set_vars(session_vars,template)
        if 'preset' in template:
            session_vars = reset_vars(session_vars,template,key='preset')
        redirect = replace_vars(session_vars,template['redirect'])
        logging.info("Redirecting with: {}".format(redirect))
        response,session_vars = match_input(user_input=redirect,brain=brain,session_vars=session_vars,noprint=noprint)
        if 'reset' in template:
            session_vars = reset_vars(session_vars,template,key='reset')
        return response,session_vars
    elif template['type'] == 'W':
        # Run command
        command = replace_vars(session_vars,template['command'])
        logging.debug("Running Command: {}".format(command))
        if 'preset' in template:
            session_vars = reset_vars(session_vars,template,key='preset')
        if not noprint and 'presponse' in template:
            presponse = replace_vars(session_vars,template['presponse'])
            printlog(presponse,'EMILY',presponse=True)
        command_result = run_command.run(command)
        logging.debug("Command Result: {}".format(command_result))
        if 'vars' in template:
            session_vars = set_vars(session_vars,template,command_result)
        response = replace_vars(session_vars,template['response'],command_result)
        if 'reset' in template:
            session_vars = reset_vars(session_vars,template,key='reset')
        return response,session_vars
    elif template['type'] == 'E':
        # Pick random template
        logging.info("Choosing random response")
        template = template['responses'][random.randint(0,len(template['responses'])-1)]
        response,session_vars = parse_template(template=template,brain=brain,session_vars=session_vars,noprint=noprint)
        return response,session_vars
    elif template['type'] == 'WU':
        # Run command with redirect
        command = replace_vars(session_vars,template['command'])
        logging.debug("Running Command: {}".format(command))
        if 'preset' in template:
            session_vars = reset_vars(session_vars,template,key='preset')
        if not noprint and 'presponse' in template:
            presponse = replace_vars(session_vars,template['presponse'])
            printlog(presponse,'EMILY',presponse=True)
        command_result = run_command.run(command)
        logging.debug("Command Result: {}".format(command_result))
        if 'vars' in template:
            session_vars = set_vars(session_vars,template,command_result)
        redirect = replace_vars(session_vars,template['redirect'],command_result)
        logging.info("Redirecting with: {}".format(redirect))
        response,session_vars = match_input(user_input=redirect,brain=brain,session_vars=session_vars,noprint=noprint)
        if 'reset' in template:
            session_vars = reset_vars(session_vars,template,key='reset')
        return response,session_vars
    elif template['type'] == 'Y':
        # Condition
        condition_matched = False
        if 'var' in template:
            if template['var'] in session_vars:
                for condition in template['conditions']:
                    if fnmatch(session_vars[template['var']],condition['pattern']):
                        response,session_vars = parse_template(template=condition['template'],brain=brain,session_vars=session_vars,noprint=noprint)
                        condition_matched = True
                        break
        else:
            for condition in template['conditions']:
                check = replace_vars(session_vars,condition['pattern'])
                if re.search(r"\{\{.*\}\}",check):
                    break
                if eval(check):
                    response,session_vars = parse_template(template=condition['template'],brain=brain,session_vars=session_vars,noprint=noprint)
                    condition_matched = True
                    break
        if not condition_matched:
            response,session_vars = parse_template(template=template['fallback'],brain=brain,session_vars=session_vars,noprint=noprint)
        return response,session_vars
    else:
        return "ERROR: malformed response template",session_vars


def set_vars(session_vars,template,command_result=None):
    for var in template['vars']:
        if command_result:
            value = replace_vars(session_vars,var['value'],command_result)
        else:
            value = replace_vars(session_vars,var['value'])
        session_vars[var['name'].lower()] = value
        logging.info("Set '{}' to '{}'".format(var['name'].lower(),value))
    return session_vars


def reset_vars(session_vars,template,key='reset'):
    try:
        for var in template[key]:
            if var.lower() == 'topic':
                session_vars[var.lower()] = 'NONE'
                logging.info("Reset 'topic' to 'NONE'")
            else:
                popped_value = session_vars.pop(var.lower())
                logging.info("Removed session variable '{}' with value '{}'".format(var.lower(),popped_value))
    except:
        pass
    finally:
        return session_vars


def replace_vars(session_vars,response,command_result=None):
    try:
        if command_result:
            if command_result['success']:
                replace_results = re.findall(r"\{\{\}\}",response)
                for result in replace_results:
                    response = response.replace("{{}}",str(command_result['response']))
                if isinstance(command_result['response'],dict):
                    replace_these = re.findall(r"\{\{([A-Za-z0-9_]*)\}\}",response)
                    for var in replace_these:
                        try:
                            response = response.replace("".join(["{{",var.lower(),"}}"]),str(command_result['response'][var.lower()]))
                        except KeyError:
                            pass
            else:
                response = command_result['response']
        replace_stars = re.findall(r"\{\{(\d*)\}\}",response)
        for star in replace_stars:
            response = response.replace("".join(["{{",star,"}}"]),session_vars["star{}".format(star)])
        replace_these = re.findall(r"\{\{([A-Za-z0-9_]*)\}\}",response)
        for var in replace_these:
            response = response.replace("".join(["{{",var.lower(),"}}"]),str(session_vars[var.lower()]))
        return response
    except KeyError:
        return response


def clear_stars(session_vars):
    for key in session_vars.keys():
        if re.search(r"star\d*",key):
            null = session_vars.pop(key)
    return session_vars


def printlog(response,speaker,presponse=False,noprint=False):
    if speaker.upper() == 'EMILY' and not noprint:
        if presponse:
            print("\n{}>  {}".format('Emily'.ljust(10),response))
        else:
            print("\n{}>  {}\n".format('Emily'.ljust(10),response))
    logging.info("")
    logging.info("{}: {}".format(speaker.upper(),response))
    logging.info("")


def apply_input_filters(user_input):
    if config.intent_filter:
        logging.debug("Applying this intent filter to user input: {}".format(config.intent_command))
        intent_command = config.intent_command.replace('user_input',user_input)
        command_result = run_command.run(intent_command)
        if command_result['success']:
            logging.info("Determined intent: {}".format(command_result['response']))
            intent = command_result['response']
        else:
            logging.error("Failed to apply intent filter: {}".format(intent_command))
            intent = None
    else:
        intent = None
    if config.preformat_filter:
        logging.debug("Applying this preformat filter to user input: {}".format(config.preformat_command))
        preformat_command = config.preformat_command.replace('user_input',user_input)
        command_result = run_command.run(preformat_command)
        if command_result['success']:
            logging.info("Preformatted input to: {}".format(command_result['response']))
            new_input = command_result['response']
        else:
            logging.error("Failed to apply preformat filter: {}".format(preformat_command))
            new_input = None
    else:
        new_input = None
    return intent,new_input


def parse_http_input(input_text):
    verb,path = get_http_verb(input_text)
    if verb == 'POST':
        message = None
        post_vars = get_post_vars(input_text)
    elif verb == 'GET':
        if path.lower() == '/health':
            message = 'SUCCESS'
        else:
            message = None
        post_vars = None
    logging.debug("Message: {}".format(message))
    return message,post_vars


def get_http_verb(input_text):
    http_verb_line = input_text.split("\n")[0]
    http_verb = http_verb_line.split(" ")[0]
    http_path = http_verb_line.split(" ")[1]
    logging.debug("Verb: {}, Path: {}".format(http_verb,http_path))
    return http_verb,http_path


def get_post_vars(post_text):
    post_vars = {}
    post_var_string = post_text.split("\n")[-1]
    post_vars_temp = urlparse.parse_qs(post_var_string)
    logging.debug("POST variables: {}".format(json.dumps(post_vars_temp)))
    for var in post_vars_temp:
        var_value = post_vars_temp[var][0]
        if var == 'session_id':
            post_vars[var] = int(var_value)
        else:
            post_vars[var] = var_value
    return post_vars


# Main Driver

def start_emily(web_socket=False):
    logging = __init_logging__()
    brain = __load_data__()
    session_vars = { 'topic':'NONE' }
    if web_socket:
        s = socket.socket()
        logging.debug("Socket successfully created")
        s.bind(('', config.emily_port))
        logging.debug("socket bound to {}".format(config.emily_port))
        s.listen(5)
        logging.debug("socket is listening")
    else:
        s = None
        print("")
    while True:
        if web_socket:
            c, addr = s.accept()
            user_input = c.recv(4096)
            printlog(user_input,'USER')
            emily_start_time = datetime.now()
            http_message,post_vars = parse_http_input(user_input)
            if http_message:
                response_body = http_message
            else:
                # If this is a new session (no id provided) start new session
                if 'session_id' not in post_vars:
                    post_vars['session_id'] = emily_sessions.create_new_session()
                    logging.info("New session ID: {}".format(post_vars['session_id']))
                # Get session vars by id
                session_vars = emily_sessions.get_session_vars(session_id=post_vars['session_id'])
                # Apply optional filters before sending to brain
                intent,new_input = apply_input_filters(user_input=post_vars['message'])
                if new_input:
                    response,session_vars = match_input(user_input=__remove_punctuation__(new_input),brain=brain,session_vars=session_vars,intent=intent,noprint=True)
                else:
                    response,session_vars = match_input(user_input=__remove_punctuation__(post_vars['message']),brain=brain,session_vars=session_vars,intent=intent,noprint=True)
                printlog(response,'EMILY',noprint=True)
                response_body = json.dumps({'response':response,'session_id':post_vars['session_id']})
            response_headers = {
                    'Content-Type': 'text/html; encoding=utf8',
                    'Content-Length': len(response_body),
                    'Connection': 'close',
                }
            response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in response_headers.iteritems())
            # Reply as HTTP/1.1 server, saying "HTTP OK" (code 200).
            response_proto = 'HTTP/1.1'
            response_status = '200'
            response_status_text = 'OK' # this can be random
            # sending all this stuff
            c.send('%s %s %s' % (response_proto, response_status, response_status_text))
            c.send(response_headers_raw)
            c.send('\n') # to separate headers from body
            c.send(response_body)
            c.close()
        else:
            if 'name' not in session_vars.keys():
                username = 'User'
            else:
                username = session_vars['name']
            user_input = raw_input('{}>  '.format(username.ljust(10)))
            printlog(user_input,'USER')
            emily_start_time = datetime.now()
            # Apply optional filters before sending to brain
            intent,new_input = apply_input_filters(user_input=user_input)
            if new_input:
                response,session_vars = match_input(user_input=__remove_punctuation__(new_input),brain=brain,session_vars=session_vars,intent=intent)
            else:
                response,session_vars = match_input(user_input=__remove_punctuation__(user_input),brain=brain,session_vars=session_vars,intent=intent)
            printlog(response,'EMILY')

        emily_response_time = datetime.now() - emily_start_time
        logging.debug("Emily Response Time: {} seconds".format("%.3f" % emily_response_time.total_seconds()))

        session_vars = clear_stars(session_vars)
        if config.logging_level.upper() == 'DEBUG':
            logging.debug("Session Variables:")
            for var in session_vars:
                logging.debug(" * {}: {}".format(var,session_vars[var]))

        if web_socket:
            if post_vars:
                if post_vars['message'].upper() in ['QUIT','Q','EXIT','BYE']:
                    emily_sessions.remove_session(session_id=post_vars['session_id'])
                    logging.info("Removed session: {}".format(post_vars['session_id']))
                else:
                    emily_sessions.set_session_vars(session_id=post_vars['session_id'],session_vars=session_vars)
        elif user_input.upper() in ['QUIT','Q','EXIT','BYE']:
            break


if __name__ == '__main__':
    if len(sys.argv) == 2:
        start_emily(sys.argv[1])
    else:
        start_emily()
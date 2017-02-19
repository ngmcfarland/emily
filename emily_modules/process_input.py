from fuzzywuzzy import fuzz
from fnmatch import fnmatch
import conversations
import run_command
import variables
import logging
import random
import sys
import re
import os


def match_input(user_input,brain,session_vars,nodes=None,intent=None,noprint=False):
    if 'next_node' not in session_vars or session_vars['next_node'] is None:
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
        session_vars = variables.check_stars(pattern=match.pattern,user_input=user_input,session_vars=session_vars)
        response,session_vars = parse_template(template=match.template,brain=intent_brain,session_vars=session_vars,user_input=user_input,nodes=nodes,noprint=noprint)
        session_vars = variables.clear_stars(session_vars=session_vars)
    else:
        responses,session_vars = conversations.process_node(node=nodes[session_vars['next_node']],nodes=nodes,session_vars=session_vars,responses=[],user_input=user_input)
        # Right now, process_node returns a list of responses. May use this globally later, but for now, I'm just joining the responses to make one.
        response = " ".join(responses)
    return response,session_vars


def parse_template(template,brain,session_vars,user_input,nodes=None,noprint=False):
    has_vars = re.compile(r"^.*\{\{.*\}\}.*$", re.IGNORECASE)
    if template['type'] == 'V':
        # Direct Response
        if 'vars' in template:
            session_vars = variables.set_vars(session_vars,template)
        if 'preset' in template:
            session_vars = variables.reset_vars(session_vars,template,key='preset')
        if has_vars.match(template['response']):
            response = variables.replace_vars(session_vars,template['response'])
        else:
            response = template['response']
        if 'reset' in template:
            session_vars = variables.reset_vars(session_vars,template,key='reset')
        return response,session_vars
    elif template['type'] == 'U':
        # Redirect
        if 'vars' in template:
            session_vars = variables.set_vars(session_vars,template)
        if 'preset' in template:
            session_vars = variables.reset_vars(session_vars,template,key='preset')
        redirect = variables.replace_vars(session_vars,template['redirect'])
        logging.info("Redirecting with: {}".format(redirect))
        response,session_vars = match_input(user_input=redirect,brain=brain,session_vars=session_vars,nodes=nodes,noprint=noprint)
        if 'reset' in template:
            session_vars = variables.reset_vars(session_vars,template,key='reset')
        return response,session_vars
    elif template['type'] == 'W':
        # Run command
        command = variables.replace_vars(session_vars,template['command'])
        logging.debug("Running Command: {}".format(command))
        if 'preset' in template:
            session_vars = variables.reset_vars(session_vars,template,key='preset')
        if not noprint and 'presponse' in template:
            presponse = variables.replace_vars(session_vars,template['presponse'])
            printlog(presponse,'EMILY',presponse=True)
        command_result = run_command.run(command)
        logging.debug("Command Result: {}".format(command_result))
        if 'vars' in template:
            session_vars = variables.set_vars(session_vars,template,command_result)
        response = variables.replace_vars(session_vars,template['response'],command_result)
        if 'reset' in template:
            session_vars = variables.reset_vars(session_vars,template,key='reset')
        return response,session_vars
    elif template['type'] == 'E':
        # Pick random template
        logging.info("Choosing random response")
        template = template['responses'][random.randint(0,len(template['responses'])-1)]
        response,session_vars = parse_template(template=template,brain=brain,session_vars=session_vars,user_input=user_input,nodes=nodes,noprint=noprint)
        return response,session_vars
    elif template['type'] == 'WU':
        # Run command with redirect
        command = variables.replace_vars(session_vars,template['command'])
        logging.debug("Running Command: {}".format(command))
        if 'preset' in template:
            session_vars = variables.reset_vars(session_vars,template,key='preset')
        if not noprint and 'presponse' in template:
            presponse = variables.replace_vars(session_vars,template['presponse'])
            printlog(presponse,'EMILY',presponse=True)
        command_result = run_command.run(command)
        logging.debug("Command Result: {}".format(command_result))
        if 'vars' in template:
            session_vars = variables.set_vars(session_vars,template,command_result)
        redirect = variables.replace_vars(session_vars,template['redirect'],command_result)
        logging.info("Redirecting with: {}".format(redirect))
        response,session_vars = match_input(user_input=redirect,brain=brain,session_vars=session_vars,nodes=nodes,noprint=noprint)
        if 'reset' in template:
            session_vars = variables.reset_vars(session_vars,template,key='reset')
        return response,session_vars
    elif template['type'] == 'Y':
        # Condition
        condition_matched = False
        if 'var' in template:
            if template['var'] in session_vars:
                for condition in template['conditions']:
                    if fnmatch(session_vars[template['var']],condition['pattern']):
                        response,session_vars = parse_template(template=condition['template'],brain=brain,session_vars=session_vars,user_input=user_input,nodes=nodes,noprint=noprint)
                        condition_matched = True
                        break
        else:
            for condition in template['conditions']:
                check = variables.replace_vars(session_vars,condition['pattern'])
                if re.search(r"\{\{.*\}\}",check):
                    break
                if eval(check):
                    response,session_vars = parse_template(template=condition['template'],brain=brain,session_vars=session_vars,user_input=user_input,nodes=nodes,noprint=noprint)
                    condition_matched = True
                    break
        if not condition_matched:
            response,session_vars = parse_template(template=template['fallback'],brain=brain,session_vars=session_vars,user_input=user_input,nodes=nodes,noprint=noprint)
        return response,session_vars
    elif template['type'] == 'C':
        # Send to conversations
        if 'vars' in template:
            session_vars = variables.set_vars(session_vars,template)
        if 'preset' in template:
            session_vars = variables.reset_vars(session_vars,template,key='preset')
        next_node = variables.replace_vars(session_vars,template['node'])
        logging.info("Directing to conversation node: {}".format(next_node))
        responses,session_vars = conversations.process_node(node=nodes[next_node],nodes=nodes,session_vars=session_vars,responses=[],user_input=user_input)
        # Right now, process_node returns a list of responses. May use this globally later, but for now, I'm just joining the responses to make one.
        response = " ".join(responses)
        if 'reset' in template:
            session_vars = variables.reset_vars(session_vars,template,key='reset')
        return response,session_vars
    else:
        return "ERROR: malformed response template",session_vars
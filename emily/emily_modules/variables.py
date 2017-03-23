import logging
import sys
import re
import os


def check_stars(pattern,user_input,session_vars):
    if re.search(r"\*",pattern):
        match_stars = re.compile(r"^{}$".format(pattern.replace('*','(.*)')),re.IGNORECASE)
        rematch = match_stars.match(user_input)
        for i in range(1,match_stars.groups+1):
            session_vars['star{}'.format(i)] = rematch.group(i)
            logging.debug("Set '{}' to '{}'".format('star{}'.format(i),rematch.group(i)))
    return session_vars


def clear_stars(session_vars):
    pop_these = []
    for key in session_vars:
        if re.search(r"star\d*",key):
            pop_these.append(key)
    for key in pop_these:
        null = session_vars.pop(key)
    return session_vars


def set_vars(session_vars,template):
    for var in template['vars']:
        value = replace_vars(session_vars,var['value'])
        session_vars[var['name'].lower()] = value
        logging.info("Set '{}' to '{}'".format(var['name'].lower(),value))
    return session_vars


def reset_vars(session_vars,template,key='reset'):
    try:
        if len(template[key]) == 1 and template[key][0].upper() == 'ALL':
            try:
                logging.info("Resetting session variables to defaults")
                temp_session_vars = session_vars['default_session_vars']
                session_vars = dict(temp_session_vars)
                session_vars['default_session_vars'] = dict(temp_session_vars)
            except KeyError:
                pass
        else:
            for var in template[key]:
                try:
                    if var.lower() == 'conversation':
                        session_vars[var.lower()] = 'default'
                        logging.info("Reset 'conversation' to 'default'")
                    else:
                        popped_value = session_vars.pop(var.lower())
                        logging.info("Removed session variable '{}' with value '{}'".format(var.lower(),popped_value))
                except KeyError:
                    pass
    except:
        pass
    finally:
        return session_vars


def replace_vars(session_vars,response):
    try:
        replace_stars = re.findall(r"\{(\d*)\}",response)
        for star in replace_stars:
            response = response.replace("".join(["{",star,"}"]),session_vars["star{}".format(star)])
        replace_these = re.findall(r"\{([A-Za-z0-9_]*)\}",response)
        for var in replace_these:
            response = response.replace("".join(["{",var.lower(),"}"]),str(session_vars[var.lower()]))
        return response
    except KeyError:
        return response
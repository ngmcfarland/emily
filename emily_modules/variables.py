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
    for key in session_vars.keys():
        if re.search(r"star\d*",key):
            null = session_vars.pop(key)
    return session_vars


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
        if len(template[key]) == 1 and template[key][0].upper() == 'ALL':
            try:
                logging.info("Resetting session variables to defaults")
                session_vars = session_vars['default_session_vars']
            except KeyError:
                pass
        else:
            for var in template[key]:
                try:
                    if var.lower() == 'topic':
                        session_vars[var.lower()] = 'NONE'
                        logging.info("Reset 'topic' to 'NONE'")
                    else:
                        popped_value = session_vars.pop(var.lower())
                        logging.info("Removed session variable '{}' with value '{}'".format(var.lower(),popped_value))
                except KeyError:
                    pass
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
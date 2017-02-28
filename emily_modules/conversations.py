from . import yes_no_parser,run_command
import logging
import random
import json
import sys
import re
import os


def process_node(node,nodes,session_vars,responses,user_input=None):
    response = 'Not yet set'
    session_vars['next_node'] = None
    if node['node_type'] == 'response':
        response = node['responses'][random.randint(0,len(node['responses'])-1)] if len(node['responses']) > 1 else node['responses'][0]
        replace_vars = re.findall(r"\{([^\{\}]*)\}",response,re.IGNORECASE)
        for var in replace_vars:
            try:
                response = re.sub(r"\{"+var+r"\}",session_vars[var],response,re.IGNORECASE)
            except KeyError:
                pass
        responses.append(response)
        session_vars['next_node'] = node['next_node'] if 'next_node' in node else None
        if session_vars['next_node'] is not None and nodes[session_vars['next_node']]['node_type'] in ['response','error']:
            responses,session_vars = process_node(node=nodes[session_vars['next_node']],nodes=nodes,session_vars=session_vars,responses=responses,user_input=user_input)
    elif node['node_type'] == 'error':
        response = node['responses'][random.randint(0,len(node['responses'])-1)] if len(node['responses']) > 1 else node['responses'][0]
        replace_vars = re.findall(r"\{([^\{\}]*)\}",response,re.IGNORECASE)
        for var in replace_vars:
            try:
                response = re.sub(r"\{"+var+r"\}",session_vars[var],response,re.IGNORECASE)
            except KeyError:
                pass
        responses.append(response)
    elif node['node_type'] == 'simple_logic':
        command = node['command'].replace('{user_input}',user_input) if user_input is not None else node['command']
        replace_vars = re.findall(r"\{([^\{\}]*)\}",command,re.IGNORECASE)
        for var in replace_vars:
            try:
                command = re.sub(r"\{"+var+r"\}",session_vars[var],command,re.IGNORECASE)
            except KeyError:
                pass
        result = run_command.run(command)
        command_response = result['response']
        if result['success']:
            for var in command_response:
                if isinstance(command_response[var],dict):
                    session_vars[var] = json.dumps(command_response[var])
                else:
                    session_vars[var] = command_response[var]
            responses,session_vars = process_node(node=nodes[node['next_node']],nodes=nodes,session_vars=session_vars,responses=responses,user_input=user_input)
        else:
            response = "Failed to run command: {}".format(command)
            session_vars['next_node'] = node['error_node'] if 'error_node' in node else None
    elif node['node_type'] == 'yes_no_logic':
        result = yes_no_parser.check_input(user_input=user_input)
        if result['result'] == 'yes':
            responses,session_vars = process_node(node=nodes[node['yes_node']],nodes=nodes,session_vars=session_vars,responses=responses,user_input=user_input)
        elif result['result'] == 'yes_prime':
            responses,session_vars = process_node(node=nodes[node['yes_prime_node']],nodes=nodes,session_vars=session_vars,responses=responses,user_input=result['user_input'])
        elif result['result'] == 'no':
            responses,session_vars = process_node(node=nodes[node['no_node']],nodes=nodes,session_vars=session_vars,responses=responses,user_input=user_input)
        elif result['result'] == 'no_prime':
            responses,session_vars = process_node(node=nodes[node['no_prime_node']],nodes=nodes,session_vars=session_vars,responses=responses,user_input=result['user_input'])
        else:
            responses,session_vars = process_node(node=nodes[node['unknown_node']],nodes=nodes,session_vars=session_vars,responses=responses,user_input=user_input)
    elif node['node_type'] == 'string_logic':
        command = node['command'].replace('{user_input}',user_input) if user_input is not None else node['command']
        replace_vars = re.findall(r"\{([^\{\}]*)\}",command,re.IGNORECASE)
        for var in replace_vars:
            try:
                command = re.sub(r"\{"+var+r"\}",session_vars[var],command,re.IGNORECASE)
            except KeyError:
                pass
        result = run_command.run(command)
        command_response = result['response']
        if result['success']:
            for var in command_response:
                if isinstance(command_response[var],dict):
                    session_vars[var] = json.dumps(command_response[var])
                else:
                    session_vars[var] = command_response[var]
            if command_response['string'].lower() in node.keys():
                responses,session_vars = process_node(node=nodes[node[command_response['string'].lower()]],nodes=nodes,session_vars=session_vars,responses=responses,user_input=user_input)
            else:
                responses,session_vars = process_node(node=nodes[node['unknown_node']],nodes=nodes,session_vars=session_vars,responses=responses,user_input=user_input)
        else:
            response = "Failed to run command: {}".format(command)
            session_vars['next_node'] = node['error_node'] if 'error_node' in node else None
            responses.append(response)
    else:
        response = "Unrecognized node_type: {}".format(node['node_type'])
        responses.append(response)
    return responses,session_vars

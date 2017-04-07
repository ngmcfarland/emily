from . import yes_no_parser,run_command,variables
import logging
import random
import json
import sys
import re
import os


def process_node(node_tag,nodes,session_vars,responses,user_input=None):
    node = nodes[node_tag]
    conversation = 'default'
    logging.debug("Processing {} node: {}".format(node['node_type'],node_tag))
    if 'vars' in node:
        session_vars = variables.set_vars(session_vars,node)
    if 'preset' in node:
        session_vars = variables.reset_vars(session_vars,node,key='preset')
    if node['node_type'] == 'response':
        responses,session_vars,success = response_node(node=node,session_vars=session_vars,responses=responses)
        if success:
            session_vars['next_node'] = node['next_node'] if 'next_node' in node else None
            if 'chain' not in node or node['chain'] == True:
                if session_vars['next_node'] is not None and nodes[session_vars['next_node']]['node_type'] == 'response':
                    responses,session_vars,conversation = process_node(node_tag=session_vars['next_node'],nodes=nodes,session_vars=session_vars,responses=responses,user_input=user_input)
    elif node['node_type'] == 'router':
        next_node,success = router_node(node=node)
        if success and next_node is not None:
            responses,session_vars,conversation = process_node(node_tag=next_node,nodes=nodes,session_vars=session_vars,responses=responses,user_input=user_input)
    elif node['node_type'] == 'simple_logic':
        session_vars,success = simple_logic_node(node=node,session_vars=session_vars,user_input=user_input)
        if success:
            session_vars['next_node'] = node['next_node'] if 'next_node' in node else None
            if ('chain' not in node or node['chain'] == True) and session_vars['next_node'] is not None:
                responses,session_vars,conversation = process_node(node_tag=session_vars['next_node'],nodes=nodes,session_vars=session_vars,responses=responses,user_input=user_input)
    elif node['node_type'] == 'string_logic':
        next_node,success = string_logic_node(node=node,session_vars=session_vars,user_input=user_input)
        if success and next_node is not None:
            responses,session_vars,conversation = process_node(node_tag=next_node,nodes=nodes,session_vars=session_vars,responses=responses,user_input=user_input)
    elif node['node_type'] == 'yes_no_logic':
        next_node,success = yes_no_logic_node(node=node,user_input=user_input)
        if success and next_node is not None:
            responses,session_vars,conversation = process_node(node_tag=next_node,nodes=nodes,session_vars=session_vars,responses=responses,user_input=user_input)
    else:
        response = "Unrecognized node_type: {}".format(node['node_type'])
        responses.append(response)
        success = False
    if not success:
        if 'error_node' in node:
            responses,session_vars = process_node(node_tag=node['error_node'],nodes=nodes,session_vars=session_vars,responses=responses,user_input=user_input)
        else:
            response = "Failed to process node: {}".format(node_tag)
            responses.append(response)
        conversation = 'default'
    else:
        conversation = node['conversation'] if 'conversation' in node else conversation
    if 'reset' in node:
        session_vars = variables.reset_vars(session_vars,node,key='reset')
    return responses,session_vars,conversation


def response_node(node,session_vars,responses):
    try:
        success = False
        logging.debug("Getting random response from: {}".format(node['responses']))
        response = node['responses'][random.randint(0,len(node['responses'])-1)]
        response = variables.replace_vars(session_vars=session_vars,response=response)
        responses.append(response)
        success = True
    except KeyError as e:
        logging.error("Response node missing attribute: {}".format(e))
    finally:
        return responses,session_vars,success


def router_node(node):
    try:
        success = False
        next_node = None
        if 'node_options' in node:
            logging.debug("Getting random node from: {}".format(node['node_options']))
            next_node = node['node_options'][random.randint(0,len(node['node_options'])-1)]
        else:
            next_node = node['next_node']
        success = True
    except KeyError as e:
        logging.error("Random node missing attribute: {}".format(e))
    finally:
        return next_node,success


def simple_logic_node(node,session_vars,user_input):
    try:
        success = False
        if '{user_input}' in node['command'] and user_input is not None:
            command = node['command'].replace('{user_input}',session_vars['user_input'])
        else:
            command = node['command']
        command = variables.replace_vars(session_vars=session_vars,response=command)
        result = run_command.run(command)
        command_response = result['response']
        if result['success']:
            if isinstance(command_response,dict):
                for var in command_response:
                    if isinstance(command_response[var],dict):
                        session_vars[var] = json.dumps(command_response[var])
                    else:
                        session_vars[var] = command_response[var]
            else:
                session_vars['command_response'] = command_response
            success = True
    except KeyError as e:
        logging.error("Simple logic node missing attribute: {}".format(e))
    finally:
        return session_vars,success


def yes_no_logic_node(node,user_input):
    try:
        success = False
        next_node = None
        result = yes_no_parser.check_input(user_input=user_input)
        logging.debug("Yes/No Result: {}".format(result['result']))
        if result['result'] == 'yes':
            next_node = node['yes_node']
        elif result['result'] == 'yes_prime':
            next_node = node['yes_prime_node']
        elif result['result'] == 'no':
            next_node = node['no_node']
        elif result['result'] == 'no_prime':
            next_node = node['no_prime_node']
        else:
            next_node = node['unknown_node']
        success = True
    except KeyError as e:
        logging.error("Yes/No logic node missing attribute: {}".format(e))
    finally:
        return next_node,success


def string_logic_node(node,session_vars,user_input):
    try:
        success = False
        next_node = None
        if '{user_input}' in node['command'] and user_input is not None:
            command = node['command'].replace('{user_input}',session_vars['user_input'])
        else:
            command = node['command']
        command = variables.replace_vars(session_vars=session_vars,response=command)
        result = run_command.run(command)
        command_response = result['response']
        if result['success'] and 'string' in command_response:
            logging.debug("String result: {}".format(command_response['string']))
            for var in command_response:
                if isinstance(command_response[var],dict):
                    session_vars[var] = json.dumps(command_response[var])
                else:
                    session_vars[var] = command_response[var]
            if command_response['string'].lower() in node.keys():
                next_node = node[command_response['string'].lower()]
            else:
                next_node = node['unknown_node']
            success = True
    except KeyError as e:
        logging.error("String logic node missing attribute: {}".format(e))
    finally:
        return next_node,success
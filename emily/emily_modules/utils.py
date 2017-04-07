from fuzzywuzzy import fuzz
from . import run_command
import logging
import string
import json
import yaml
import sys
import re
import os


def load_data(brain_files=[],brain_table=None,source='LOCAL',region='us-east-1'):
    nodes = {}
    patterns = {}
    if source.upper() == 'LOCAL':
        brain_files = [file for file in brain_files if file.lower().endswith('.json') or file.lower().endswith('.yaml')]
        logging.info("Loading brain files: {}".format(brain_files))
        brain_count = len(brain_files)
        for filename in brain_files:
            try:
                if filename.lower().endswith('.json'):
                    with open(filename,'r') as f:
                        data = json.loads(f.read())
                elif filename.lower().endswith('.yaml'):
                    with open(filename,'r') as f:
                        data = yaml.load(f.read())
                nodes,patterns = load_brain(nodes=nodes,patterns=patterns,data=data)
            except:
                print("Failed to load {}".format(filename))
                logging.error("Failed to load {}".format(filename))
                print("Reason: {} - {}".format(sys.exc_info()[0],sys.exc_info()[1]))
                logging.error("Reason: {} - {}".format(sys.exc_info()[0],sys.exc_info()[1]))
                brain_count -= 1
        logging.info("Loaded {} brain files".format(brain_count))
    elif source.upper() == 'DYNAMODB':
        try:
            import boto3
            client = boto3.client('dynamodb')
            response = client.scan(TableName=brain_table)
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                brain_count = response['Count']
                for brain in response['Items']:
                    data = json.loads(brain['brain'])
                    nodes,pattern = load_brain(nodes=nodes,patterns=patterns,data=data)
            else:
                logging.error("Failed to scan DynamoDB table: {}".format(brain_table))
        except:
                print("Failed to load {}".format(filename))
                logging.error("Failed to load {}".format(filename))
                print("Reason: {} - {}".format(sys.exc_info()[0],sys.exc_info()[1]))
                logging.error("Reason: {} - {}".format(sys.exc_info()[0],sys.exc_info()[1]))
                brain_count -= 1
    brain = {'nodes':nodes,'patterns':patterns}
    return brain


def load_brain(nodes,patterns,data):
    for convo_key in data['conversations']:
        conversation = data['conversations'][convo_key]
        pattern_key = "{}.{}".format(data['intent'],convo_key)
        patterns[pattern_key] = []
        for node_key in conversation:
            new_key = "{}.{}.{}".format(data['intent'],convo_key,node_key)
            if new_key not in nodes:
                nodes[new_key] = {}
                node = conversation[node_key]
                for attr in node:
                    if attr == 'pattern':
                        patterns[pattern_key].append((node[attr].lower(),new_key))
                    elif attr == 'utterances':
                        patterns[pattern_key] += [(utterance.lower(),new_key) for utterance in node['utterances']]
                    elif attr == 'conversation':
                        if node[attr].count('.') == 0:
                            nodes[new_key][attr] = "{}.{}".format(data['intent'],node[attr])
                        else:
                            nodes[new_key][attr] = node[attr]
                    elif attr == 'node_options':
                        new_options = []
                        for option in node[attr]:
                            if option.count('.') == 0:
                                new_options.append("{}.{}.{}".format(data['intent'],convo_key,option))
                            elif option.count('.') == 1:
                                new_options.append("{}.{}".format(data['intent'],option))
                            else:
                                new_options.append(option)
                        nodes[new_key][attr] = new_options
                    elif attr not in ['node_type','responses','vars','reset','preset','chain','command']:
                        if node[attr] is not None and node[attr].count('.') == 0:
                            nodes[new_key][attr] = "{}.{}.{}".format(data['intent'],convo_key,node[attr])
                        elif node[attr] is not None and node[attr].count('.') == 1:
                            nodes[new_key][attr] = "{}.{}".format(data['intent'],node[attr])
                        else:
                            nodes[new_key][attr] = node[attr]
                    else:
                        nodes[new_key][attr] = node[attr]
            else:
                logging.error("Duplicate node key entry - node not added to brain: {}".format(new_key))
    return nodes,patterns


def init_logging(log_file,logging_level,already_started=False,write_log_to_file=True):
    try:
        numeric_level = getattr(logging, logging_level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: {}'.format(logging_level))
        if write_log_to_file:
            if not already_started:
                logging.basicConfig(filename=log_file, filemode='w', format='%(asctime)s | %(levelname)-8s | %(name)-32s | %(funcName)-25s | %(message)s', datefmt='%H:%M:%S', level=numeric_level)
            else:
                logging.basicConfig(filename=log_file, format='%(asctime)s | %(levelname)-8s | %(name)-32s | %(funcName)-25s | %(message)s', datefmt='%H:%M:%S', level=numeric_level)
        else:
            logging.basicConfig(format='%(asctime)s | %(levelname)-8s | %(name)-32s | %(funcName)-25s | %(message)s', datefmt='%H:%M:%S', level=numeric_level)
    finally:
        return logging


def remove_punctuation(input_string,keep_stars=False):
    # string.punctuation evaluates to:
    #   !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    # If keep_stars flag is True, the function does not remove '*' from input_string
    if keep_stars:
        punctuation = string.punctuation.replace('*','')
    else:
        punctuation = string.punctuation
    # Compatibility with Python 2.x and 3.x
    if sys.version_info >= (3,0):
        result = str(input_string).translate(str.maketrans("","",punctuation))
    else:
        result = str(input_string).translate(string.maketrans("",""),punctuation)
    return result


def printlog(response,speaker,presponse=False,noprint=False):
    if speaker.upper() == 'EMILY' and not noprint:
        if presponse:
            print("\n{}>  {}".format('Emily'.ljust(10),response))
        else:
            print("\n{}>  {}\n".format('Emily'.ljust(10),response))
    logging.info("")
    logging.info("{}: {}".format(speaker.upper(),response))
    logging.info("")


def apply_input_filters(user_input,intent_command=None,preformat_command=None):
    if intent_command:
        logging.debug("Applying this intent filter to user input: {}".format(intent_command))
        intent_command = intent_command.replace('{user_input}',user_input)
        command_result = run_command.run(intent_command)
        if command_result['success']:
            logging.info("Determined intent: {}".format(command_result['response']))
            intent = command_result['response']
        else:
            logging.error("Failed to apply intent filter: {}".format(intent_command))
            intent = None
    else:
        intent = None
    if preformat_command:
        logging.debug("Applying this preformat filter to user input: {}".format(preformat_command))
        preformat_command = preformat_command.replace('{user_input}',user_input)
        command_result = run_command.run(preformat_command)
        if command_result['success']:
            logging.info("Preformatted input to: {}".format(command_result['response']))
            new_input = command_result['response']
        else:
            logging.error("Failed to apply preformat filter: {}".format(preformat_command))
            new_input = None
    else:
        new_input = user_input
    return intent,new_input
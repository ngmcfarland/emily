from fuzzywuzzy import fuzz
import run_command
import logging
import string
import json
import sys
import re
import os


def load_data(brain_files=[]):
    brain_files = [file for file in brain_files if file.endswith('.json')]
    logging.info("Loading brain files: {}".format(brain_files))
    brain_count = len(brain_files)
    brain = []
    conversations = {}
    for filename in brain_files:
        try:
            with open(filename,'r') as f:
                data = json.loads(f.read())
            for topic in data['topics']:
                for category in topic['categories']:
                    if 'node' in category['template'] and '.' not in category['template']['node']:
                        category_template = dict(category['template'])
                        category_template['node'] = "{}.{}".format(data['intent'].lower(),category['template']['node'])
                    else:
                        category_template = dict(category['template'])
                    brain.append({'intent':data['intent'],'topic':topic['topic'],'pattern':category['pattern'],'template':category_template})
                    if 'utterances' in category:
                        for utterance in category['utterances']:
                            brain.append({'intent':data['intent'],'topic':topic['topic'],'pattern':utterance,'template':category_template})
            if 'conversations' in data:
                conversations = get_conversations(data=data,conversations=conversations)
        except:
            print("Failed to load {}".format(filename))
            logging.error("Failed to load {}".format(filename))
            print("Reason: {} - {}".format(sys.exc_info()[0],sys.exc_info()[1]))
            logging.error("Reason: {} - {}".format(sys.exc_info()[0],sys.exc_info()[1]))
            brain_count -= 1
    logging.info("Loaded {} brain files".format(brain_count))
    return brain,conversations


def expand_utterances(brain):
    rows = []
    brain.loc[brain['utterances'].isnull(),['utterances']] = brain.loc[brain['utterances'].isnull(),'utterances'].apply(lambda x: [])
    _ = brain.apply(lambda row: [rows.append([row['intent'],utterance,{'type':'U','redirect':row['pattern']},row['topic'],[]]) for utterance in row.utterances], axis=1)
    brain = brain.append(pd.DataFrame(rows, columns=['intent','pattern','template','topic','utterances']))
    brain.drop('utterances',axis=1,inplace=True)
    return brain


def get_conversations(data,conversations):
    for key in data['conversations']:
        new_key = "{}.{}".format(data['intent'].lower(),key)
        if new_key not in conversations:
            conversations[new_key] = {}
            for attr in data['conversations'][key]:
                if attr.lower() not in ['command','node_type','responses']:
                    conversations[new_key][attr] = "{}.{}".format(data['intent'].lower(),data['conversations'][key][attr])
                else:
                    conversations[new_key][attr] = data['conversations'][key][attr]
        else:
            logging.error("ERROR: Duplicate conversation entries found!")
            print("ERROR: Duplicate conversation entries found!")
            sys.exit(1)
    return conversations


def init_logging(log_file,logging_level,already_started=False):
    numeric_level = getattr(logging, logging_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: {}'.format(logging_level))
    
    if not already_started:
        logging.basicConfig(filename=log_file, filemode='w', format='%(asctime)s | %(levelname)-8s | %(name)-32s | %(funcName)-25s | %(message)s', datefmt='%H:%M:%S', level=numeric_level)
    else:
        logging.basicConfig(filename=log_file, format='%(asctime)s | %(levelname)-8s | %(name)-32s | %(funcName)-25s | %(message)s', datefmt='%H:%M:%S', level=numeric_level)
    return logging


def remove_punctuation(input_string):
    # string.punctuation evaluates to:
    #   !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    return str(input_string).translate(string.maketrans("",""),string.punctuation)


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
        intent_command = intent_command.replace('user_input',user_input)
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
        preformat_command = preformat_command.replace('user_input',user_input)
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
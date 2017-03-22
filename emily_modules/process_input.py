from . import conversations,variables,utils
from fuzzywuzzy import fuzz
from fnmatch import fnmatch
import logging
import random
import sys
import re
import os


def match_input(user_input,brain,session_vars,intent=None):
    try:
        if 'next_node' not in session_vars or session_vars['next_node'] is None:
            logging.debug("Next node not defined. Checking user input against patterns.")
            # Filter patterns by intent if intent was determined already
            if intent is not None:
                patterns = {}
                for key in brain['patterns']:
                    if key.split('.')[0] == intent.lower():
                        patterns[key] = brain['patterns'][key]
            else:
                patterns = brain['patterns']
            conversation = session_vars['conversation'] if 'conversation' in session_vars else 'default'
            best_match = match_patterns(user_input=user_input.lower(),patterns=patterns,conversation=conversation,session_vars=session_vars)
            if best_match is not None:
                next_node = best_match[2]
                session_vars = variables.check_stars(pattern=best_match[1],user_input=user_input,session_vars=session_vars)
            else:
                next_node = None
        else:
            next_node = session_vars['next_node']
        if next_node is not None:
            # Process the conversation node
            responses,session_vars,conversation = conversations.process_node(node_tag=next_node,nodes=brain['nodes'],session_vars=session_vars,responses=[],user_input=user_input)
            session_vars['conversation'] = conversation
            response = " ".join(responses)
            session_vars = variables.clear_stars(session_vars=session_vars)
        else:
            session_vars['next_node'] = None
            response = "I'm sorry, I don't know what you are asking."
    except:
        logging.error("{}".format(sys.exc_info()[0]))
        logging.error("{}".format(sys.exc_info()[1]))
        session_vars['next_node'] = None
        response = "I'm sorry, I don't know what you are asking."
    finally:
        return response,session_vars


def match_patterns(user_input,patterns,conversation,session_vars):
    r_weight = 1      # Weight for fuzz.ratio function
    pr_weight = 0.7   # Weight for fuzz.partial_ratio function
    intent = None
    # Get patterns that match the conversation
    if conversation != 'default':
        intent = conversation.split('.')[0]
        search_patterns = []
        for key in patterns:
            # filter patterns to nodes that match '<intent>.<conversation>.*'
            if ".".join(key.split('.')[:2]).lower() == conversation.lower():
                for pattern in patterns[key]:
                    if re.search(r"\{[A-Za-z0-9_\-\.]+\}",pattern[0]):
                        new_pattern = variables.replace_vars(session_vars=session_vars,response=pattern[0])
                        search_patterns.append((new_pattern,pattern[1]))
                    else:
                        search_patterns.append(pattern)
        if conversation.split('.')[1] == 'default':
            convo_match = None
            convo_default_match = score_patterns(user_input=user_input,search_patterns=search_patterns,r_weight=r_weight,pr_weight=pr_weight)
        else:
            convo_match = score_patterns(user_input=user_input,search_patterns=search_patterns,r_weight=r_weight,pr_weight=pr_weight)
            search_patterns = []
            for key in patterns:
                # Filter patterns to nodes that match '<intent>.default.*'
                if ".".join(key.split('.')[:2]).lower() == "{}.{}".format(intent,'default').lower():
                    for pattern in patterns[key]:
                        if re.search(r"\{[A-Za-z0-9_\-\.]+\}",pattern[0]):
                            new_pattern = variables.replace_vars(session_vars=session_vars,response=pattern[0])
                            search_patterns.append((new_pattern,pattern[1]))
                        else:
                            search_patterns.append(pattern)
            convo_default_match = score_patterns(user_input=user_input,search_patterns=search_patterns,r_weight=r_weight,pr_weight=pr_weight)
    else:
        convo_match = None
        convo_default_match = None
    search_patterns = []
    if intent is not None:
        for key in patterns:
            # Filter patterns to nodes that match '*.default.*' excluding '<intent>.default.*'
            if key.split('.')[0].lower() != intent.lower() and key.split('.')[1].lower() == 'default':
                for pattern in patterns[key]:
                    if re.search(r"\{[A-Za-z0-9_\-\.]+\}",pattern[0]):
                        new_pattern = variables.replace_vars(session_vars=session_vars,response=pattern[0])
                        search_patterns.append((new_pattern,pattern[1]))
                    else:
                        search_patterns.append(pattern)
    else:
        for key in patterns:
            # Filter patterns to nodes that match '*.default.*'
            if key.split('.')[1] == 'default':
                for pattern in patterns[key]:
                    if re.search(r"\{[A-Za-z0-9_\-\.]+\}",pattern[0]):
                        new_pattern = variables.replace_vars(session_vars=session_vars,response=pattern[0])
                        search_patterns.append((new_pattern,pattern[1]))
                    else:
                        search_patterns.append(pattern)
    # Score the results
    default_match = score_patterns(user_input=user_input,search_patterns=search_patterns,r_weight=r_weight,pr_weight=pr_weight)
    best_match = score_matches(default=default_match,convo_default=convo_default_match,convo=convo_match)
    return best_match


def score_patterns(user_input,search_patterns,r_weight,pr_weight):
    threshold = 90
    total_possible = r_weight*100 + pr_weight*100
    matches = []
    for pattern in search_patterns:
        check_pattern = utils.remove_punctuation(input_string=pattern[0],keep_stars=True).lower()
        if fnmatch(user_input,check_pattern) or fuzz.ratio(user_input,check_pattern) > threshold:
            score = r_weight*fuzz.ratio(user_input,check_pattern) + pr_weight*fuzz.partial_ratio(user_input,check_pattern)
            matches.append((score,pattern[0],pattern[1]))
    if len(matches) > 0:
        logging.debug("Choosing best match from: {}".format([x[1] for x in matches]))
        best_match = sorted(matches,key=lambda pattern: pattern[0],reverse=True)[0]
        logging.debug("Chose '{}' with {}% confidence.".format(best_match[1],(float(best_match[0])/float(total_possible))*100))
    else:
        logging.debug("No matches found above threshold: {}".format(threshold))
        best_match = None
    return best_match


def score_matches(default,convo_default,convo):
    logging.debug("Choosing best match from: ['{}','{}','{}']".format(default,convo_default,convo))
    if convo is not None:
        best_match = convo
    elif convo_default is not None:
        if convo_default[1] == '*' and default[1] != '*':
            best_match = default
        else:
            best_match = convo_default
    else:
        best_match = default
    return best_match
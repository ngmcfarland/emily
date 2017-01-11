from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from fnmatch import fnmatch
import random
import string
import json
import sys
import re
import os

curdir = os.path.dirname(__file__)
library_dir = os.path.join(curdir, 'library')


def browse_library():
    dir_files = os.listdir(library_dir)
    library_files_object = {}
    library_files_list = []
    index = 0
    for file in sorted(dir_files, key=str.lower):
        if fnmatch(file,'*.json') and not fnmatch(file,'*_index.json'):
            library_files_list.append("{} - {}".format(index,file))
            library_files_object[str(index)] = file
            index += 1
    return {'response':"\n".join(library_files_list),'library_files':library_files_object}


def index_json(json_file,file_input_type="direct"):
    if file_input_type == 'browse':
        library_files_object = browse_library()
        json_file = library_files_object['library_files'][json_file]
    if os.path.isfile(os.path.join(library_dir, json_file)):
        input_file = os.path.join(library_dir, json_file)
    else:
        print("ERROR: Could not find JSON file: {}".format(json_file))
        sys.exit(1)

    # load the JSON file
    with open(input_file,'r') as f:
        document = json.loads(f.read())

    # Prep index file
    index_file = "{}/{}_index.json".format(os.path.dirname(input_file),os.path.basename(input_file).split('.')[0])

    utterances = []
    indexes = {}
    used_ids = []

    if isinstance(document,dict):
        for attribute in document:
            utterances,indexes,used_ids = process_attribute(document,attribute,[attribute],utterances,indexes,used_ids)    
    elif isinstance(document,list):
        for i,attribute in enumerate(document):
            utterances,indexes,used_ids = process_attribute(document,i,[i],utterances,indexes,used_ids)
    else:
        print("I can only index dictionaries and lists")
        sys.exit(1)

    with open(index_file,'w') as f:
        f.write(json.dumps({'utterances':utterances,'indexes':indexes}))

    return {'index_file':index_file,'json_file':input_file}



def generate_id(used_ids=[]):
    id_length = 8
    accept_chars = ''.join([string.ascii_uppercase,string.ascii_lowercase,string.digits])
    while True:
        new_id = ''.join(random.SystemRandom().choice(accept_chars) for _ in range(id_length))
        if new_id not in used_ids:
            used_ids.append(new_id)
            break
    return new_id,used_ids


def process_attribute(root,attribute,index,utterances,indexes,used_ids):
    # Get a new attribute id
    attribute_id,used_ids = generate_id(used_ids)
    attribute_type = get_attribute_type(root,attribute)
    indexes[attribute_id] = {'type':attribute_type,'index':index}
    if attribute_type == 'object':
        if isinstance(attribute,basestring):
            utterances.append({'key':attribute.lower(),'value':None,'pointer':attribute_id})
        for child in root[attribute]:
            child_type = get_attribute_type(root[attribute],child)
            if child_type in ['string','bool','number']:
                if not isinstance(root[attribute][child],int) and not isinstance(root[attribute][child],bool) and not isinstance(root[attribute][child],float):
                    value = root[attribute][child].lower()
                else:
                    value = str(root[attribute][child])
                utterances.append({'key':child.lower(),'value':value,'pointer':attribute_id})
            else:
                utterances,indexes,used_ids = process_attribute(root[attribute],child,index+[child],utterances,indexes,used_ids)
    elif attribute_type == 'array':
        utterances.append({'key':attribute.lower(),'value':None,'pointer':attribute_id})
        for i,child in enumerate(root[attribute]):
            utterances,indexes,used_ids = process_attribute(root[attribute],i,index+[i],utterances,indexes,used_ids)
    return utterances,indexes,used_ids


def get_attribute_type(root,attribute):
    if isinstance(root[attribute],dict):
        attribute_type = 'object'
    elif isinstance(root[attribute],list):
        attribute_type = 'array'
    elif isinstance(root[attribute],basestring):
        attribute_type = 'string'
    elif isinstance(root[attribute],bool):
        attribute_type = 'bool'
    elif isinstance(root[attribute],int) or isinstance(root[attribute],float):
        attribute_type = 'number'
    return attribute_type


def answer_question(json_file,index_file,input_string,question_type='search'):
    # Read in JSON file and index file
    with open(json_file,'r') as f:
        document = json.loads(f.read())
    with open(index_file,'r') as f:
        doc_index = json.loads(f.read())

    # Set to lowercase
    input_string = input_string.lower()

    match_score = 0
    pointer = None
    match_key = None
    match_value = None
    for utterance in doc_index['utterances']:
        old_match_score = match_score
        match_score = fuzz.partial_ratio(input_string,utterance['key'])
        if utterance['value']:
            if re.search(re.escape(utterance['value']),input_string):
                match_score += 200
            else:
                match_score += fuzz.partial_ratio(input_string,utterance['value'])
        else:
            match_score = 2*match_score
        if match_score > old_match_score:
            pointer = utterance['pointer']
            match_key = utterance['key']
            match_value = utterance['value']
            # print("Match Score: {}, New Pointer: {}".format(match_score,pointer))
        else:
            match_score = old_match_score
    index_object = doc_index['indexes'][pointer]
    # take out the matching subject pieces so as to not confuse the attribute search
    input_string = input_string.replace(match_key,'')
    if match_value:
        input_string = input_string.replace(match_value,'')
    if question_type == 'search':
        if index_object['type'] == 'object':
            json_object = get_object_at_index(document,index_object['index'])
            # print(json_object)
            match = process.extractOne(input_string,json_object.keys())
            result = json_object[match[0]]
        else:
            result = "I'm sorry, I don't know how to retrieve information from {} objects".format(index_object['type'])
    elif question_type == 'quantity':
        json_object = get_object_at_index(document,index_object['index'])
        if index_object['type'] == 'array':
            result = len(json_object)
        elif index_object['type'] == 'object':
            match = process.extractOne(input_string,json_object.keys())
            child_type = get_attribute_type(json_object,match[0])
            if child_type == 'array':
                result = len(json_object[match[0]])
            elif child_type == 'number':
                result = json_object[match[0]]
        else:
            result = "I'm sorry, I don't know how to quantify information from {} objects".format(index_object['type'])
    return result


def get_object_at_index(document,index):
    try:
        json_object = document
        for key in index:
            json_object = json_object[key]
    except KeyError:
        json_object = {}
    return json_object
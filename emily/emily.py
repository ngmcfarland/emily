from .emily_modules import sessions,variables,process_input,utils,run_command,send_message
from flask_cors import CORS,cross_origin
from flask import Flask,request
from datetime import datetime
from six import string_types
from six.moves import input
import threading
import logging
import socket
import yaml
import json
import sys
import os

curdir = os.path.dirname(os.path.realpath(__file__))
config_file = 'emily_conf/emily_config.yaml'
with open(os.path.join(curdir,config_file),'r') as f:
    config = yaml.load(f.read())

app = Flask('emily')
CORS(app)


def __init_config__(**alt_config):
    global config
    for var in config:
        config[var] = alt_config[var] if var in alt_config else config[var]


class Emily(threading.Thread):
    def __init__(self,more_brains=[],more_vars={},disable_emily_defaults=False,**alt_config):
        super(Emily, self).__init__()
        self.already_started = True
        try:
            __init_config__(**alt_config)
            self.s = socket.socket()
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind(('',config['emily_port']))
            self.s.listen(5)
            self.already_started = False
            logging = utils.init_logging(log_file=os.path.join(curdir,config['log_file']),logging_level=config['logging_level'],write_log_to_file=config['write_log_to_file'])
            logging.debug("Socket successfully created and listening on port {}".format(config['emily_port']))
            if disable_emily_defaults:
                brain_files = more_brains
                self.brain = utils.load_data(brain_files=brain_files,source=config['brain_source'])
            else:
                if config['brain_source'].upper() == 'LOCAL':
                    brain_dir = os.path.join(curdir, config['brain_path'])
                    brain_files = ["{}/{}".format(brain_dir,file) for file in os.listdir(brain_dir)]
                    brain_files += more_brains
                    self.brain = utils.load_data(brain_files=brain_files,source=config['brain_source'])
                elif config['brain_source'].upper() == 'DYNAMODB':
                    self.brain = utils.load_data(brain_table=config['brain_path'],source=config['brain_source'],region=config['region'])
                else:
                    logging.error("Invalid source defined in config: {}".format(config['brain_source']))
                    sys.exit(1)
        except socket.error as err:
            if err.errno == 48:
                logging = utils.init_logging(log_file=os.path.join(curdir,config['log_file']),logging_level=config['logging_level'],already_started=True,write_log_to_file=config['write_log_to_file'])
                logging.debug("Emily already started")
            else:
                print(err)
        finally:
            self.more_vars = more_vars


    def run(self):
        default_session_vars = config['default_session_vars']
        for key in self.more_vars.keys():
            default_session_vars[key] = self.more_vars[key]
        default_session_vars['next_node'] = config['starting_node']
        if not self.already_started:
            while True:
                c,addr = self.s.accept()
                user_input = c.recv(4096)
                user_input = json.loads(user_input.decode())
                utils.printlog(response=user_input['message'],speaker='USER')
                emily_start_time = datetime.now()
                session_id = user_input['session_id']
                session_vars = sessions.get_session_vars(session_id=session_id,
                    source=config['session_vars_source'],
                    session_vars_path=config['session_vars_path'],
                    region=config['region'],
                    default_session_vars=default_session_vars)
                # Apply optional filters before sending to brain
                intent,new_input = utils.apply_input_filters(user_input=str(user_input['message']),
                    intent_command=config['intent_command'],
                    preformat_command=config['preformat_command'])
                session_vars['user_input'] = new_input
                response,session_vars = process_input.match_input(user_input=utils.remove_punctuation(new_input),
                    brain=self.brain,
                    session_vars=session_vars,
                    intent=intent)
                utils.printlog(response=response,speaker='EMILY',noprint=True)
                c.send(json.dumps({'response':response,'session_id':session_id}).encode())
                c.close()

                emily_response_time = datetime.now() - emily_start_time
                logging.debug("Emily Response Time: {} seconds".format("%.3f" % emily_response_time.total_seconds()))

                if config['logging_level'].upper() == 'DEBUG':
                    logging.debug("Session Variables:")
                    for var in session_vars:
                        logging.debug(" * {}: {}".format(var,session_vars[var]))

                if user_input['message'].upper() in ['Q','QUIT','EXIT','BYE']:
                    sessions.remove_session(session_id=session_id,
                        source=config['session_vars_source'],
                        session_vars_path=config['session_vars_path'],
                        region=config['region'])
                    logging.info("Removed session: {}".format(session_id))
                    if config['session_vars_source'].upper() == 'LOCAL' and sessions.get_session_count(session_vars_path=config['session_vars_path']) == 0:
                        self.s.close()
                        break
                else:
                    sessions.set_session_vars(session_id=session_id,
                        session_vars=session_vars,
                        source=config['session_vars_source'],
                        session_vars_path=config['session_vars_path'],
                        region=config['region'])

    def send(self,message,session_id):
        new_s = socket.socket()
        port = config['emily_port']
        new_s.connect(('localhost',port))
        new_s.send(json.dumps({'message':message,'session_id':session_id}).encode())
        response = new_s.recv(4096)
        response = json.loads(response.decode())
        new_s.close()
        return response['response'],response['session_id']

    def get_session(self,preferred_id=None):
        default_session_vars = config['default_session_vars']
        for key in self.more_vars.keys():
            default_session_vars[key] = self.more_vars[key]
        if 'starting_node' in config:
            default_session_vars['next_node'] = config['starting_node']
        session_id = sessions.create_new_session(default_session_vars=default_session_vars,
            source=config['session_vars_source'],
            session_vars_path=config['session_vars_path'],
            region=config['region'],
            preferred_id=preferred_id)
        return session_id


@app.route('/get_session')
def get_session():
    session_id = sessions.create_new_session(default_session_vars=config['default_session_vars'],
        source=config['session_vars_source'],
        session_vars_path=config['session_vars_path'],
        region=config['region'])
    return str(session_id)

@app.route('/get_session', methods=['POST'])
def get_preferred_session():
    session_id = None
    if request.json is not None and 'preferred_id' in request.json:
        session_id = sessions.create_new_session(default_session_vars=config['default_session_vars'],
            source=config['session_vars_source'],
            session_vars_path=config['session_vars_path'],
            region=config['region'],
            preferred_id=request.json['preferred_id'])
    elif request.form is not None and 'preferred_id' in request.form:
        session_id = sessions.create_new_session(default_session_vars=config['default_session_vars'],
            source=config['session_vars_source'],
            session_vars_path=config['session_vars_path'],
            region=config['region'],
            preferred_id=request.form['preferred_id'])
    else:
        session_id = sessions.create_new_session(default_session_vars=config['default_session_vars'],
            source=config['session_vars_source'],
            session_vars_path=config['session_vars_path'],
            region=config['region'])
    return str(session_id)

@app.route('/chat', methods=['POST'])
def chat():
    response = 'None'
    session_id = None
    if request.json is not None:
        logging.debug("Client request: {}".format(json.dumps(request.json)))
        if 'session_id' not in request.json:
            response = 'Please include session ID in request. Session ID can be obtained by performing a GET against /get_session'
        else:
            response,session_id = send_message.send(message=request.json['message'],session_id=request.json['session_id'],port=config['emily_port'])
    else:
        if 'session_id' not in request.form:
            response = 'Please include session ID in request. Session ID can be obtained by performing a GET against /get_session'
        else:
            response,session_id = send_message.send(message=request.form['message'],session_id=request.form['session_id'],port=config['emily_port'])
    response = json.dumps({'response':response,'session_id':session_id})
    return response


def start_emily(more_brains=[],more_vars={},disable_emily_defaults=False,**alt_config):
    session = Emily(more_brains=more_brains,more_vars=more_vars,disable_emily_defaults=disable_emily_defaults,**alt_config)
    session.start()
    print("Web Server Started...")
    return app


def emily_server():
    app = start_emily()
    app.run(debug=True)


def chat():
    logging = utils.init_logging(log_file=config['log_file'],logging_level=config['logging_level'])
    if config['brain_source'].upper() == 'LOCAL':
        brain_dir = os.path.join(curdir, config['brain_path'])
        brain_files = ["{}/{}".format(brain_dir,file) for file in os.listdir(brain_dir)]
        brain = utils.load_data(brain_files=brain_files,
            source=config['brain_source'])
    elif config['brain_source'].upper() == 'DYNAMODB':
        brain = utils.load_data(brain_table=config['brain_path'],
            source=config['brain_source'],
            region=config['region'])
    else:
        logging.error("Invalid source defined in config: {}".format(config['brain_source']))
        sys.exit(1)
    session_vars = config['default_session_vars']
    session_vars['default_session_vars'] = dict(config['default_session_vars'])
    session_vars['next_node'] = config['starting_node']
    print("")
    while True:
        username = session_vars['name'] if 'name' in session_vars else 'User'
        user_input = input('{}>  '.format(username.ljust(10)))
        utils.printlog(response=user_input,speaker='USER')
        emily_start_time = datetime.now()
        # Apply optional filters before sending to brain
        intent,new_input = utils.apply_input_filters(user_input=user_input)
        session_vars['user_input'] = new_input
        response,session_vars = process_input.match_input(user_input=utils.remove_punctuation(new_input),
            brain=brain,
            session_vars=session_vars,
            intent=intent)
        utils.printlog(response=response,speaker='EMILY')

        emily_response_time = datetime.now() - emily_start_time
        logging.debug("Emily Response Time: {} seconds".format("%.3f" % emily_response_time.total_seconds()))

        if config['logging_level'].upper() == 'DEBUG':
            logging.debug("Session Variables:")
            for var in session_vars:
                logging.debug(" * {}: {}".format(var,session_vars[var]))

        if user_input.upper() in ['QUIT','Q','EXIT','BYE']:
            break


def stateless(message,session_id=None,preferred_id=None,more_brains=[],more_vars={},disable_emily_defaults=False,**alt_config):
    __init_config__(**alt_config)
    logging = utils.init_logging(log_file=config['log_file'],
        logging_level=config['logging_level'],
        already_started=True,
        write_log_to_file=config['write_log_to_file'])
    if config['brain_source'].upper() == 'LOCAL':
        if not disable_emily_defaults:
            brain_dir = os.path.join(curdir, config['brain_path'])
            brain_files = ["{}/{}".format(brain_dir,file) for file in os.listdir(brain_dir)]
            brain_files += more_brains
        else:
            brain_files = more_brains
        brain = utils.load_data(brain_files=brain_files,source=config['brain_source'])
    elif config['brain_source'].upper() == 'DYNAMODB':
        brain = utils.load_data(brain_table=config['brain_path'],source=config['brain_source'],region=config['region'])
    else:
        logging.error("Invalid source defined in config: {}".format(config['brain_source']))
        sys.exit(1)
    if session_id is None:
        session_vars = config['default_session_vars']
        session_vars['default_session_vars'] = dict(config['default_session_vars'])
        session_vars['next_node'] = config['starting_node']
        for var in more_vars:
            session_vars[var] = more_vars[var]
        session_id = sessions.create_new_session(default_session_vars=session_vars,
            source=config['session_vars_source'],
            session_vars_path=config['session_vars_path'],
            region=config['region'],
            preferred_id=preferred_id)
    else:
        default_session_vars = config['default_session_vars']
        for var in more_vars:
            default_session_vars[var] = more_vars[var]
        default_session_vars['next_node'] = config['starting_node']
        session_vars = sessions.get_session_vars(session_id=session_id,
            source=config['session_vars_source'],
            session_vars_path=config['session_vars_path'],
            region=config['region'],
            default_session_vars=default_session_vars)
    utils.printlog(response=message,speaker='USER')
    emily_start_time = datetime.now()
    # Apply optional filters before sending to brain
    intent,new_input = utils.apply_input_filters(user_input=message)
    session_vars['user_input'] = new_input
    response,session_vars = process_input.match_input(user_input=utils.remove_punctuation(new_input),
        brain=brain,
        session_vars=session_vars,
        intent=intent)
    utils.printlog(response=response,speaker='EMILY',noprint=True)
    emily_response_time = datetime.now() - emily_start_time
    logging.debug("Emily Response Time: {} seconds".format("%.3f" % emily_response_time.total_seconds()))
    if config['logging_level'].upper() == 'DEBUG':
        logging.debug("Session Variables:")
        for var in session_vars:
            logging.debug(" * {}: {}".format(var,session_vars[var]))
    if new_input.upper() in ['QUIT','Q','EXIT','BYE']:
        sessions.remove_session(session_id=session_id,
            source=config['session_vars_source'],
            session_vars_path=config['session_vars_path'],
            region=config['region'])
        logging.info("Removed session: {}".format(session_id))
    else:
        sessions.set_session_vars(session_id=session_id,
            session_vars=session_vars,
            source=config['session_vars_source'],
            session_vars_path=config['session_vars_path'],
            region=config['region'])
    return response,session_id



if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'chat':
        chat()
    elif len(sys.argv) == 2:
        start_emily(sys.argv[1])
    else:
        application = start_emily()
        application.run()

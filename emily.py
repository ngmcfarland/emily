from emily_modules import sessions, variables, process_input, utils, run_command
from datetime import datetime
import threading
import logging
import socket
import yaml
import json
import sys
import os

curdir = os.path.dirname(__file__)
config_file = 'emily_conf/emily_config.yaml'
with open(os.path.join(curdir,config_file),'r') as f:
    config = yaml.load(f.read())


class Emily(threading.Thread):
    def __init__(self,more_brains=[],more_vars={},disable_emily_defaults=False,**alt_config):
        super(Emily, self).__init__()
        try:
            emily_config = {}
            for var in config:
                emily_config[var] = alt_config[var] if var in alt_config else config[var]
            self.config = emily_config
            self.s = socket.socket()
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.s.bind(('',self.config['emily_port']))
            self.s.listen(5)
            self.already_started = False
            logging = utils.init_logging(log_file=os.path.join(curdir,self.config['log_file']),logging_level=self.config['logging_level'])
            logging.debug("Socket successfully created and listening on port {}".format(self.config['emily_port']))
            if disable_emily_defaults:
                brain_files = more_brains
            else:
                brain_dir = os.path.join(curdir, self.config['brain_dir'])
                brain_files = ["{}/{}".format(brain_dir,file) for file in os.listdir(brain_dir)]
                brain_files += more_brains
            self.brain = utils.load_data(brain_files=brain_files)
        except socket.error,err:
            if err.errno == 48:
                logging = utils.init_logging(log_file=os.path.join(curdir,self.config['log_file']),logging_level=self.config['logging_level'],already_started=True)
                logging.debug("Emily already started")
                self.already_started = True
            else:
                print(err)
        finally:
            self.more_vars = more_vars


    def run(self):
        default_session_vars = self.config['default_session_vars']
        for key in self.more_vars.keys():
            default_session_vars[key] = self.more_vars[key]
        if not self.already_started:
            while True:
                c,addr = self.s.accept()
                user_input = c.recv(4096)
                user_input = json.loads(user_input)
                utils.printlog(response=user_input['message'],speaker='USER')
                emily_start_time = datetime.now()
                session_id = user_input['session_id']
                if not session_id:
                    session_id = sessions.create_new_session(default_session_vars=default_session_vars)
                    logging.info("New session ID: {}".format(session_id))
                session_vars = sessions.get_session_vars(session_id=session_id)
                # Apply optional filters before sending to brain
                intent,new_input = utils.apply_input_filters(user_input=str(user_input['message']))
                response,session_vars = process_input.match_input(user_input=utils.remove_punctuation(new_input),brain=self.brain,session_vars=session_vars,intent=intent,noprint=True)
                utils.printlog(response=response,speaker='EMILY',noprint=True)
                c.send(json.dumps({'response':response,'session_id':session_id}))
                c.close()

                emily_response_time = datetime.now() - emily_start_time
                logging.debug("Emily Response Time: {} seconds".format("%.3f" % emily_response_time.total_seconds()))

                if self.config['logging_level'].upper() == 'DEBUG':
                    logging.debug("Session Variables:")
                    for var in session_vars:
                        logging.debug(" * {}: {}".format(var,session_vars[var]))

                if user_input['message'].upper() in ['Q','QUIT','EXIT','BYE']:
                    sessions.remove_session(session_id=session_id)
                    logging.info("Removed session: {}".format(session_id))
                    if sessions.get_session_count() == 0:
                        self.s.close()
                        break
                else:
                    sessions.set_session_vars(session_id=session_id,session_vars=session_vars)

    def send(self,message,session_id=None):
        new_s = socket.socket()
        port = self.config['emily_port']
        new_s.connect(('localhost',port))
        new_s.send(json.dumps({'message':message,'session_id':session_id}))
        response = new_s.recv(4096)
        response = json.loads(response)
        new_s.close()
        return response['response'],response['session_id']




def start_emily(web_socket=False):
    logging = utils.init_logging(log_file=os.path.join(curdir,config['log_file']),logging_level=config['logging_level'])
    brain_dir = os.path.join(curdir, config['brain_dir'])
    brain_files = ["{}/{}".format(brain_dir,file) for file in os.listdir(brain_dir)]
    brain = utils.load_data(brain_files=brain_files)
    session_vars = { 'topic':'NONE' }
    if web_socket:
        s = socket.socket()
        logging.debug("Socket successfully created")
        s.bind(('', config['emily_port']))
        logging.debug("socket bound to {}".format(config['emily_port']))
        s.listen(5)
        logging.debug("socket is listening")
    else:
        s = None
        print("")
    while True:
        if web_socket:
            c, addr = s.accept()
            user_input = c.recv(4096)
            user_input = json.loads(user_input)
            utils.printlog(response=user_input,speaker='USER')
            emily_start_time = datetime.now()
            session_id = user_input['session_id']
            # If this is a new session (no id provided) start new session
            if not session_id:
                session_id = sessions.create_new_session()
                logging.info("New session ID: {}".format(session_id))
            # Get session vars by id
            session_vars = sessions.get_session_vars(session_id=post_vars['session_id'])
            # Apply optional filters before sending to brain
            intent,new_input = utils.apply_input_filters(user_input=str(user_input['message']))
            response,session_vars = process_input.match_input(user_input=utils.remove_punctuation(new_input),brain=brain,session_vars=session_vars,intent=intent,noprint=True)
            utils.printlog(response=response,speaker='EMILY',noprint=True)            
            c.send(json.dumps({'response':response,'session_id':session_id}))
            c.close()
        else:
            username = session_vars['name'] if 'name' in session_vars else 'User'
            user_input = raw_input('{}>  '.format(username.ljust(10)))
            utils.printlog(response=user_input,speaker='USER')
            emily_start_time = datetime.now()
            # Apply optional filters before sending to brain
            intent,new_input = utils.apply_input_filters(user_input=user_input)
            response,session_vars = process_input.match_input(user_input=utils.remove_punctuation(new_input),brain=brain,session_vars=session_vars,intent=intent)
            utils.printlog(response=response,speaker='EMILY')

        emily_response_time = datetime.now() - emily_start_time
        logging.debug("Emily Response Time: {} seconds".format("%.3f" % emily_response_time.total_seconds()))

        if config['logging_level'].upper() == 'DEBUG':
            logging.debug("Session Variables:")
            for var in session_vars:
                logging.debug(" * {}: {}".format(var,session_vars[var]))

        if web_socket:
            if user_input['message'].upper() in ['QUIT','Q','EXIT','BYE']:
                sessions.remove_session(session_id=session_id)
                logging.info("Removed session: {}".format(session_id))
            else:
                sessions.set_session_vars(session_id=session_id,session_vars=session_vars)
        elif user_input.upper() in ['QUIT','Q','EXIT','BYE']:
            break


if __name__ == '__main__':
    if len(sys.argv) == 2:
        start_emily(sys.argv[1])
    else:
        start_emily()
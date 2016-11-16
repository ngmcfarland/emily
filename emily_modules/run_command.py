import traceback
import logging
import sys
import os

def run(command):
    try:
        return_value = eval(command)
        return {'success': True, 'response': return_value}
    except NameError, e:
        module = str(e).split("'")[1]
        return re_run(command,module)
    except:
        logging.error("Error running command in {}".format(__file__))
        logging.error("{}".format(sys.exc_info()[0]))
        logging.error("{}".format(sys.exc_info()[1]))
        response = "...well, this is embarrassing. I seem to be having trouble running commands right now using {}".format(__file__)
        return {'success': False, 'response': response}

def re_run(command,module):
    try:
        exec("import {}".format(module))
        rerun_value = eval(command)
        return {'success': True, 'response': rerun_value}
    except:
        logging.error("Error running {} in {}".format(command,__file__))
        logging.error("{}".format(sys.exc_info()[0]))
        logging.error("{}".format(sys.exc_info()[1]))
        for element in traceback.extract_stack():
            logging.error("{}".format(element))
        response = "...well, this is embarrassing. I seem to be having trouble running: '{}'. Make sure the location of this module is accessible in PYTHONPATH.".format(command)
        return {'success': False, 'response': response}

if __name__ == '__main__':
    run(sys.argv[1])
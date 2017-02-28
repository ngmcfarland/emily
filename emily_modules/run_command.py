from datetime import datetime
import traceback
import logging
import sys
import os

def run(command):
    try:
        logging.debug("Starting command run")
        start_time = datetime.now()
        return_value = eval(command)
        logging.debug("Ran Command: {}".format(command))
        result = {'success': True, 'response': return_value}
    except NameError as e:
        module = str(e).split("'")[1]
        result = re_run(command,module)
    except:
        logging.error("Error running command in {}".format(__file__))
        logging.error("{}".format(sys.exc_info()[0]))
        logging.error("{}".format(sys.exc_info()[1]))
        response = "...well, this is embarrassing. I seem to be having trouble running commands right now using {}".format(__file__)
        result = {'success': False, 'response': response}
    finally:
        exec_time = datetime.now() - start_time
        logging.debug("Command Execution Time: {} seconds".format("%.3f" % exec_time.total_seconds()))
        return result


def re_run(command,module):
    try:
        if sys.version_info >= (3,0):
            exec("from . import {}".format(module))
            rerun_value = eval(command)
            logging.debug("Ran Command: {}".format(command))
            result = {'success': True, 'response': rerun_value}
        else:
            result = re_re_run(command,module)
    except ImportError as e:
        module = str(e).split("'")[1]
        result = re_re_run(command,module)
    except:
        logging.error("Error running command in {}".format(__file__))
        logging.error("{}".format(sys.exc_info()[0]))
        logging.error("{}".format(sys.exc_info()[1]))
        response = "...well, this is embarrassing. I seem to be having trouble running commands right now using {}".format(__file__)
        result = {'success': False, 'response': response}
    finally:
        return result


def re_re_run(command,module):
    try:
        exec("import {}".format(module))
        rererun_value = eval(command)
        logging.debug("Ran Command: {}".format(command))
        return {'success': True, 'response': rererun_value}
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
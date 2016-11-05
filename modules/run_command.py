import sys

def run(command):
    try:
        return_value = eval(command)
        return return_value
    except NameError, e:
        module = str(e).split("'")[1]
        return re_run(command,module)
    except:
        return "ERROR: Inside run"

def re_run(command,module):
    try:
        exec("import {}".format(module))
        rerun_value = eval(command)
        return rerun_value
    except:
        return "ERROR: Inside rerun\n{}\n{}".format(sys.exc_info()[0],sys.exc_info()[1])

if __name__ == '__main__':
    run(sys.argv[1])
import sys
from datetime import datetime
import time
from parse_date import parse_date
from parse_time import parse_time
import dateparser_config as config
import re

def __wrapper__(datetime_input,output_format='%m/%d/%Y %H:%M:%S'):
    """Wraps parse_datetime() function when user calls 'python dateparser.py <options>' from command line"""
    result = parse_time(time_input,output_format)
    print("Result: {}".format(result))
    return 0


def parse_datetime(datetime_input,output_format='%m/%d/%Y %H:%M:%S',return_datetime=False):
    """
    """
    datetime_input = str(datetime_input)
    case1 = re.compile(r"^(.+)\sat\s(.+)$", re.IGNORECASE)
    case2 = re.compile(r"^(.+)\son\s(.+)$", re.IGNORECASE)
    case3 = re.compile(r"^(\d{8})(\d{4,6})$")
    case4 = re.compile(r"^(\d{9,10})$")
    match_value = case1.match(datetime_input)
    if case1.match(datetime_input):
        match_value = case1.match(datetime_input)
        date = parse_date(match_value.group(1),'%Y-%m-%d')
        timestamp = parse_time(match_value.group(2),'%H:%M:%S')
    elif case2.match(datetime_input):
        match_value = case2.match(datetime_input)
        date = parse_date(match_value.group(2),'%Y-%m-%d')
        timestamp = parse_time(match_value.group(1),'%H:%M:%S')
    elif case3.match(datetime_input):
        match_value = case3.match(datetime_input)
        date = parse_date(match_value.group(1),'%Y-%m-%d')
        timestamp = parse_time(match_value.group(2),'%H:%M:%S')
    elif case4.match(datetime_input):
        match_value = case4.match(datetime_input)
        date = time.strftime('%Y-%m-%d',time.localtime(float(match_value.group(1))))
        timestamp = time.strftime('%H:%M:%S',time.localtime(float(match_value.group(1))))
    else:
        print("\nERROR[500]: The format that you entered does not match any known datetime formats.")
        print(config.parse_datetime_usage)
        return None
    datetime_result = datetime.strptime('{} {}'.format(date,timestamp),'%Y-%m-%d %H:%M:%S')
    if return_datetime:
        return datetime_result
    else:
        return datetime.strftime(datetime_result,output_format)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        __wrapper__(sys.argv[1])
    elif len(sys.argv) == 3:
        __wrapper__(sys.argv[1],sys.argv[2])
    else:
        print("ERROR[300]: Invalid number of arguments\n")
        print(config.parse_datetime_usage)
        sys.exit()
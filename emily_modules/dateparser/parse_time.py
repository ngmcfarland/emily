import sys
from datetime import datetime, timedelta
import dateparser_config as config
import time
import re


def __wrapper__(time_input,output_format='%H:%M:%S'):
    """Wraps parse_time() function when user calls 'python dateparser.py <options>' from command line"""
    result = parse_time(time_input,output_format)
    print("Result: {}".format(result))
    return 0


def parse_time(time_input,output_format='%H:%M:%S',return_datetime=False):
    """
    Takes a common, human-readable time format, and converts it to the format requested
    Recognized input formats (case insensitive) including combinations of each:
        15:35:21
        7:30 AM
        09:54:23 PM
        Five minutes from now
        Two hours ago
        Quarter till 11 pm
        Midnight
    Parameters:
        time_input      - human-readable time string
        output_format   - format for the string result using Python datetime format. Default: '%H:%M:%S'
        return_datetime - True value returns Python datetime type, False returns string. Default: False
    Example: 
        input: dateparser.parse_time('11:53 PM','%H:%M:%S')
        result: '23:53:00'

    TODO: Add match for values like "five o'clock", "seven thirty"
    """
    time_input = str(time_input)
    case1 = re.compile(r"^(\d{1,2})[\:\.]?(\d{1,2})[\:\.]?(\d{1,2})?\s?(pm|am|(this|in\sthe)\s(morning|evening)|tonight)?$", re.IGNORECASE)
    case2 = re.compile(r"^in\s(\d{1,2}|[a-z]+)\s([a-z]+)$", re.IGNORECASE)
    case3 = re.compile(r"^(\d{1,2}|[a-z]+)\s([a-z]+)\s(from\snow|ago)$", re.IGNORECASE)
    #case4 = re.compile(r"^(\d{1,2}|[a-z]+)\s")
    case4 = re.compile(r"^(\d{1,2}|[a-z]+)\s(past|till|after|before|to)\s(\d{1,2}|[a-z]+)\s?(o[\'\s]?clock)?\s?(am|pm|(this|in\sthe)\s(morning|evening)|tonight)?$", re.IGNORECASE)
    case5 = re.compile(r"^(\d{1,2}|[a-z]+)\s?(am|pm|(this|in\sthe)\s(morning|evening)|tonight)?$", re.IGNORECASE)
    case6 = re.compile(r"^(\d{9,10})$")
    if case1.match(time_input):
        # Example: 15:45:21 or 9:25 AM
        match_value = case1.match(time_input)
        hour = __format_element__(match_value.group(1),"HOUR",match_value.group(4))
        minute = __format_element__(match_value.group(2),"MINUTE")
        second = __format_element__(match_value.group(3),"SECOND")
    elif case2.match(time_input):
        match_value = case2.match(time_input)
        hour,minute,second = __relative_time__(value=match_value.group(1),units=match_value.group(2))
    elif case3.match(time_input):
        match_value = case3.match(time_input)
        if match_value.group(3).upper() == "AGO":
            hour,minute,second = __relative_time__(value=match_value.group(1),units=match_value.group(2),reverse=True)
        else:
            hour,minute,second = __relative_time__(value=match_value.group(1),units=match_value.group(2))
    elif case4.match(time_input):
        match_value = case4.match(time_input)
        if match_value.group(2).upper() in ["PAST","AFTER"]:
            hour,minute,second = __relative_time__(value=match_value.group(1),start_value=match_value.group(3),period=match_value.group(5))
        elif match_value.group(2).upper() in ["TILL","BEFORE","TO"]:
            hour,minute,second = __relative_time__(value=match_value.group(1),start_value=match_value.group(3),period=match_value.group(5),reverse=True)
        else:
            print("\nERROR[101]: The format you entered does not match any known time formats.")
            print(config.parse_time_usage)
            return None
    elif case5.match(time_input):
        # Example: "Noon" or "Midnight" or "six" or "11 PM"
        match_value = case5.match(time_input)
        hour,minute,second = __relative_time__(value=match_value.group(1),period=match_value.group(2))
    elif case6.match(time_input):
        # Example: 1470443584
        match_value = case6.match(time_input)
        hour,minute,second = __time_since_epoch__(float(match_value.group(1)))
    else:
        print("\nERROR[100]: The format you entered does not match any known time formats.")
        print(config.parse_time_usage)
        return None
    if hour and minute and second:
        time_result = datetime.strptime("{0}:{1}:{2}".format(hour,minute,second),'%H:%M:%S')
        if return_datetime:
            return time_result
        else:
            return str(datetime.strftime(time_result,output_format))
    else:
        print("\nERROR[102]: The format you entered does not match any known time formats.")
        print(config.parse_time_usage)
        return None


def __format_element__(value, element_type, period=None):
    """Internal function used for standardizing hour, minute, and second values"""
    if element_type == "HOUR":
        if period:
            if period.upper() in ["PM","THIS EVENING","IN THE EVENING","TONIGHT"]:
                result = '{}'.format(int(value)+12)
            else:
                result = value.zfill(2)
        else:
            result = value.zfill(2)
    elif element_type == "MINUTE":
        result = value.zfill(2)
    elif element_type == "SECOND":
        if value:
            result = value.zfill(2)
        else:
            result = '00'
    return result


def __time_since_epoch__(value):
    """Internal function used for Unix datetime format"""
    hour = time.strftime('%H',time.localtime(value))
    minute = time.strftime('%M',time.localtime(value))
    second = time.strftime('%S',time.localtime(value))
    return hour,minute,second


def __relative_time__(value, units=None, reverse=False, start_value=None, period=None):
    """Internal function used when inputs like 'noon' and 'midnight' are provided"""
    if start_value:
        had_start_value = True
        if not __is_int__(start_value):
            start_match_found = False
            for number in config.numbers:
                if start_value.upper() in number['strings']:
                    start_value = number['value']
                    start_match_found = True
                    break
        else:
            start_match_found = True
        if start_match_found:
            start_value = datetime.strptime('{}:00:00'.format(__format_element__(start_value,"HOUR",period)),'%H:%M:%S')
        else:
            print("\nERROR[202]: The format you entered does not match any known time formats.")
            return None,None,None
    else:
        had_start_value = False
        start_value = datetime.now()
    if units:
        value_match_found = False
        units_match_found = False
        if __is_int__(value):
            int_value = int(value)
            value_match_found = True
        else:
            for number in config.numbers:
                if value.upper() in number['strings']:
                    int_value = int(number['value'])
                    value_match_found = True
                    break
        for time in config.times:
            if units.upper() in time['strings']:
                delta_seconds = time['value']
                units_match_found = True
                break
        if value_match_found and units_match_found:
            if reverse:
                return __get_elements__(start_value - timedelta(seconds=int_value*delta_seconds))    
            else:
                return __get_elements__(start_value + timedelta(seconds=int_value*delta_seconds))
        else:
            print("\nERROR[201]: The format you entered does not match any known time formats")
            return None,None,None
    if value.upper() == "NOON":
        return "12","00","00"
    elif value.upper() == "MIDNIGHT":
        return "00","00","00"
    elif value.upper() == ["NOW","RIGHT NOW"]:
        return __get_elements__(datetime.now())
    else:
        value_match_found = False
        if had_start_value:
            for time in config.times:
                if value.upper() in time['strings']:
                    delta_seconds = time['value']
                    value_match_found = True
                    break
            if value_match_found:
                if reverse:
                    return __get_elements__(start_value - timedelta(seconds=delta_seconds))
                else:
                    return __get_elements__(start_value + timedelta(seconds=delta_seconds))
            else:
                print("\nERROR[200]: The format you entered does not match any known time formats.")
                return None,None,None
        else:
            if not __is_int__(value):
                for number in config.numbers:
                    if value.upper() in number['strings']:
                        hour = number['value']
                        value_match_found = True
                        break
            else:
                value_match_found = True
                hour = value
            if value_match_found:
                return __format_element__(hour,"HOUR",period),"00","00"
            else:
                print("\nERROR[203]: The format you entered does not match any known time formats.")


def __get_elements__(time_input):
    hour = datetime.strftime(time_input,'%H')
    minute = datetime.strftime(time_input,'%M')
    second = datetime.strftime(time_input,'%S')
    return hour,minute,second


def __is_int__(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    if len(sys.argv) == 2:
        __wrapper__(sys.argv[1])
    elif len(sys.argv) == 3:
        __wrapper__(sys.argv[1],sys.argv[2])
    else:
        print("ERROR[300]: Invalid number of arguments\n")
        print(config.parse_time_usage)
        sys.exit()
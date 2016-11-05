import sys
from datetime import datetime, timedelta
import time
import dateparser_config as config
import re


def __wrapper__(date_input,output_format='%Y-%m-%d'):
    """Wraps parse_date() function when user calls 'python dateparser.py <options>' from command line"""
    result = parse_date(date_input,output_format)
    print("Result: {}".format(result))
    return 0


def parse_date(date_input,output_format='%Y-%m-%d',return_datetime=False):
    """
    Takes a common, human-readable date format, and converts it to the format requested
    Recognized input formats (case insensitive) including combinations of each:
        Jan 1st, 2000
        January 1 2000
        1.1.2000
        01/01/00
        2000-01-01
        01-JAN-2000
        20000101
        Today
        Tomorrow
        Yesterday
        Tuesday
        Next Friday
        Last Saturday
    Parameters:
        date_input      - human-readable date string
        output_format   - format for the string result using Python datetime format. Default: '%Y-%m-%d'
        return_datetime - True value returns Python datetime type, False returns string. Default: False
    Example: 
        input: dateparser.parse_date('July 28th, 2016','%m/%d/%Y')
        result: '07/28/2016'

    TODO: Add match for values like 'fifth' and 'second'
    """
    date_input = str(date_input)
    case1 = re.compile(r"^([a-z]+)\s(\d+)(th|rd|st|nd)?[\W]*(\d{0,4})?$", re.IGNORECASE)
    case2 = re.compile(r"^(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.]?(\d{0,4})?")
    case3 = re.compile(r"^(\d{4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,2})")
    case4 = re.compile(r"^(\d{1,2})[\/\-\.]([a-z]+)[\/\-\.](\d{2,4})", re.IGNORECASE)
    case5 = re.compile(r"^(\d{1,2})(th|rd|st|nd)?\s(of\s)?([a-z]+)[\W]?(\d{0,4})?", re.IGNORECASE)
    case6 = re.compile(r"^(\d{4})(\d{2})(\d{2})$")
    case7 = re.compile(r"^[a-z\s]+$", re.IGNORECASE)
    case8 = re.compile(r"^(\d{9,10})$")
    if case1.match(date_input):
        # Example: July 21st, 2016 or Oct 10 2016
        match_value = case1.match(date_input)
        day = __format_element__(match_value.group(2),"DAY")
        month = __format_element__(match_value.group(1),"MONTH")
        year = __format_element__(match_value.group(4),"YEAR")
    elif case2.match(date_input):
        # Example: 7/21/16 or 07.21.2016
        match_value = case2.match(date_input)
        day = __format_element__(match_value.group(2),"DAY")
        month = __format_element__(match_value.group(1),"MONTH")
        year = __format_element__(match_value.group(3),"YEAR")
    elif case3.match(date_input):
        # Example: 2016/07/21 or 2016-7-21
        match_value = case3.match(date_input)
        day = __format_element__(match_value.group(3),"DAY")
        month = __format_element__(match_value.group(2),"MONTH")
        year = __format_element__(match_value.group(1),"YEAR")
    elif case4.match(date_input):
        # Example: 21-JUL-2016
        match_value = case4.match(date_input)
        day = __format_element__(match_value.group(1),"DAY")
        month = __format_element__(match_value.group(2),"MONTH")
        year = __format_element__(match_value.group(3),"YEAR")
    elif case5.match(date_input):
        # Example: 21st of July, 2016 or 10 Oct 2016
        match_value = case5.match(date_input)
        day = __format_element__(match_value.group(1),"DAY")
        month = __format_element__(match_value.group(4),"MONTH")
        year = __format_element__(match_value.group(5),"YEAR")
    elif case6.match(date_input):
        # Example: 20160721
        match_value = case6.match(date_input)
        day = __format_element__(match_value.group(3),"DAY")
        month = __format_element__(match_value.group(2),"MONTH")
        year = __format_element__(match_value.group(1),"YEAR")
    elif case7.match(date_input):
        # Example: "today", "tomorrow", "yesterday", "Tuesday", "Next Saturday", "Last Thursday"
        day,month,year = __relative_date__(date_input)
    elif case8.match(date_input):
        # Example: 1470443584
        match_value = case8.match(date_input)
        day,month,year = __date_since_epoch__(float(match_value.group(1)))
    else:
        print("\nERROR: The format you entered does not match any known date formats.")
        print(config.parse_date_usage)
        return None
    date_result = datetime.strptime("{0}-{1}-{2}".format(year,month,day),'%Y-%m-%d')
    if return_datetime:
        return date_result
    else:
        return str(datetime.strftime(date_result,output_format))


def __format_element__(value, element_type):
    """Internal function used for standardizing day, month, and year values"""
    if element_type == "YEAR":
        if len(value) == 0:
            result = '{}'.format(datetime.strftime(datetime.now(),'%Y'))
        elif len(value) == 2:
            result = '{0}{1}'.format(datetime.strftime(datetime.now(),'%Y')[0:2],value)
        else:
            result = value
    elif element_type == "MONTH":
        if re.match(r"^\d+$",value):
            result = value.zfill(2)
        else:
            for month in config.months:
                if value.upper() in month['strings']:
                    result = month['value']
                    break
    elif element_type == "DAY":
        result = value.zfill(2)
    return result


def __date_since_epoch__(value):
    """Internal function used for Unix datetime format"""
    day = time.strftime('%d',time.localtime(value))
    month = time.strftime('%m',time.localtime(value))
    year = time.strftime('%Y',time.localtime(value))
    return day,month,year


def __relative_date__(value):
    """Internal function used when inputs like 'today' and 'tuesday' are provided"""
    weekday_match = re.compile(r"^(next\s|last\s)?([a-z]+)$", re.IGNORECASE)
    weekday_int = None
    if value.upper() == "TODAY":
        return __get_elements__(datetime.now())
    elif value.upper() == "TOMORROW":
        return __get_elements__(datetime.now()+timedelta(days=1))
    elif value.upper() == "YESTERDAY":
        return __get_elements__(datetime.now()-timedelta(days=1))
    elif value.upper() == "TOMORROW":
        return __get_elements__(datetime.now()+timedelta(days=1))
    elif weekday_match.match(value).group(1):
        weekday_value = weekday_match.match(value).group(2)
        for weekday in config.weekdays:
            if weekday_value.upper() in weekday['strings']:
                weekday_int = int(weekday['value'])
                break
        if not weekday_int:
            print("\nERROR: The format you entered does not match any known date formats.")
            print(config.parse_date_usage)
            return None
        else:
            today_int = datetime.now().weekday()
            if weekday_match.match(value).group(1).upper() == 'NEXT ':
                if today_int <= weekday_int:
                    delta = (weekday_int+7) - today_int
                else:
                    delta = (weekday_int+14) - today_int
                return __get_elements__(datetime.now()+timedelta(days=delta))
            elif weekday_match.match(value).group(1).upper() == 'LAST ':
                if weekday_int < today_int:
                    delta = today_int - weekday_int
                else:
                    delta = (today_int+7) - weekday_int
                return __get_elements__(datetime.now()-timedelta(days=delta))
    else:
        for weekday in config.weekdays:
            if value.upper() in weekday['strings']:
                weekday_int = int(weekday['value'])
                break
        if not weekday_int:
            print("\nERROR: The format you entered does not match any known date formats.")
            print(config.parse_date_usage)
            return None
        else:
            today_int = datetime.now().weekday()
            if today_int <= weekday_int:
                delta = weekday_int - today_int
            else:
                delta = (weekday_int+7) - today_int
            return __get_elements__(datetime.now()+timedelta(days=delta))



def __get_elements__(date_input):
    day = datetime.strftime(date_input,'%d')
    month = datetime.strftime(date_input,'%m')
    year = datetime.strftime(date_input,'%Y')
    return day,month,year


if __name__ == '__main__':
    if len(sys.argv) == 2:
        __wrapper__(sys.argv[1])
    elif len(sys.argv) == 3:
        __wrapper__(sys.argv[1],sys.argv[2])
    else:
        print("ERROR: Invalid number of arguments\n")
        print(config.parse_date_usage)
        sys.exit()
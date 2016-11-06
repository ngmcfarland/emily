# DateParser Config

months = [
    {"strings": ["JAN","JANUARY"],"value": "01"},
    {"strings": ["FEB","FEBRUARY"],"value": "02"},
    {"strings": ["MAR","MARCH"],"value": "03"},
    {"strings": ["APR","APRIL"],"value": "04"},
    {"strings": ["MAY"],"value": "05"},
    {"strings": ["JUN","JUNE"],"value": "06"},
    {"strings": ["JUL","JULY"],"value": "07"},
    {"strings": ["AUG","AUGUST"],"value": "08"},
    {"strings": ["SEP","SEPTEMBER","SEPT"],"value": "09"},
    {"strings": ["OCT","OCTOBER"],"value": "10"},
    {"strings": ["NOV","NOVEMBER"],"value": "11"},
    {"strings": ["DEC","DECEMBER"],"value": "12"}
]

weekdays = [
    {"strings": ["MON","MONDAY"],"value": "0"},
    {"strings": ["TUE","TUESDAY"],"value": "1"},
    {"strings": ["WED","WEDNESDAY"],"value": "2"},
    {"strings": ["THU","THURSDAY","THUR"],"value": "3"},
    {"strings": ["FRI","FRIDAY"],"value": "4"},
    {"strings": ["SAT","SATURDAY"],"value": "5"},
    {"strings": ["SUN","SUNDAY"],"value": "6"}
]

numbers = [
    {"strings": ["FIRST","ONE"],"value": "01"},
    {"strings": ["SECOND","TWO"],"value": "02"},
    {"strings": ["THIRD","THREE"],"value": "03"},
    {"strings": ["FOURTH","FOUR"],"value": "04"},
    {"strings": ["FIFTH","FIVE"],"value": "05"},
    {"strings": ["SIXTH","SIX"],"value": "06"},
    {"strings": ["SEVENTH","SEVEN"],"value": "07"},
    {"strings": ["EIGHTH","EIGHT"],"value": "08"},
    {"strings": ["NINETH","NINE"],"value": "09"},
    {"strings": ["TENTH","TEN"],"value": "10"},
    {"strings": ["ELEVENTH","ELEVEN"],"value": "11"},
    {"strings": ["TWELFTH","TWELVE"],"value": "12"},
    {"strings": ["THIRTEENTH","THIRTEEN"],"value": "13"},
    {"strings": ["FOURTEENTH","FOURTEEN"],"value": "14"},
    {"strings": ["FIFTEENTH","FIFTEEN"],"value": "15"},
    {"strings": ["SIXTEENTH","SIXTEEN"],"value": "16"},
    {"strings": ["SEVENTEENTH","SEVENTEEN"],"value": "17"},
    {"strings": ["EIGHTEENTH","EIGHTEEN"],"value": "18"},
    {"strings": ["NINETEENTH","NINETEEN"],"value": "19"},
    {"strings": ["TWENTIETH","TWENTY"],"value": "20"},
    {"strings": ["TWENTY-FIRST","TWENTY-ONE"],"value": "21"},
    {"strings": ["TWENTY-SECOND","TWENTY-TWO"],"value": "22"},
    {"strings": ["TWENTY-THIRD","TWENTY-THREE"],"value": "23"},
    {"strings": ["TWENTY-FOURTH","TWENTY-FOUR"],"value": "24"},
    {"strings": ["TWENTY-FIFTH","TWENTY-FIVE"],"value": "25"},
    {"strings": ["TWENTY-SIXTH","TWENTY-SIX"],"value": "26"},
    {"strings": ["TWENTY-SEVENTH","TWENTY-SEVEN"],"value": "27"},
    {"strings": ["TWENTY-EIGHTH","TWENTY-EIGHT"],"value": "28"},
    {"strings": ["TWENTY-NINETH","TWENTY-NINE"],"value": "29"},
    {"strings": ["THIRTIETH","THIRTY"],"value": "30"},
    {"strings": ["THIRTY-FIRST","THIRTY-ONE"],"value": "31"}
]

times = [
    {"strings": ["QUARTER"],"value": 900},
    {"strings": ["HALF"],"value": 1800},
    {"strings": ["TEN","10"],"value": 600},
    {"strings": ["FIVE","5"],"value": 300},
    {"strings": ["HOUR","HOURS"],"value": 3600},
    {"strings": ["MINUTE","MINUTES"],"value": 60},
    {"strings": ["SECOND","SECONDS"],"value": 1}
]

holidays = [
    {"strings": ["NEW YEARS DAY","NEW YEARS"],"value": "01/01"},
    {"strings": ["MARTIN LUTHER KING DAY","MLK DAY"],"value": "01/18"},
    {"strings": ["GROUNDHOG DAY"],"value": "02/02"},
    {"strings": ["VALENTINES DAY"],"value": "02/14"},
    {"strings": ["PRESIDENTS DAY"],"value": "02/15"},
    {"strings": ["PI DAY"],"value": "03/14"},
    {"strings": ["ST PATRICKS DAY","SAINT PATRICKS DAY"],"value": "03/17"},
    {"strings": ["EASTER","EASTER SUNDAY"],"value": "03/27"},
    {"strings": ["CINCO DE MAYO"],"value": "05/05"},
    {"strings": ["MOTHERS DAY"],"value": "05/08"},
    {"strings": ["MEMORIAL DAY"],"value": "05/30"},
    {"strings": ["FATHERS DAY"],"value": "06/19"},
    {"strings": ["INDEPENDENCE DAY"],"value": "07/04"},
    {"strings": ["LABOR DAY"],"value": "09/05"},
    {"strings": ["COLUMBUS DAY"],"value": "10/10"},
    {"strings": ["HALLOWEEN"],"value": "10/31"},
    {"strings": ["VETERANS DAY"],"value": "11/11"},
    {"strings": ["CHRISTMAS EVE"],"value":"12/24"},
    {"strings": ["CHRISTMAS","CHRISTMAS DAY"],"value":"12/25"},
    {"strings": ["NEW YEARS EVE"],"value":"12/31"}
]

parse_date_usage = "\nUsage: python parse_date.py 'date_input' ['output_format',return_datetime]\n\nWhere: date_input     - Date in common, human-readable format\n       output_format  - Format for date result (using datetime format). Default: '%Y-%m-%d'\n       return_datetime  - True returns result as datetime type instead of string. Default: False\n"

parse_time_usage = "\nUsage: python parse_time.py 'time_input' ['output_format',return_datetime]\n\nWhere: time_input     - Time in common, human-readable format\n       output_format  - Format for time result (using datetime format). Default: '%H:%M:%S'\n       return_datetime  - True returns result as datetime type instead of string. Default: False\n"

parse_datetime_usage = "\nUsage: python parse_datetime.py 'datetime_input' ['output_format',return_datetime]\n\nWhere: datetime_input     - Date and time in common, human-readable format\n       output_format  - Format for datetime result (using datetime format). Default: '%Y-%m-%d %H:%M:%S'\n       return_datetime  - True returns result as datetime type instead of string. Default: False\n"
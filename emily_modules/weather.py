from conf import weather_conf as config
import requests
from datetime import datetime
from dateparser import parse_datetime
import sys

def get_full_results(city,app_id):
    r = requests.get('http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&APPID={}'.format(city,app_id))
    return r.json()

def get_temp(city):
    app_id = config.app_id
    if app_id == '<YOUR_API_KEY_HERE>':
        response = "Please enter your API key in the 'emily/modules/conf/weather_conf.py' file.\nA free API key can be obtained here:\nhttps://openweathermap.org/price"
        print(response)
        return response
    full_results = get_full_results(city,app_id)
    return full_results['main']['temp']

def get_sun_schedule(city,event,date_format='%I:%M %p'):
    app_id = config.app_id
    if app_id == '<YOUR_API_KEY_HERE>':
        response = "Please enter your API key in the 'emily/modules/conf/weather_conf.py' file.\nA free API key can be obtained here:\nhttps://openweathermap.org/price"
        print(response)
        return response
    full_results = get_full_results(city,app_id)
    if event.upper() == 'SUNRISE':
        return parse_datetime(full_results['sys']['sunrise'],output_format=date_format)
    elif event.upper() == 'SUNSET':
        return parse_datetime(full_results['sys']['sunset'],output_format=date_format)
    else:
        return None


if __name__ == '__main__':
    if len(sys.argv) == 3:
        aiml_wrapper(sys.argv[1],sys.argv[2])
    else:
        print("ERROR: Invalid number of arguments.")
        sys.exit(1)

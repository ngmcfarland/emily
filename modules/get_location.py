import requests
import json
import sys

def aiml_wrapper(context):
    location = where_am_i(context)
    print(location)

def where_am_i(context):
    url = 'http://freegeoip.net/json'
    r = requests.get(url)
    result = json.loads(r.text)
    if context == 'STATE':
        return result['region_name']
    elif context == 'CITY':
        return result['city']
    elif context == 'CITYSTATE':
        return '{}, {}'.format(result['city'],result['region_name'])
    else:
        return "Unknown context..."

if __name__ == '__main__':
    aiml_wrapper(sys.argv[1])
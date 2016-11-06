from conf import travel_time_conf as config
import requests
import sys

def main(origin,destination):
    key = config.api_key
    if key == '<YOUR_API_KEY_HERE>':
        response = "Please enter your API key in the 'emily/modules/conf/travel_time_conf.py' file.\nA free API key can be obtained here:\nhttps://developers.google.com/maps/pricing-and-plans/"
        print(response)
        return response
    origin = origin.replace(' ','+')
    destination = destination.replace(' ','+')
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins={}&destinations={}&key={}'.format(origin,destination,key)
    r = requests.get(url)
    response = r.json()
    if response['status'] == 'OK':
        return response['rows'][0]['elements'][0]['duration']['text']
    else:
        return "Something went wrong"


if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2])
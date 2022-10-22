import json
from urllib.request import urlopen
from urllib import parse
import re


def query_suggestions_by_name(train_station_name):
    url = "http://reiseauskunft.bahn.de/bin/ajax-getstop.exe/dn?REQ0JourneyStopsS0A=1&REQ0JourneyStopsS0G=" + parse.quote(train_station_name)
    request = urlopen(url)
    content = request.read()
    request.close()
    return content


def clean_suggestions(raw_suggestions):
    match = re.search('SLs\\.sls=(\\{.*\\});SLs\\.showSuggestion\\(\\);', str(raw_suggestions, "ISO-8859-1"))
    return match.group(1)


def select_train_station_id(cleaned_suggestions):
    decoded_suggestions = json.loads(cleaned_suggestions)['suggestions']
    if len(decoded_suggestions) < 1:
        return -1
    else:
        return decoded_suggestions[0]['extId']


def select_station_name(cleaned_suggestions):
    decoded_suggestions = json.loads(cleaned_suggestions)['suggestions']
    if len(decoded_suggestions) < 1:
        return None
    else:
        return decoded_suggestions[0]['value']


def get_train_station_id(train_station_name):
    raw_suggestions = query_suggestions_by_name(train_station_name)
    cleaned_suggestions = clean_suggestions(raw_suggestions)
    return select_train_station_id(cleaned_suggestions)


if __name__ == '__main__':
    train_station = 'H'
    station_id = get_train_station_id(train_station)
    print(station_id)

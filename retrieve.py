import requests
from bs4 import BeautifulSoup

import re
import pprint

from url_constructor import create_request_string
from settings import STATIONS_AND_TRAINS
from get_trainstation_ids import get_train_station_id


def _remove_leading_zeros(s):
    return re.search("0*(\\d*)", s).group(1)


def create_requests(use_train_id=True):

    train_stations = list(STATIONS_AND_TRAINS.keys())

    station_name_to_id = {
        station: _remove_leading_zeros(get_train_station_id(station))
        for station in train_stations
    }

    train_station_requests = []

    for station_name in train_stations:
        station_id = station_name_to_id[station_name]

        train_codes = STATIONS_AND_TRAINS[station_name] if use_train_id else [None]

        for train_code in train_codes:
            train_station_requests.append(create_request_string(station_id, train_code=train_code))

    return train_station_requests


def parse_row(row):
    parsed_row = {
        'planned_time': row.find_next('td', class_='time').text.strip(),
        'train_name': row.find_next('span', class_='nowrap').text.strip(),
        'platform': row.find_next('td', class_='platform').text.strip(),
        'message': row.find_next('td', class_='ris').text.strip()
    }
    direction_cell = row.find_next('td', class_='route')
    parsed_row['direction'] = direction_cell.find_next('span', class_='bold').text.strip()
    return parsed_row


def parse_request(r):
    print(r)

    soup = BeautifulSoup(requests.get(r).text, 'html.parser')

    rows = soup.findAll('tr', id=lambda x: x and x.startswith('journeyRow'))

    alerts = []

    for row in rows:
        info = row.find_next('td', class_='ris')

        # if not empty then something is wrong
        if info.text.strip() != '':
            # save info and platform just in case
            # TODO: parse what exactly is the problem
            potential_alert = parse_row(row)

            # if message is the same as planned time then it's not an actual delay
            if potential_alert['planned_time'] != potential_alert['message']:
                alerts.append(potential_alert)

    return alerts


def fetch_data(use_train_id=True):
    reqs = create_requests(use_train_id)
    alerts = [a for r in reqs for a in parse_request(r)]

    return alerts


if __name__ == '__main__':
    pprint.pprint(fetch_data(use_train_id=False))
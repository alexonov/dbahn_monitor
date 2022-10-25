"""
The goal is to find out if there are delays or cancellations
We only care about certain stations, i.e.
Hamburg -> station and station -> Hamburg

For that we query departures from the station and arrivals to the station

1. Departures to the station - we only need trains going TO Hamburg
    This is an easy case, we just parse the message as it is,
    the delay time is the time we care about

2. Arrivals - we only need trains coming FROM Hamburg
    This case in not that simple. We need to know the time of
    departure from Hamburg.
    So first we save make a list of all the train from Hamburg,
    then go look at the Hamburg departure board and check the status there.
    We do this only if the train id is there - otherwise we just post the message as is

"""
import requests
from bs4 import BeautifulSoup

import re

from url_constructor import create_request_string, BoardType
from settings import CENTRAL_STATION, STATIONS_TO_MONITOR
from get_trainstation_ids import get_train_station_id
from alert import Alert


def _remove_leading_zeros(s):
    return re.search("0*(\\d*)", s).group(1)


def fetch_data_departures(station_ids):
    departure_to_central_requests = [
        create_request_string(sid, board_type=BoardType.DEPARTURE) for sid in station_ids
    ]
    departure_alerts = [
        a
        for req in departure_to_central_requests
        for a in parse_departure(req)
        # only interested in trains going to Hamburg
        if a.is_same_direction(CENTRAL_STATION)
    ]
    return departure_alerts


def fetch_data_arrivals(station_ids):
    arrival_requests = [create_request_string(sid, board_type=BoardType.ARRIVAL) for sid in station_ids]

    # keep train id is missing - keep as is, otherwise go to hamburg board
    red_alerts = []
    train_ids = []
    for request in arrival_requests:
        print(f'Extracting arrival info for url {request}')

        for row in _find_journey_rows(request):
            alert = Alert.generate_from_row(row)
            if not alert.is_real_alert or alert.direction.lower() != CENTRAL_STATION.lower():
                continue

            if alert.train_id is not None:
                train_ids.append(alert.train_id)
            else:
                red_alerts.append(alert)

    print(f'Found {len(red_alerts)} red alerts from {CENTRAL_STATION}')

    print(f'Found {len(train_ids)} trains from {CENTRAL_STATION}: {train_ids}')

    central_station_id = _remove_leading_zeros(get_train_station_id(CENTRAL_STATION))
    departure_from_central_requests = [
        create_request_string(central_station_id, board_type=BoardType.DEPARTURE, train_code=train_id)
        for train_id in train_ids
    ]
    arrivals_alerts = [a for req in departure_from_central_requests for a in parse_departure(req)]
    return arrivals_alerts + red_alerts


def parse_departure(request):
    print(f'Extracting departing info from url: {request}')
    alerts = [Alert.generate_from_row(row) for row in _find_journey_rows(request)]
    alerts = [a for a in alerts if a.is_real_alert]
    return alerts


def _find_journey_rows(request):
    soup = BeautifulSoup(requests.get(request).text, 'html.parser')
    rows = soup.findAll('tr', id=lambda x: x and x.startswith('journeyRow'))
    return rows


def fetch_data():
    station_ids = [_remove_leading_zeros(get_train_station_id(station)) for station in STATIONS_TO_MONITOR]
    alerts = fetch_data_arrivals(station_ids) + fetch_data_departures(station_ids)

    return alerts


if __name__ == '__main__':
    r = create_arrival_request('Hamburg-Tonndorf')
    train_ids = extract_train_ids(r, 'Hamburg Hbf')


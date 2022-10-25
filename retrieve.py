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


def fetch_data_departures():
    alerts = []
    for station in STATIONS_TO_MONITOR:
        station_id = get_train_station_id(station)
        request = create_request_string(station_id, board_type=BoardType.DEPARTURE)
        print(f'Extracting departure from {station} to {CENTRAL_STATION}...')
        parsed_alert = parse_departure(request, from_station=station, to_station=CENTRAL_STATION)
        alerts.extend([a for a in parsed_alert if a.is_same_direction(CENTRAL_STATION)])
    return alerts


def fetch_data_arrivals():

    # keep train id is missing - keep as is, otherwise go to hamburg board
    no_train_alerts = []
    train_alerts = []
    for station in STATIONS_TO_MONITOR:
        station_id = get_train_station_id(station)
        request = create_request_string(station_id, board_type=BoardType.ARRIVAL)

        print(f'Extracting arrival to {station} for url {request}')

        for row in _find_journey_rows(request):
            alert = Alert.generate_from_row(row, from_station=CENTRAL_STATION, to_station=station)
            if not alert.is_real_alert or alert.direction.lower() != CENTRAL_STATION.lower():
                continue

            if alert.train_id is not None:
                train_alerts.append(alert)
            else:
                no_train_alerts.append(alert)

    print(f'Found {len(no_train_alerts)} no train alerts from {CENTRAL_STATION}')
    print(f'Found {len(train_alerts)} train alerts from {CENTRAL_STATION}')

    central_station_id = get_train_station_id(CENTRAL_STATION)

    arrival_alerts = []
    for train_alert in train_alerts:
        print(f'Extracting departure from {CENTRAL_STATION} to {train_alert.to_station} on a {train_alert.train_id} train...')
        request = create_request_string(
            central_station_id,
            board_type=BoardType.DEPARTURE,
            train_code=train_alert.train_id
        )
        arrival_alerts.extend(parse_departure(request, from_station=CENTRAL_STATION, to_station=train_alert.to_station))

    return arrival_alerts + no_train_alerts


def parse_departure(request, from_station, to_station):
    print(f'Extracting departing info from url: {request}')
    alerts = [
        Alert.generate_from_row(row, from_station=from_station, to_station=to_station)
        for row in _find_journey_rows(request)
    ]
    alerts = [a for a in alerts if a.is_real_alert]
    return alerts


def _find_journey_rows(request):
    soup = BeautifulSoup(requests.get(request).text, 'html.parser')
    rows = soup.findAll('tr', id=lambda x: x and x.startswith('journeyRow'))
    return rows


def fetch_data():
    alerts = fetch_data_arrivals() + fetch_data_departures()

    return alerts


if __name__ == '__main__':
    pass


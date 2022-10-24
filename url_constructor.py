from enum import Enum, auto
from dataclasses import dataclass
from urllib import parse


# url = 'http://reiseauskunft.bahn.de/bin/bhftafel.exe/dn?ld=9646&rt=1&input=%238002549&boardType=dep&time=actual&productsFilter=0001000000&start=yes'
BASE_URL = 'http://reiseauskunft.bahn.de/bin/bhftafel.exe/dn?ld=9646&rt=1&input=%23'


class TransportType(Enum):
    ICE = auto()
    IC = auto()
    Interregional = auto()
    Regional = auto()
    SBahn = auto()
    Bus = auto()
    Ship = auto()
    UBahn = auto()
    Tram = auto()
    Taxi = auto()


class BoardType:
    DEPARTURE = 'dep'
    ARRIVAL = 'arr'


def create_request_string(train_station_id, filter_setting=None, train_code=None, board_type='dep'):
    # use regional train by default
    filter_setting = filter_setting or TransportFilter(TransportType.Regional)

    url = f'{BASE_URL}{parse.quote(train_station_id)}&boardType={board_type}&time=actual&productsFilter={filter_setting}&start=yes'
    if train_code is not None:
        url += f'&REQTrain_name={train_code}'
    return url


@dataclass(init=False)
class TransportFilter:
    _selected_options: list

    def __init__(self, *args):
        # only valid filter options
        assert all(option in TransportType for option in args)

        # no duplicates
        assert len(args) == len(set(args))

        self._selected_options = args

    def __str__(self):
        filter_digits = [int(option in self._selected_options) for option in TransportType]
        return ''.join(str(d) for d in filter_digits)



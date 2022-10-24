CENTRAL_STATION = 'Hamburg Hbf'

STATIONS_TO_MONITOR = (
    'Hamburg-Tonndof',
    # "Klecken",

)

TRAIN_NUMBERS = [
    11340,  # 'RB81',
    # 81945,  # 'RB41'
]

STATIONS_AND_TRAINS = {
    'Hamburg Hbf': [
        11340,
        # 81945
    ],
    'Hamburg-Tonndof': [11340],
    # 'Klecken': [81945],
}

ROUTES = (
    ('Hamburg Hbf', 'Klecken'),
    ('Hamburg Hbf', 'Hamburg-Tonndof'),
)
#!venv/bin/python
from retrieve import fetch_data
from telegram_bot import send_alerts
from pathlib import Path
import json
from collections import deque
from settings import STATIONS_TO_MONITOR
from datetime import datetime


PROCESSED_ALERTS_PATH = Path('data/processed_alerts')
PROCESSED_ALERTS_FILE = PROCESSED_ALERTS_PATH / 'alerts.json'


# make sure file to store alerts exists
PROCESSED_ALERTS_PATH.mkdir(parents=True, exist_ok=True)
if not PROCESSED_ALERTS_FILE.exists():
    with open(PROCESSED_ALERTS_FILE, 'w') as f:
        f.write(json.dumps([]))


def main():
    print(f'Requesting status at {datetime.now().strftime("%d-%m-%Y %H:%M:%S")} for {",".join(STATIONS_TO_MONITOR)}')

    # get all alerts
    alerts = fetch_data()

    print(f'Found {len(alerts)} alerts')

    # keep only new alerts
    with open(PROCESSED_ALERTS_FILE, 'r') as f:
        processed_alerts = deque(json.load(f))

    new_alerts = [a for a in alerts if a.encoded_alert not in processed_alerts]

    print(f'{len(new_alerts)} alerts are new')

    # notify new alerts and save
    send_alerts(new_alerts)
    processed_alerts.extend([a.encoded_alert for a in new_alerts])

    with open(PROCESSED_ALERTS_FILE, 'w') as f:
        json.dump(list(processed_alerts), f)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        with open(PROCESSED_ALERTS_FILE, 'w') as f:
            f.write(json.dumps([]))
        raise e

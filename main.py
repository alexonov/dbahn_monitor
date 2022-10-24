from retrieve import fetch_data
from telegram_bot import send_alerts
from pathlib import Path
import json
from collections import deque
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

PROCESSED_ALERTS_PATH = Path('data/processed_alerts')
PROCESSED_ALERTS_FILE = PROCESSED_ALERTS_PATH / 'alerts.json'


# make sure file to store alerts exists
PROCESSED_ALERTS_PATH.mkdir(parents=True, exist_ok=True)
if not PROCESSED_ALERTS_FILE.exists():
    with open(PROCESSED_ALERTS_FILE, 'w') as f:
        f.write(json.dumps([]))


def main():
    # get all alerts
    alerts = fetch_data()

    logging.info(f'Found {len(alerts)} alerts')

    # keep only new alerts
    with open(PROCESSED_ALERTS_FILE, 'r') as f:
        processed_alerts = deque(json.load(f))

    new_alerts = [a for a in alerts if a.encoded_alert not in processed_alerts]

    logging.info(f'{len(new_alerts)} alerts are new')

    # notify new alerts and save
    send_alerts(new_alerts)
    processed_alerts.extend(new_alerts)

    with open(PROCESSED_ALERTS_FILE, 'w') as f:
        json.dump([a.encoded_alert for a in processed_alerts], f)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        with open(PROCESSED_ALERTS_FILE, 'w') as f:
            f.write(json.dumps([]))
        raise e

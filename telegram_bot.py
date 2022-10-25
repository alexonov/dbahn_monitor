import requests

from secrets import BOT_TOKEN, CHANNEL_ID
from alert import Alert


BASE_URL = 'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={MESSAGE}&parse_mode=Markdown'
UPDATES_URL = 'https://api.telegram.org/bot{TOKEN}/getUpdates'


def compile_url(message):
    return BASE_URL.format(
        TOKEN=BOT_TOKEN,
        CHAT_ID=CHANNEL_ID,
        MESSAGE=message
    )


def send_alerts(alerts: list[Alert]):
    for alert in alerts:
        notify(alert.formatted_alert)
        print(alert.formatted_alert)


def notify(message):
    requests.post(compile_url(message))


def get_updates():
    return requests.get(UPDATES_URL.format(TOKEN=BOT_TOKEN)).text


if __name__ == '__main__':
    notify('test')
    # print(get_updates())

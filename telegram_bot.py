import requests

from secrets import BOT_TOKEN, CHANNEL_ID


BASE_URL = 'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={MESSAGE}&parse_mode=Markdown'
UPDATES_URL = 'https://api.telegram.org/bot{TOKEN}/getUpdates'


def compile_url(message):
    return BASE_URL.format(
        TOKEN=BOT_TOKEN,
        CHAT_ID=CHANNEL_ID,
        MESSAGE=message
    )


def notify(alerts):
    for alert in alerts:
        formatted_alert = format_alert(alert)
        requests.post(compile_url(formatted_alert))


def format_alert(alert):
    return f"""Внимание!
    поезд: *{alert["train_name"]}*
    направление: *{alert["direction"]}*
    время: *{alert["planned_time"]}*
    платформа: *{alert["platform"]}*
    статус: *{alert["message"]}*
    """


def get_updates():
    return requests.get(UPDATES_URL.format(TOKEN=BOT_TOKEN)).text


if __name__ == '__main__':
    notify(['test'])
    # print(get_updates())

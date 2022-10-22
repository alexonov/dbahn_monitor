from retrieve import fetch_data
from telegram_bot import notify


def main():
    alerts = fetch_data(False)
    notify(alerts)


if __name__ == '__main__':
    main()
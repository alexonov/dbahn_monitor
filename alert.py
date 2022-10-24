import uuid
from typing import NamedTuple
import re


def _extract_span_text(cell, class_):
    try:
        return cell.find_next('span', class_=class_).text.strip()
    except AttributeError:
        return None


class Alert(NamedTuple):
    planned_time: str
    direction: str
    train_name: str
    platform: str
    message: str
    red_alert: str
    delay_on_time: str
    train_id: str

    @classmethod
    def generate_from_row(cls, row):
        message_cell = row.find_next('td', class_='ris')

        parsed_row = {
            'planned_time': row.find_next('td', class_='time').text.strip(),
            'train_name': row.find_next('span', class_='nowrap').text.strip(),
            'platform': row.find_next('td', class_='platform').text.strip(),
            'message': message_cell.text.strip()
        }
        direction_cell = row.find_next('td', class_='route')
        parsed_row['direction'] = _extract_span_text(direction_cell, class_='bold')
        parsed_row['red_alert'] = _extract_span_text(message_cell, class_='red')
        parsed_row['delay_on_time'] = _extract_span_text(message_cell, class_='delayOnTime bold')

        train_cell = row.find_all('td', class_='train')[1]
        parsed_row['train_id'] = re.search('(?<=\().+?(?=\))', train_cell.find_next('a').text).group()

        return cls(**parsed_row)

    @property
    def formatted_alert(self):
        return f"""
поезд: *{self.train_name}*
направление: *{self.direction}*
время: *{self.planned_time}*
платформа: *{self.platform}*
статус: *{self.message}*
        """

    @property
    def is_real_alert(self):
        # if message is the same as planned time then it's not an actual delay
        return self.planned_time != self.message and self.message != ''

    @property
    def is_red_alert(self):
        return self.red_alert != ''

    @property
    def encoded_alert(self):
        return uuid.uuid3(uuid.NAMESPACE_DNS, str(self))

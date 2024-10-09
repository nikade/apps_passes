import logging

import requests

from exceptions import TgBotSendException

logger = logging.getLogger(__name__)

class TgBot:
    def __init__(self, token: str, chat_id: int):
        self._token = token
        self._chat_id = chat_id
        self._bot_url = 'https://api.telegram.org/bot' + self._token + '/'

    def send_message(self, message: str):
        try:
            resp = requests.post(
                url=self._bot_url + 'sendMessage',
                # headers={'Content-Type': 'multipart/form-data'},
                params={'chat_id': self._chat_id, 'text': message}
            )
            if resp.status_code != 200:
                logging.error(f"error не могу отправить сообщение \"{message}\"\n")
                raise Exception

        except Exception as e:
            logging.error(f"Ошибка отправки сообщение в ТГ {str(e)}")
            raise TgBotSendException


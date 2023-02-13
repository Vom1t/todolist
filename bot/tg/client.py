import logging
import requests
from pydantic import ValidationError
from bot.tg.dc import GetUpdatesResponse, SendMessageResponse

logger = logging.getLogger(__name__)


class TgClient:
    def __init__(self, token):
        self.token = token

    def get_url(self, method: str):
        return f'https://api.telegram.org/bot{self.token}/{method}'

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        data = requests.get(self.get_url('getUpdates'), params={'timeout': timeout, 'offset': offset}).json()
        try:
            return GetUpdatesResponse(**data)
        except ValidationError:
            logger.error(f'Пришли не валидные данные: {data}')

    def send_message(self, chat_id: str, text: str) -> SendMessageResponse:
        data = requests.get(self.get_url('sendMessage'), params={'chat_id': chat_id, 'text': text}).json()
        try:
            return SendMessageResponse(**data)
        except ValidationError:
            logger.error(f'Пришли не валидные данные: {data}')

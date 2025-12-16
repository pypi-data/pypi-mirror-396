import json
import re
import requests
from django.conf import settings


class OnesignalService:
    def __init__(self, onesignal_tokens=None, message='New message', data_to_send=None, title=settings.PROJECT_NAME):
        self.send(onesignal_tokens=onesignal_tokens, message=message, data_to_send=data_to_send, title=title)

    def send(self, onesignal_tokens, message, data_to_send, title):
        if not onesignal_tokens:
            return False
        if not isinstance(onesignal_tokens, list):
            onesignal_tokens = [onesignal_tokens]

        valid_onesignal_tokens = [
            token for token in onesignal_tokens if re.match(r'^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$', token)
        ]

        if not valid_onesignal_tokens:
            return False

        onesignal_app_id = settings.ONESIGNAL_APP_ID
        onesignal_api_key = settings.ONESIGNAL_API_KEY

        if not onesignal_app_id or not onesignal_api_key:
            return False

        data = {
            'app_id': onesignal_app_id,
            'include_player_ids': valid_onesignal_tokens,
            'data': data_to_send or {},
            'contents': {"en": message},
            'headings': {"en": title},
        }

        url = 'https://onesignal.com/api/v1/notifications'
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f'Basic {onesignal_api_key}',
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            response_data = response.json()

            return True
        except requests.exceptions.RequestException as e:
            return False

import os
import requests

from dotenv import load_dotenv

load_dotenv()

SUCCESS = 200
PROCESSING = 102
FAILED = 400
INVALID_NUMBER = 160
MESSAGE_IS_EMPTY = 170
SMS_NOT_FOUND = 404
SMS_SERVICE_NOT_TURNED = 600

ESKIZ_EMAIL = os.getenv('ESKIZ_EMAIL')
ESKIZ_SECRET_KEY = os.getenv('ESKIZ_SECRET_KEY')


class SendSmsWithEskizApi:
    def __init__(self, message, phone, email=ESKIZ_EMAIL, password=ESKIZ_SECRET_KEY):
        self.message = message
        self.phone = phone
        self.spend = None
        self.email = email
        self.password = password

    def authorization(self):
        data = {
            'email': self.email,
            'password': self.password,
        }
        AUTHORIZATION_URL = 'http://notify.eskiz.uz/api/auth/login'

        r = requests.request('POST', AUTHORIZATION_URL, data=data)

        if r.json()['data']['token']:
            return r.json()['data']['token']
        else:
            return FAILED

    def send_message(self):
        token = self.authorization()

        if token == FAILED:
            return FAILED

        SEND_SMS_URL = "http://notify.eskiz.uz/api/message/sms/send"
        PAYLOAD = {
            'mobile_phone': str(self.phone),
            'message': self.message,
            'from': '4546',
        }
        FILES = []
        HEADERS = {
            'Authorization': f'Bearer {token}'
        }

        r = requests.request("POST", SEND_SMS_URL,
                             headers=HEADERS, data=PAYLOAD, files=FILES)

        return r.status_code

import requests


class SendSmsWithEskizApi:
    def __init__(self, message, phone, email='polatbekbeknazarov2003@gmail.com', password='S97ac7SfrA73BY7Ta1pFAJqJrrYyE1y96Qmj8JJ0'):
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
        token = r.json()['data']['token']

        return token

    def send_message(self):
        token = self.authorization()
        print(self.message)

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

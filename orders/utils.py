import requests


class SendSmsWithEskizApi:
    def __init__(
        self,
        message,
        phone,
        email="polatbekbeknazarov2003@gmail.com",
        password="S97ac7SfrA73BY7Ta1pFAJqJrrYyE1y96Qmj8JJ0",
    ):
        self.message = message
        self.phone = phone
        self.spend = None
        self.email = email
        self.password = password

    def authorization(self):
        data = {
            "email": self.email,
            "password": self.password,
        }
        authorization_url = "http://notify.eskiz.uz/api/auth/login"

        r = requests.request("POST", authorization_url, data=data)
        token = r.json()["data"]["token"]

        return token

    def send_message(self):
        token = self.authorization()

        send_sms_url = "http://notify.eskiz.uz/api/message/sms/send"
        payload = {
            "mobile_phone": str(self.phone),
            "message": self.message,
            "from": "4546",
        }
        files = []
        headers = {"Authorization": f"Bearer {token}"}

        r = requests.request(
            "POST", send_sms_url, headers=headers, data=payload, files=files
        )

        return r.status_code

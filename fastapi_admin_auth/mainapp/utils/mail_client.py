# Email Client
import base64
from pathlib import Path

import emails
from emails.template import JinjaTemplate as T
from azure.communication.email import EmailClient
from jinja2 import Template
from fastapi.templating import Jinja2Templates

__all__ = [
    "EmailClientBase",
    "EmailClientAzure"
]


class EmailClientBase:
    def __init__(
            self,
            user: str,
            password: str,
            host: str,
            port: int = 587,
            ssl: bool = False,
            from_mail: str = "corus@sk.com",
            from_name: str = "G.AI Engineering2 Team",
            corus_url: str = "http://app.corus-ai.net/",
    ):
        self.smtp_config = {
            'host': host,
            'port': port,
            'ssl': ssl,
            'user': user,
            'password': password
        }
        self.mail_from = (from_name, from_mail)
        self.from_name = from_name
        self.from_mail = from_mail
        self.corus_url = corus_url

    def send_create_account(
            self,
            recipient_name: str,
            recipient_mail: str,
            activate_url: str,
            api_key: str,
    ) -> int:
        """
        계정 생성 및 활성화 메일 발송
        """
        with open("../templates/create_account.html", "r") as f:
            contents = f.read()
            message = emails.html(subject=f"(SK C&C CODEV) {recipient_name} 님, 안녕하세요. 사용자 활성화 안내입니다.",
                                  html=T(contents),
                                  mail_from=self.mail_from)
            try:
                message.attach(data=open('../templates/manual.pdf', 'rb'), filename='manual.pdf')
            except FileNotFoundError:
                pass
            r = message.send(
                to=(recipient_name, recipient_mail),
                render={
                    'corus_url': self.corus_url,
                    'name': recipient_name,
                    'activate_url': activate_url,
                    'api_key': api_key,
                    'team': self.from_name
                }
            )
            return r.status_code

    def send_reset_password(
            self,
            recipient_name: str,
            recipient_mail: str,
            password: str,
    ) -> int:
        """
        PASSWORD 초기화 메일 발송
        """
        with open("../templates/reset_password.html", "r") as f:
            contents = f.read()
            message = emails.html(subject=f"(SK C&C CODEV) {recipient_name} 님, 안녕하세요. Password 초기화 안내입니다.",
                                  html=T(contents),
                                  mail_from=self.mail_from)

            r = message.send(
                to=(recipient_name, recipient_mail),
                render={
                    'corus_url': self.corus_url,
                    'name': recipient_name,
                    'password': password,
                    'team': self.from_name
                }
            )
            return r.status_code


class EmailClientAzure:
    def __init__(
            self,
            from_mail: str = "DoNotReply@4af00481-d7ac-4522-9236-654394d6cfc0.azurecomm.net",
            from_name: str = "G.AI Engineering2 Team",
            corus_url: str = "http://app.corus-ai.net/",
            connection_string: str = "endpoint=https://corus-email-comm.unitedstates.communication.azure.com/;accesskey=+Lv9Ps+JDNwwTexyTm6s6P5EzhVEcS0dqu8MT1eCmShW/A3iVD4Dj9jsTID79NTKAzkjxZJaBfpL3Y5fgCdbdA==",
            manual_url: str = ""
    ):
        self.base_dir = Path(Path(__file__).resolve().parent).resolve().parent
        self.sender_address = from_mail
        self.from_name = from_name
        self.corus_url = corus_url
        self.POLLER_WAIT_TIME = 10
        self.client = EmailClient.from_connection_string(connection_string)
        self.templates = Jinja2Templates(directory=str(Path(self.base_dir, 'templates')))
        self.manual_url = manual_url

    def send_create_account(
            self,
            recipient_name: str,
            recipient_mail: str,
            activate_url: str,
            api_key: str,
    ) -> bool:
        """
        계정 생성 및 활성화 메일 발송
        """
        template_html = self.templates.get_template("create_account.html")
        template_txt = self.templates.get_template("create_account.txt")

        message = {
            "senderAddress": self.sender_address,
            "recipients": {
                "to": [{"address": recipient_mail}],
            },
            "content": {
                "subject": f"(SK C&C CODEV) {recipient_name} 님, 안녕하세요. 사용자 활성화 안내입니다.",
                "plainText": template_txt.render(
                    corus_url=self.corus_url,
                    name=recipient_name,
                    activate_url=activate_url,
                    api_key=api_key,
                    team=self.from_name,
                    manual_url=self.manual_url
                ),
                "html": template_html.render(
                    corus_url=self.corus_url,
                    name=recipient_name,
                    activate_url=activate_url,
                    api_key=api_key,
                    team=self.from_name,
                    manual_url=self.manual_url
                )
            }
        }
        try:
            with open(f"{self.base_dir}/templates/manual.pdf", "rb") as file:
                file_bytes_b64 = base64.b64encode(file.read())
            message['attachments'] = [
                {
                    "name": "manual.pdf",
                    "contentType": "application/pdf",
                    "contentInBase64": file_bytes_b64.decode()
                }
            ]
        except FileNotFoundError as e:
            pass

        poller = self.client.begin_send(message)

        time_elapsed = 0
        while not poller.done():
            poller.wait(self.POLLER_WAIT_TIME)
            time_elapsed += self.POLLER_WAIT_TIME

            if time_elapsed > 18 * self.POLLER_WAIT_TIME:
                raise RuntimeError("Polling timed out.")

        if poller.result()["status"] == "Succeeded":
            print(f"Successfully sent the email (operation id: {poller.result()['id']})")
            return True
        else:
            raise RuntimeError(str(poller.result()["error"]))

    def send_reset_password(
            self,
            recipient_name: str,
            recipient_mail: str,
            password: str,
    ) -> bool:
        """
        PASSWORD 초기화 메일 발송
        """
        template_html = self.templates.get_template("reset_password.html")
        template_txt = self.templates.get_template("reset_password.txt")

        message = {
            "senderAddress": self.sender_address,
            "recipients": {
                "to": [{"address": recipient_mail}],
            },
            "content": {
                "subject": f"(SK C&C CODEV) {recipient_name} 님, 안녕하세요. Password 초기화 안내입니다.",
                "plainText": template_txt.render(
                    corus_url=self.corus_url,
                    admin_url=f"{self.corus_url}/api/corus/backend/dashboard",
                    name=recipient_name,
                    password=password,
                    team=self.from_name
                ),
                "html": template_html.render(
                    corus_url=self.corus_url,
                    admin_url=f"{self.corus_url}/api/corus/backend/dashboard",
                    name=recipient_name,
                    password=password,
                    team=self.from_name
                )
            }
        }
        poller = self.client.begin_send(message)

        time_elapsed = 0
        while not poller.done():
            poller.wait(self.POLLER_WAIT_TIME)
            time_elapsed += self.POLLER_WAIT_TIME

            if time_elapsed > 18 * self.POLLER_WAIT_TIME:
                raise RuntimeError("Polling timed out.")

        if poller.result()["status"] == "Succeeded":
            print(f"Successfully sent the email (operation id: {poller.result()['id']})")
            return True
        else:
            raise RuntimeError(str(poller.result()["error"]))

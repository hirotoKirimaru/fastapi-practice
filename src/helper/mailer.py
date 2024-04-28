from typing import Final
from email.header import Header
from email.message import EmailMessage
from smtplib import SMTP


class Mailer:
    class Local:
        # host: Final[str] = "mail"
        host: Final[str] = "localhost"
        port: Final[int] = 1025

        @classmethod
        def send(cls):
            sender = 'no-reply@example.com'
            receiver = '1@example.com'
            subject = 'Python SMTP Mail Subject'
            body_text = 'Hello, this is a test email sent by Python smtplib.'
            body_html = '<html>Hello, this is a test email sent by Python smtplib.</html>'

            msg = EmailMessage()
            msg.set_content(body_text)
            msg.add_alternative(body_html, subtype='html')

            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = receiver
            try:
                with SMTP(host=cls.host, port=cls.port) as smtp:
                    smtp.send_message(msg)
            except Exception as e:
                print(f"Failed to send email. Error {str(e)}")
                raise e

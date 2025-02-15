from email.message import EmailMessage
from enum import Enum
from smtplib import SMTP
from typing import Final, NamedTuple

from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template


class Mailer:

    class Body(NamedTuple):
        text: str
        html: str

    class Templates(NamedTuple):
        text: Template
        html: Template

    class MailExtension(str, Enum):
        TEXT = "txt"
        HTML = "html"

    @classmethod
    def get_templates(cls, path: str) -> Templates:
        file_loader = FileSystemLoader("src/resources/templates")
        env = Environment(loader=file_loader, undefined=StrictUndefined)
        template_text = env.get_template(f"{path}.{Mailer.MailExtension.TEXT.value}")
        template_html = env.get_template(f"{path}.{Mailer.MailExtension.HTML.value}")

        return template_text, template_html

    @classmethod
    def build_body(cls, path: str, params={}) -> Body:
        text, html = cls.get_templates(path)
        return text.render(**params), html.render(**params)

    class Local:
        # host: Final[str] = "mail"
        host: Final[str] = "localhost"
        port: Final[int] = 1025

        @classmethod
        def send(cls) -> None:
            sender = "no-reply@example.com"
            receiver = "1@example.com"
            subject = "Python SMTP Mail Subject"
            # body_text ,body_html = Mailer.build_body("signin", name='NAME')
            body_text, body_html = Mailer.build_body("signin", params={"name": "NAME"})

            # body_text = "Hello, this is a test email sent by Python smtplib."
            # body_html = (
            #     "<html>Hello, this is a test email sent by Python smtplib.</html>"
            # )

            msg = EmailMessage()
            msg.set_content(body_text)
            msg.add_alternative(body_html, subtype="html")

            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = receiver
            try:
                with SMTP(host=cls.host, port=cls.port) as smtp:
                    smtp.send_message(msg)
            except Exception as e:
                print(f"Failed to send email. Error {str(e)}")
                raise e

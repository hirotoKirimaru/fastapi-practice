from typing import Final, NamedTuple
from email.message import EmailMessage
from smtplib import SMTP
from enum import Enum
from minijinja import Environment

class Mailer:

    env = Environment(loader=lambda name: open(f"src/resources/templates/{name}").read())

    class Body(NamedTuple):
        text: str
        html: str

    class Templates(NamedTuple):
        text: str
        html: str

    class MailExtension(str, Enum):
        TEXT = "txt"
        HTML = "html"

    @classmethod
    def get_templates(cls, path: str) -> Templates:
        template_text = cls.env.loader(f"{path}.{Mailer.MailExtension.TEXT.value}")
        template_html = cls.env.loader(f"{path}.{Mailer.MailExtension.HTML.value}")

        return cls.Templates(template_text, template_html)

    @classmethod
    def build_body(cls, path: str, params={}) -> Body:
        text_template, html_template = cls.get_templates(path)
        return cls.Body(
            text=cls.env.render_str(text_template, **params),
            html=cls.env.render_str(html_template, **params)
        )

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

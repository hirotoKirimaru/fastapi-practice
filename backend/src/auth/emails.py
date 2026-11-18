"""認証まわりのメール。SMTP の設定（settings.emails_enabled）が無ければ送らずにログだけ出す。

ローカルでは infra/compose.yml の mailpit（SMTP 1025 / UI 8025）に送れる:
SMTP_HOST=localhost SMTP_PORT=1025 SMTP_TLS=false EMAILS_FROM_EMAIL=info@example.com
"""

import logging
import smtplib
from email.message import EmailMessage

from src.helper.config import settings
from src.models.user import User

logger = logging.getLogger(__name__)


def _send(to: str, subject: str, body: str) -> None:
    if not settings.emails_enabled:
        # トークンはログに出さない（ログを読める人が他人のパスワードを変えられてしまう）
        logger.warning(
            "メールの送信先が未設定なので送らない: to=%s subject=%s", to, subject
        )
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = to
    msg.set_content(body)
    smtp_cls = smtplib.SMTP_SSL if settings.SMTP_SSL else smtplib.SMTP
    assert settings.SMTP_HOST is not None
    with smtp_cls(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        if settings.SMTP_TLS and not settings.SMTP_SSL:
            smtp.starttls()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        smtp.send_message(msg)


def send_reset_password(user: User, token: str) -> None:
    link = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    _send(
        user.email,
        f"[{settings.PROJECT_NAME}] パスワードの再設定",
        f"{user.name} さん\n\n次のリンクからパスワードを再設定してください。\n{link}\n",
    )


def send_verify(user: User, token: str) -> None:
    link = f"{settings.FRONTEND_HOST}/verify?token={token}"
    _send(
        user.email,
        f"[{settings.PROJECT_NAME}] メールアドレスの確認",
        f"{user.name} さん\n\n次のリンクからメールアドレスを確認してください。\n{link}\n",
    )

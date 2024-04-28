from src.helper.mailer import Mailer


class TestMailer:
    class TestLocal:
        async def test_01(self, mocker):
            # GIVEN
            smtp_mock = mocker.patch("src.helper.mailer.SMTP")
            smtp_mock.return_value.__enter__.return_value.send_message = (
                mocker.MagicMock()
            )
            smtp = (
                smtp_mock.return_value.__enter__.return_value
            )  # This is the mock object for `smtp` in your `with` statement

            # WHEN
            Mailer.Local.send()

            # THEN
            assert smtp.send_message.called

            # メッセージ内容を取得
            msg = smtp.send_message.call_args[0][0]

            assert msg["Subject"] == "Python SMTP Mail Subject"
            assert msg["From"] == "no-reply@example.com"
            assert msg["To"] == "1@example.com"
            # assert msg.get_content() == "Hello, this is a test email sent by Python smtplib."

            # マルチパートメール
            assert msg.is_multipart()

            for part in msg.iter_parts():
                match part.get_content_type():
                    case "text/plain":
                        assert (
                            part.get_content()
                            == "Hello, this is a test email sent by Python smtplib.\n"
                        )
                    case "text/html":
                        assert (
                            part.get_content()
                            == "<html>Hello, this is a test email sent by Python smtplib.</html>\n"
                        )

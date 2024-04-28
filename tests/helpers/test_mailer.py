from src.helper.mailer import Mailer


class TestMailer:
    class TestLocal:
        async def test_01(self):
            _ = Mailer.Local.send()


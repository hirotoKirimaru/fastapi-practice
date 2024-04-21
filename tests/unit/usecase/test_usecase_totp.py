from src.usecase.usecase_totp import Totp


class TestTotp:
    class TestCreateSalt:
        async def test_salt(self):
            salt = Totp.create_salt()
            assert salt is not None

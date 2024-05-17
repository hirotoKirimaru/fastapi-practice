import pytest


class TestCase:

    def get_mailer_class(self, env):
        match(env):
            case "local":
                return self.DummyMailer
            case "dev" | "prod":
                return self.Mailer
            case _:
                raise ValueError(f"Unknown case: {env}")


    class DummyMailer:
        pass

    class Mailer:
        pass

    @pytest.mark.parametrize('env,clazz', [
        ("local", DummyMailer),
        ("dev", Mailer),
        ("prod", Mailer),
    ])
    def test_get_class(self, env, clazz):
        assert self.get_mailer_class(env) is clazz

    def test_invalid_case(self):
        with pytest.raises(ValueError) as e:
            self.get_mailer_class("stg")
        assert str(e.value) == "Unknown case: stg"

    # @pytest.mark.parametrize('month,ans', [
    #     ("local", 31),
    #     ("dev", 28),
    #     ("prod", 31),
    # ])
    # def test_end_date(self, env, ans):
    #     match(env, ):
    #         case
    #             result
    #
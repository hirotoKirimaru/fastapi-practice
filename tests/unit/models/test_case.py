import pytest
from dataclasses import dataclass

from pydantic import BaseModel


class TestCase:

    def get_mailer_class(self, env):
        match env:
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

    @pytest.mark.parametrize(
        "env,clazz",
        [
            ("local", DummyMailer),
            ("dev", Mailer),
            ("prod", Mailer),
        ],
    )
    def test_get_class(self, env, clazz):
        assert self.get_mailer_class(env) is clazz

    def test_invalid_case(self):
        with pytest.raises(ValueError) as e:
            self.get_mailer_class("stg")
        assert str(e.value) == "Unknown case: stg"

    @dataclass
    class Point:
        x: int
        y: int

    class Point2(BaseModel):
        x: int
        y: int

    def match_point(self, point: Point):
        match point:
            case self.Point(x=0, y=0):
                return "Origin"
            case self.Point(x=0, y=_):
                return "Y-axis"
            case self.Point(x=_, y=0):
                return "X-axis"
            case self.Point():
                return "Somewhere else"

    def match_point2(self, point: Point2):
        match point:
            case self.Point2(x=0, y=0):
                return "Origin"
            case self.Point2(x=0, y=_):
                return "Y-axis"
            case self.Point2(x=_, y=0):
                return "X-axis"
            case self.Point2():
                return "Somewhere else"

    def match_point3(self, x: int, y: int):
        match x, y:
            case 0, 0:
                return "Origin"
            case 0, _:
                return "Y-axis"
            case _, 0:
                return "X-axis"
            case _:
                return "Somewhere else"

    @pytest.mark.parametrize(
        "x, y, expected",
        [
            (0, 0, "Origin"),
            (0, 100, "Y-axis"),
            (100, 0, "X-axis"),
            (100, 100, "Somewhere else"),
        ],
    )
    def test_point(self, x, y, expected):
        assert self.match_point(self.Point(x=x, y=y)) == expected
        assert self.match_point2(self.Point2(x=x, y=y)) == expected
        assert self.match_point3(x=x, y=y) == expected

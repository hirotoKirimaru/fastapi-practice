from collections import namedtuple
from enum import Enum


class CsvHeaderColumn(int, Enum):
    """
    intを継承しているとvalueにアクセスしなくてもアクセスできる

    """

    ID = 1
    NAME = 2
    EMAIL = 3
    ADMIN_FLG = 4


class StrInherit(str, Enum):
    ADMIN = "ADMIN"


# metaclassの競合が起きるから、継承できない
# E   TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
# class DummyUser(User, Enum):
#     ADMIN = User(name="admin", email="admin@example.com")


DummyValue = namedtuple("DummyValue", ["name", "email"])


class DummyUser(Enum):
    ADMIN = DummyValue("admin", "admin@example.com")


def add(num1: int, num2: CsvHeaderColumn):
    return num1 + num2


class Test:
    def test_normal(self):
        # 正しくはこちらのアクセス
        assert CsvHeaderColumn.ID.value == 1

        assert CsvHeaderColumn.ID == 1
        assert CsvHeaderColumn.NAME == 2
        assert CsvHeaderColumn.EMAIL == 3
        assert CsvHeaderColumn.ADMIN_FLG == 4
        assert len(CsvHeaderColumn) == 4, f"定義している数({4})が一致していること"

    def test_add(self):
        assert add(1, CsvHeaderColumn.ID) == 2


class TestDummyUser:
    def test_normal(self):
        assert DummyUser.ADMIN.value.name == "admin"
        assert DummyUser.ADMIN.value.email == "admin@example.com"

        # assert DummyUserEnum.value[0] == "admin"

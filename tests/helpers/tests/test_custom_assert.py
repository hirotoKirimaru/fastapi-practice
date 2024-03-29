from datetime import date

import pytest

from tests.helpers.custom_assert import CustomAssert


@pytest.mark.parametrize(
    "object",
    [
        (1),
        ("1"),
        (True),
        (date.today()),
    ],
)
def test_01(object):
    assert CustomAssert.is_primitive(object) is True


# 配列にしておく
@pytest.mark.parametrize(
    "object",
    [
        (["1"]),
    ],
)
def test_02(object):
    assert CustomAssert.is_primitive(object) is False

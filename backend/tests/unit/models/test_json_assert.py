import json

import pytest

"""
json比較する際には、一度辞書型にしてから比較する。
"""


def test_01():
    actual = """
    {
      "parent": {
        "id": 100,
        "name": "kirimaru",
        "children":  [
          {
            "id": 101
          },
          {
            "id": 102
          }
        ]
      }
    }
    """
    expected = """
    {
      "parent": {
        "name": "kirimaru",
        "id": 100,
        "children":  [
          {
            "id": 101
          },
          {
            "id": 102
          }
        ]
      }
    }
    """

    assert json.loads(actual) == json.loads(expected)
    # assert actual == expected


@pytest.mark.skipif(True, reason="ソート順番が違うのを実行する方法分からず")
def test_02():
    actual = """
    {
      "ids": [
        {"id": 1},
        {"id": 2}
      ]
    }
    """
    expected = """
    {
      "ids": [
        {"id": 2},
        {"id": 1}
      ]
    }
    """

    assert sorted(json.loads(actual).items()) == sorted(json.loads(expected).items())


@pytest.mark.skipif(True, reason="ソート順番が違うのを実行する方法分からず")
def test_03():
    actual = """
    {
      "parent": {
        "id": 100,
        "name": "kirimaru",
        "children":  [
          {
            "id": 101
          },
          {
            "id": 102
          }
        ]
      }
    }
    """
    expected = """
    {
      "parent": {
        "name": "kirimaru",
        "id": 100,
        "children":  [
          {
            "id": 102
          },
          {
            "id": 101
          }
        ]
      }
    }
    """
    print("***********")
    print(json.loads(actual)["parent"]["chidren"])
    print(json.loads(actual)["parent"]["chidren"].items())
    # print(json.loads(actual)["children"].items())

    assert sorted(json.loads(actual).items()) == sorted(json.loads(expected).items())

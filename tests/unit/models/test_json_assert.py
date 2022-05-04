import pytest
import json

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

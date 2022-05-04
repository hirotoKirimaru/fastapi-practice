import pytest
import json


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

    assert json.loads(actual) == json.loads(expected)

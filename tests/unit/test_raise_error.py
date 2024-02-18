import json
import logging
import traceback

class TestRaiseError:
    async def test_01(self):
        try:
            try:
                1 / 0
            except ZeroDivisionError as e:
                raise ValueError("ERROR")
                # raise ValueError("ERROR") from e
                # raise ValueError("ERROR") from None
        except Exception as e:
            print(traceback.format_exc())

        try:
            try:
                1 / 0
            except ZeroDivisionError as e:
                # raise ValueError("ERROR")
                raise ValueError("ERROR") from e
                # raise ValueError("ERROR") from None
        except Exception as e:
            print(traceback.format_exc())

        try:
            try:
                1 / 0
            except ZeroDivisionError as e:
                # raise ValueError("ERROR")
                # raise ValueError("ERROR") from e
                raise ValueError("ERROR") from None
        except Exception as e:
            print(traceback.format_exc())



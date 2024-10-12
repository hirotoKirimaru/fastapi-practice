from src.schemas.common import CustomEmailStr
from pydantic import BaseModel, ValidationError
import pytest


class TestCustomEmailStr:
    class _Test(BaseModel):
        email: CustomEmailStr

    class TestIsValid:
        @pytest.mark.parametrize(
            "value, expected",
            [
                ("aiueo@example.com", True),
                ("AIUEO@example.com", True),
                ("aiueo+０@example.com", False),
                ("aiueo+あいうえお@example.com", False),
                ("あいうえお+あいうえお@example.com", False),
            ],
        )
        def test_is_valid(self, value, expected):
            if expected:
                TestCustomEmailStr._Test(email=value)
            else:
                with pytest.raises(ValidationError):
                    TestCustomEmailStr._Test(email=value)

        @pytest.mark.parametrize(
            "value",
            [
                ("aiueo@example.com"),
                ("AIUEO@example.com"),
            ],
        )
        def test_is_lower(self, value):
            assert TestCustomEmailStr._Test(email=value).email == value.lower()
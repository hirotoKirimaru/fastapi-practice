import logging
import re
from typing import Any, Type

from pydantic import EmailStr, GetCoreSchemaHandler
from pydantic_core import core_schema


class CustomEmailStr(EmailStr):

    @classmethod
    def validate_half_and_full_email(cls, value: str) -> str:
        lower_value = value.lower()
        if not re.search(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", lower_value):
            # if not re.search(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", lower_value):
            logging.warn(f"Invalid email address: {value}")
            raise ValueError("ERROR.EMAIL_VALIDATION")
        return lower_value

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        email_schema = handler.generate_schema(EmailStr)
        return core_schema.chain_schema(
            [
                email_schema,
                core_schema.no_info_after_validator_function(
                    cls.validate_half_and_full_email, core_schema.str_schema()
                ),
            ]
        )

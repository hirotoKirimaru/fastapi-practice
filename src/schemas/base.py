from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_serializer
from pydantic.alias_generators import to_camel

from src.helper.datetime_resolver import DatetimeResolver


class CustomModel(BaseModel):
    #
    model_config = ConfigDict(
        from_attributes=True,
        alias_generator=to_camel,
        populate_by_name=True,
        strict=True,
    )



    # @model_serializer(mode="wrap")
    # def serialize_datetime(self, handler, info) -> dict:
    #     # 標準のシリアライズ処理を実行
    #     result = handler(self)
    #
    #     # datetimeフィールドを一括変換
    #     for field_name, value in self.__dict__.items():
    #         field_type = self.model_fields[field_name].annotation
    #         if field_type is datetime or isinstance(value, datetime):
    #             result[field_name] = DatetimeResolver.enforce_utc(value)
    #
    #     return result
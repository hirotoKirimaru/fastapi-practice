import json
from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

from pydantic import BaseModel, PlainSerializer, field_serializer


class _TestModel(BaseModel):
    dt: datetime
    normal_dt: datetime

    @field_serializer("dt")
    def serialize_datetime(self, dt: datetime, _info):
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class TestFieldSerializer:
    async def test_01(self):
        dt = datetime(2024, 12, 1, 2, 3, 4, tzinfo=ZoneInfo("UTC"))
        model = _TestModel(dt=dt, normal_dt=dt)
        actual_str = model.model_dump_json()
        actual_dict = json.loads(actual_str)

        assert actual_dict.get("dt") == "2024-12-01 02:03:04"
        assert actual_dict.get("normal_dt") == "2024-12-01T02:03:04Z"


CustomDatetime = Annotated[
    datetime,
    PlainSerializer(lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")),
    # PlainValidator(lambda dt: datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')), # str -> datetime, datetime -> strが混ざるのでNG。
]


class _TestModel2(BaseModel):
    dt: CustomDatetime
    normal_dt: datetime


class TestCustomDatetime:
    async def test_serialize(self):
        dt = datetime(2024, 12, 1, 2, 3, 4, tzinfo=ZoneInfo("UTC"))
        model = _TestModel2(dt=dt, normal_dt=dt)
        actual_str = model.model_dump_json()
        actual_dict = json.loads(actual_str)

        assert actual_dict.get("dt") == "2024-12-01 02:03:04"
        assert actual_dict.get("normal_dt") == "2024-12-01T02:03:04Z"

    async def test_deserialize(self):
        # GIVEN
        dt = datetime(2024, 12, 1, 2, 3, 4, tzinfo=ZoneInfo("UTC"))
        model = _TestModel2(dt=dt, normal_dt=dt)
        actual_str = model.model_dump_json()

        # WHEN
        actual = _TestModel2.model_validate_json(actual_str)
        # シリアライズ時にTZが削除されている
        assert actual.dt == dt.replace(tzinfo=None)
        assert actual.normal_dt == dt

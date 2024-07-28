from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic import BaseModel, field_serializer, PlainSerializer
import json
from typing import Annotated
from pydantic import BaseModel, PlainSerializer

class _TestModel(BaseModel):
    dt: datetime
    normal_dt: datetime

    @field_serializer('dt')
    def serialize_datetime(self, dt: datetime, _info):
        return dt.strftime('%Y-%m-%d %H:%M:%S')

class TestFieldSerializer:
    async def test_01(self):
        dt = datetime(2024, 12, 1, 2, 3, 4, tzinfo=ZoneInfo('UTC'))
        model = _TestModel(dt=dt, normal_dt=dt)
        actual_str = model.model_dump_json()
        actual_dict = json.loads(actual_str)

        assert actual_dict.get('dt') == "2024-12-01 02:03:04"
        assert actual_dict.get('normal_dt') == "2024-12-01T02:03:04Z"


CustomDatetime = Annotated[
    datetime,
    PlainSerializer(lambda dt: dt.strftime('%Y-%m-%d %H:%M:%S'))
]

class _TestModel2(BaseModel):
    dt: CustomDatetime
    normal_dt: datetime

class TestCustomDatetime:
    async def test_01(self):
        dt = datetime(2024, 12, 1, 2, 3, 4, tzinfo=ZoneInfo('UTC'))
        model = _TestModel2(dt=dt, normal_dt=dt)
        actual_str = model.model_dump_json()
        actual_dict = json.loads(actual_str)

        assert actual_dict.get('dt') == "2024-12-01 02:03:04"
        assert actual_dict.get('normal_dt') == "2024-12-01T02:03:04Z"
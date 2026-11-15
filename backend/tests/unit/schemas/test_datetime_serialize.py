import json
from datetime import datetime
from typing import Annotated
from zoneinfo import ZoneInfo

import pytest
from pydantic import AfterValidator, BaseModel, PlainSerializer, field_serializer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.helper.datetime_resolver import DatetimeResolver
from src.models.user import User


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


# def enforce_utc(value: datetime) -> datetime:
#     if value.tzinfo is None:  # タイムゾーン未設定の場合
#         value = value.replace(tzinfo=ZoneInfo("UTC"))  # UTCとみなす
#     return value.astimezone(tz=ZoneInfo("UTC"))  # UTCに変換


CustomDatetime = Annotated[
    datetime,
    AfterValidator(DatetimeResolver.enforce_utc),
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
        # ようにしていたが、AfterValidatorで追加するようにしたので問題なし

        # assert actual.dt == dt.replace(tzinfo=None)
        assert actual.dt == dt
        assert actual.normal_dt == dt


# class _TestModel3(CustomModel):
class _TestModel3(BaseModel):
    dt: datetime | None = None
    dt_2: CustomDatetime | None = None


class TestTimezone:
    async def test_01(self):
        """
        tzありとtzありは比較可能
        """
        dt_1 = datetime(2024, 12, 1, 2, 3, 4, tzinfo=ZoneInfo("UTC"))
        dt_2 = datetime(2024, 12, 1, 2, 3, 4, tzinfo=ZoneInfo("UTC"))

        assert dt_1 >= dt_2

    async def test_02(self):
        """
        tzありとなしは比較不可
        """
        dt_1 = datetime(2024, 12, 1, 2, 3, 4)
        dt_2 = datetime(2024, 12, 1, 2, 3, 4, tzinfo=ZoneInfo("UTC"))

        with pytest.raises(TypeError) as e:
            dt_1 >= dt_2

        assert e.type is TypeError

    async def test_03(self):
        """
        pydantic経由しても同様
        """
        model_1 = _TestModel3(dt="2024-12-01T02:03:04")
        dt_1 = datetime(2024, 12, 1, 2, 3, 4)

        assert model_1.dt >= dt_1

    async def test_04(self):
        """
        pydantic
        """
        model_1 = _TestModel3(dt="2024-12-01T02:03:04")
        dt_1 = datetime(2024, 12, 1, 2, 3, 4, tzinfo=ZoneInfo("UTC"))

        with pytest.raises(TypeError) as e:
            model_1.dt >= dt_1

        assert e.type is TypeError

    async def test_05(self):
        """
        pydanticの入力値も必要
        """
        model_1 = _TestModel3(dt="2024-12-01T02:03:04Z")
        dt_1 = datetime(2024, 12, 1, 2, 3, 4, tzinfo=ZoneInfo("UTC"))

        assert model_1.dt >= dt_1

    async def test_06(self):
        """
        pydanticの入力値も必要
        """
        model_1 = _TestModel3(dt_2="2024-12-01T02:03:04")
        dt_1 = datetime(2024, 12, 1, 2, 3, 4, tzinfo=ZoneInfo("UTC"))

        assert model_1.dt_2 >= dt_1

    async def test_07(self):
        """
        pydanticの入力値も必要
        """
        model_1 = _TestModel3(dt_2="2024-12-01T02:03:04Z")
        dt_1 = datetime(2024, 12, 1, 2, 3, 4, tzinfo=ZoneInfo("UTC"))

        assert model_1.dt_2 >= dt_1

    async def test_08(self, db: AsyncSession):
        dt_1 = datetime(2024, 12, 1, 2, 3, 4, tzinfo=ZoneInfo("UTC"))

        user = User(name="test", email="test@example.com", soft_destroyed_at=dt_1)
        db.add(user)
        await db.flush()

        # ここまではTZある
        assert user.soft_destroyed_at >= dt_1

        db.expunge(user)

        new_user = (await db.execute(select(User))).scalars().first()
        assert new_user

        # SQLAlchemyを経由したことによって欠落する
        with pytest.raises(TypeError) as e:
            new_user.soft_destroyed_at >= dt_1

        assert e.type is TypeError

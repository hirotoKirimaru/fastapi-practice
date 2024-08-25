from sqlalchemy import and_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.orm import joinedload
from datetime import datetime

import pytest

import src.crud.user

# import logging
from src.models.user import User
from src.models.organization import Organization


class TestUser:
    class TestDefault:
        async def test_01(self, db: AsyncSession) -> None:
            # logging.basicConfig()
            # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

            user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
            user2 = User(id=2, name="11", email="a@example.com", organization_id=1)
            user3 = User(id=3, name="11", email="a@example.com", organization_id=1)
            db.add(user1)
            db.add(user2)
            db.add(user3)
            await db.commit()

            query: select = select(User)

            condition = and_(User.id == 1)

            query = query.where(condition)
            actual = (await db.execute(query)).scalars().all()

            # assert user1.id == actual[0].id
            assert len(actual) == 1

        async def test_02(self, db: AsyncSession) -> None:
            user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
            user2 = User(id=2, name="11", email="a@example.com", organization_id=1)
            user3 = User(id=3, name="11", email="a@example.com", organization_id=1)
            db.add(user1)
            db.add(user2)
            db.add(user3)
            await db.commit()

            query: select = select(User)

            # 最後の条件で上書き
            condition = and_(User.id == 1)
            condition = and_(User.organization_id == 1)

            query = query.where(condition)
            actual = (await db.execute(query)).scalars().all()

            # assert user1.id == actual[0].id
            assert len(actual) == 3

        async def test_03(self, db: AsyncSession) -> None:
            user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
            user2 = User(id=2, name="11", email="a@example.com", organization_id=1)
            user3 = User(id=3, name="11", email="a@example.com", organization_id=1)
            db.add(user1)
            db.add(user2)
            db.add(user3)
            await db.commit()

            query: Select = select(User)

            # 条件をまとめる
            criteria = []
            criteria.append(and_(User.id == 1))
            criteria.append(and_(User.organization_id == 1))

            query = query.where(*criteria)
            actual = (await db.execute(query)).scalars().all()

            # assert user1.id == actual[0].id
            assert len(actual) == 1

    class TestName:
        async def test_01(self, db: AsyncSession):
            user1 = User(
                id=1, name="kirimaru", email="a@example.com", organization_id=1
            )
            db.add(user1)
            await db.commit()

            query: Select = select(User).where(User.id == 1)
            result = (await db.execute(query)).scalars().first()
            assert result.display_name == "kirimaru"

        async def test_soft_destroyed_name(self, db: AsyncSession):
            user1 = User(
                id=1,
                name="kirimaru",
                email="a@example.com",
                organization_id=1,
                soft_destroyed_at=datetime.now(),
            )
            db.add(user1)
            await db.commit()

            query: Select = select(User).where(User.id == 1)
            result = (await db.execute(query)).scalars().first()
            assert result.display_name == "削除済ユーザ"

        async def test_criteria_is_db_value(self, db: AsyncSession):
            user1 = User(
                id=1,
                name="kirimaru",
                email="a@example.com",
                organization_id=1,
                soft_destroyed_at=datetime.now(),
            )
            db.add(user1)
            await db.commit()

            query: Select = select(User).where(User.name == "kirimaru")
            result = (await db.execute(query)).scalars().first()
            assert result.display_name == "削除済ユーザ"

        async def test_cant_find_app_name(self, db: AsyncSession):
            """
            DBの kirimaru ではなく、Appで加工した「削除済ユーザ」で検索するので、Appを経由すると取得できない。
            """
            user1 = User(
                id=1,
                name="kirimaru",
                email="a@example.com",
                organization_id=1,
                soft_destroyed_at=datetime.now(),
            )
            db.add(user1)
            name = user1.display_name
            await db.commit()

            query: Select = select(User).where(User.name == name)
            result = (await db.execute(query)).scalars().first()
            assert result is None

        async def test_setter(self, db: AsyncSession):
            user1 = User(
                id=1, name="kirimaru", email="a@example.com", organization_id=1
            )
            db.add(user1)
            await db.commit()

            query: Select = select(User).where(User.id == 1)
            result = (await db.execute(query)).scalars().first()
            result.name = "UPDATE_NAME"
            db.add(result)
            await db.commit()

            result = (await db.execute(query)).scalars().first()
            assert result.name == "UPDATE_NAME"

    class TestFindByEmail:
        class TestPartialMatch:
            async def test_parameter_upper(self, db: AsyncSession):
                user1 = User(
                    id=1, name="kirimaru", email="a@example.com", organization_id=1
                )
                db.add(user1)
                await db.commit()

                parameter = "A@EXAMPLE.COM"
                # SELECT users.id, users.name, users.email, users.soft_destroyed_at, users.organization_id, users.birth_day, users.salt, organizations_1.id AS id_1
                # FROM users LEFT OUTER JOIN organizations AS organizations_1 ON organizations_1.id = users.organization_id
                #   NOTE: ilike だとこうなる
                # WHERE lower(users.email) LIKE lower(:email_1)
                result = await src.crud.user.find_by_email(db, email=parameter)
                assert result.id == user1.id

            async def test_parameter_lower(self, db: AsyncSession):
                user1 = User(
                    id=1, name="kirimaru", email="A@EXAMPLE.COM", organization_id=1
                )
                db.add(user1)
                await db.commit()

                parameter = "a@example.com"
                result = await src.crud.user.find_by_email(db, email=parameter)
                assert result.id == user1.id

            async def test_lower_case(self, db: AsyncSession):
                """
                ilikeを使用しないパターン
                """
                user1 = User(
                    id=1, name="kirimaru", email="a@example.com", organization_id=1
                )
                db.add(user1)
                await db.commit()

                parameter = "A@EXAMPLE.COM"
                query = select(User).where(
                    func.lower(User.display_email) == parameter.lower()
                )
                result = (await db.execute(query)).scalars().first()
                assert result.id == user1.id


class TestUserRelationShip:
    async def test_01(self, db: AsyncSession):
        user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
        db.add(user1)
        await db.commit()

        query: Select = select(User).where(User.id == 1)
        result = (await db.execute(query)).scalars().first()
        with pytest.raises(MissingGreenlet):
            _ = result.organization

    async def test_02(self, db: AsyncSession):
        user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
        user2 = User(id=2, name="22", email="b@example.com", organization_id=1)
        user3 = User(id=3, name="33", email="c@example.com", organization_id=1)
        user_ng = User(id=100, name="100", email="100@example.com", organization_id=2)
        organization_1 = Organization(id=1)
        organization_2 = Organization(id=2)
        db.add(user1)
        db.add(user2)
        db.add(user3)
        db.add(organization_1)

        db.add(user_ng)
        db.add(organization_2)
        await db.commit()

        query: Select = (
            select(User).options(joinedload(User.organization)).where(User.id == 1)
        )
        result = (await db.execute(query)).scalars().first()
        assert result.organization is not None

        # NOTE: 以降はSQLの確認
        # 実行時にLeft outer joinがいいか、別でID検索したほうが総合的に早いか…？
        # https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.relationship.params.lazy
        query: Select = select(User).where(User.id == 2)
        result = (await db.execute(query)).scalars().first()
        assert result.organization is not None

        query: Select = select(User).where(User.id == 3)
        result = (await db.execute(query)).scalars().first()
        assert result.organization is not None

        # NOTE: organization2, 3, 4 を定義していなければ、ここでエラーになる
        query: Select = select(User).where(User.id == 100)
        result = (await db.execute(query)).scalars().first()
        assert result.organization is not None
        # with pytest.raises(MissingGreenlet) as e:
        #     _ = result.organization

    async def test_immediate(self, db: AsyncSession):
        """
        これを有効活用した方が早いのかも…。
        """
        user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
        user2 = User(id=2, name="22", email="b@example.com", organization_id=1)
        user3 = User(id=3, name="33", email="c@example.com", organization_id=1)
        organization_1 = Organization(id=1)
        db.add(user1)
        db.add(user2)
        db.add(user3)
        db.add(organization_1)
        await db.commit()

        query: Select = select(User).where(User.id == 1)
        result = (await db.execute(query)).scalars().first()
        assert result.organization4 is not None

        # NOTE: 以降はSQLの確認
        # 実行時にLeft outer joinがいいか、別でID検索したほうが総合的に早いか…？
        # https://docs.sqlalchemy.org/en/20/orm/relationship_api.html#sqlalchemy.orm.relationship.params.lazy
        # lazy=immediateだけの方がいいかも。
        query: Select = select(User).where(User.id == 2)
        result = (await db.execute(query)).scalars().first()
        assert result.organization4 is not None

        query: Select = select(User).where(User.id == 3)
        result = (await db.execute(query)).scalars().first()
        assert result.organization4 is not None

    async def test_not_lazy_default(self, db: AsyncSession):
        """
        lazyがselectだけダメな模様？


        :param db:
        :return:
        """
        user1 = User(id=1, name="11", email="a@example.com", organization_id=1)
        organization_1 = Organization(id=1)
        db.add(user1)
        db.add(organization_1)
        await db.commit()

        query: Select = select(User).where(User.id == 1)
        result = (await db.execute(query)).scalars().first()
        assert result.organization2 is not None
        assert result.organization3 is None

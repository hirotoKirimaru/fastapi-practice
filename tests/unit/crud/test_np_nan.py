import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user import User


class TestNpNan:

    async def test_01(self, db: AsyncSession) -> None:
        """
        TODO: 昔はこれでエラーになることがあった
        """
        query = select(User).where(User.id.in_([np.nan]))
        actual = (await db.execute(query)).scalars().all()

        assert len(actual) == 0

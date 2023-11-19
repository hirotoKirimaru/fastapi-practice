import pytest
from sqlalchemy.ext.asyncio import AsyncSession


class TestUser:
    @pytest.mark.asyncio
    async def test_get_single(self, db: AsyncSession):
        # Given
        print([x for x in range(10)])
        # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        print(*[x for x in range(10)])
        # 0 1 2 3 4 5 6 7 8 9

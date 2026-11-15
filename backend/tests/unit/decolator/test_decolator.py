import pytest


def reset_auto_increment(table_name: str, count: int = 1):
    def _reset_auto_increment(func):
        async def wrapper(*args, **kwargs):
            # いい感じにDBのリセットがしたい
            print("***before****")
            print(f"table_name: {table_name} count: {count}")
            await func(*args, **kwargs)
            print("***after***")

        return wrapper

    return _reset_auto_increment


def reset_auto_increment2(table_name: str, count: int = 1):
    def _reset_auto_increment2(func):
        def wrapper(*args, **kwargs):
            # いい感じにDBのリセットがしたい
            print("***before****")
            print(f"table_name: {table_name} count: {count}")
            func(*args, **kwargs)
            print("***after***")

        return wrapper

    return _reset_auto_increment2


# TODO: decolatorに対して asyncがうまく効かないみたい
# @reset_auto_increment("users")
@pytest.mark.asyncio
async def test_01() -> None:
    assert 1 == 1


@reset_auto_increment2("organizations", count=100)
def test_02() -> None:
    assert 2 == 2

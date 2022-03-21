import pytest


class TestNested:
    """
    PytestでNestedしたテストクラスを書きたいときのやり方

    """
    class TestMethodA:
        def test_1(self):
            assert 1 == 1

    class TestMethodB:
        class TestConditionA:
            def test_1(self):
                assert 1 == 1

        class TestConditionB:
            def test_1(self, condition_a):
                assert condition_a == 1

            def test_2(self, condition_b):
                assert condition_b == 2


@pytest.fixture
def condition_a():
    return 1


@pytest.fixture
def condition_b():
    return 2

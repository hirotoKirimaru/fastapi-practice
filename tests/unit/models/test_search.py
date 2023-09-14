from typing import Dict
import pytest
import time

import random


skip: bool = True

# 10回やった平均を取る


@pytest.mark.skipif(skip, reason="ちょっと重いからスキップさせる")
def test_01():
    print("1111111111111111111111")
    processingTime: float = 0
    for y in range(10):
        start = time.perf_counter()

        a = [x for x in range(100000)]

        for x in range(100):
            [x for x in a if x == random.randrange(100000)]

        end = time.perf_counter()
        processingTime += end - start

    print(processingTime / 10)


@pytest.mark.skipif(skip, reason="ちょっと重いからスキップさせる")
def test_02():
    print("22222222222222222222222")
    processingTime: float = 0
    for y in range(10):
        start = time.perf_counter()

        a = [x for x in range(100000)]
        b: Dict[int, int] = {x: x for x in a}

        for x in range(100):
            b.get(random.randrange(100000))

        end = time.perf_counter()
        processingTime += end - start

    print(processingTime / 10)

import datetime

class User:
    def __init__(self, user_id, email = None, name = None, birthday=None):
        self.id = id
        self.email = email
        self.name = name
        self.birthday = birthday

    user_id: str
    email: str
    name: str
    birthday: datetime

@pytest.mark.skipif(False, reason="ちょっと重いからスキップさせる")
def test_03():
    print("333333333")
    processingTime: float = 0
    for y in range(10):
        start = time.perf_counter()

        a = [User(user_id=str(x)) for x in range(100000)]

        for x in range(100):
            [x for x in a if x.id == random.randrange(100000)]

        end = time.perf_counter()
        processingTime += end - start

    print(processingTime / 10)


@pytest.mark.skipif(False, reason="ちょっと重いからスキップさせる")
def test_04():
    print("4444444444")
    processingTime: float = 0
    for y in range(10):
        start = time.perf_counter()

        a = [User(user_id=str(x)) for x in range(100000)]
        b: Dict[int, int] = {x.id: x for x in a}

        for x in range(100):
            b.get(random.randrange(100000))

        end = time.perf_counter()
        processingTime += end - start

    print(processingTime / 10)
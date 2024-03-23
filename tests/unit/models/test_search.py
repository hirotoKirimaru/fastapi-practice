import datetime
import random
import time
from typing import Dict

import pytest

skip: bool = True

# 10回やった平均を取る

number_of_trials = 10
max = 100000
search_times = 100


@pytest.mark.skipif(skip, reason="ちょっと重いからスキップさせる")
def test_01():
    print("1111111111111111111111")
    processingTime: float = 0
    for y in range(number_of_trials):
        start = time.perf_counter()

        a = [x for x in range(max)]

        for x in range(search_times):
            [x for x in a if x == random.randrange(max)]

        end = time.perf_counter()
        processingTime += end - start

    print(processingTime / 10)


@pytest.mark.skipif(skip, reason="ちょっと重いからスキップさせる")
def test_02():
    print("22222222222222222222222")
    processingTime: float = 0
    for y in range(number_of_trials):
        start = time.perf_counter()

        a = [x for x in range(max)]
        b: Dict[int, int] = {x: x for x in a}

        for x in range(search_times):
            b.get(random.randrange(max))

        end = time.perf_counter()
        processingTime += end - start

    print(processingTime / 10)


class User:
    def __init__(self, user_id, email=None, name=None, birthday=None):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.birthday = birthday

    user_id: str
    email: str
    name: str
    birthday: datetime


@pytest.mark.skipif(skip, reason="ちょっと重いからスキップさせる")
def test_03():
    print("333333333")
    processingTime: float = 0
    for y in range(number_of_trials):
        start = time.perf_counter()

        a = [User(user_id=str(x)) for x in range(max)]

        for x in range(search_times):
            [x for x in a if x.user_id == str(random.randrange(max))]

        end = time.perf_counter()
        processingTime += end - start

    print(processingTime / number_of_trials)


@pytest.mark.skipif(skip, reason="ちょっと重いからスキップさせる")
def test_04():
    print("4444444444")
    processingTime: float = 0
    for y in range(number_of_trials):
        start = time.perf_counter()

        a = [User(user_id=str(x)) for x in range(max)]
        b: Dict[str, User] = {x.user_id: x for x in a}

        for x in range(search_times):
            b.get(str(random.randrange(max)), User(user_id="XXXX"))

        end = time.perf_counter()
        processingTime += end - start

    print(processingTime / number_of_trials)

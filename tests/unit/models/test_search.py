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

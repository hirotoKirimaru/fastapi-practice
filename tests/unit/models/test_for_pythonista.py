from typing import Final
import time


class TestForPythonista:
    """
    FORよりもリスト内包表記(List Compression)の方が早いことを示すだけのテスト

    """
    # NUM: Final[int] = 100_000_000
    NUM: Final[int] = 1

    def test_for(self):
        start = time.perf_counter_ns()

        result = []
        for x in range(self.NUM):
            result.append(x)

        end = time.perf_counter_ns()
        total_processing_time = end - start
        average_processing_time = total_processing_time / self.NUM
        print("for")
        print(f"処理ナノ時間:{total_processing_time}, 平均処理ナノ時間:{average_processing_time}")

    def test_list_compression(self):
        start = time.perf_counter_ns()

        _ = [x for x in range(self.NUM)]

        end = time.perf_counter_ns()
        total_processing_time = end - start
        average_processing_time = total_processing_time / self.NUM
        print("list compression")
        print(f"処理ナノ時間:{total_processing_time}, 平均処理ナノ時間:{average_processing_time}")

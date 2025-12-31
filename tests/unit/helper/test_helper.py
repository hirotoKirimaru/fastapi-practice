import asyncio
import time
from unittest.mock import patch

import pytest

from src.helper.helper import timeit


class TestTimeitContextManager:
    """timeitコンテキストマネージャーのテストクラス"""

    @pytest.fixture
    def mock_logger(self):
        """ログ出力をモックするフィクスチャ"""
        with patch("src.helper.helper.logger") as mock_log:
            yield mock_log

    async def test_timeit_normal_execution(self, mock_logger):
        """正常実行時のテスト"""
        operation_name = "テスト処理"

        async with timeit(operation_name):
            await asyncio.sleep(0.1)  # 0.1秒待機

        # ログが2回呼ばれることを確認（開始と終了）
        assert mock_logger.info.call_count == 2

        # 開始ログの確認
        start_call = mock_logger.info.call_args_list[0]
        assert f"[{operation_name}] 処理開始" in str(start_call)

        # 終了ログの確認
        end_call = mock_logger.info.call_args_list[1]
        end_log_msg = str(end_call)
        assert f"[{operation_name}] 処理完了" in end_log_msg
        assert "実行時間:" in end_log_msg
        assert "秒" in end_log_msg

    async def test_timeit_with_exception(self, mock_logger):
        """例外発生時のテスト"""
        operation_name = "エラー処理"

        with pytest.raises(ValueError, match="テストエラー"):
            async with timeit(operation_name):
                await asyncio.sleep(0.05)
                raise ValueError("テストエラー")

        # 例外が発生してもログは2回呼ばれる
        assert mock_logger.info.call_count == 2

        # 開始ログの確認
        start_call = mock_logger.info.call_args_list[0]
        assert f"[{operation_name}] 処理開始" in str(start_call)

        # 終了ログも出力される（finallyブロックで実行）
        end_call = mock_logger.info.call_args_list[1]
        assert f"[{operation_name}] 処理完了" in str(end_call)

    async def test_timeit_default_operation_name(self, mock_logger):
        """デフォルトの操作名のテスト"""
        async with timeit():
            await asyncio.sleep(0.01)

        # デフォルト名「Operation」が使用される
        start_call = mock_logger.info.call_args_list[0]
        assert "[Operation] 処理開始" in str(start_call)

        end_call = mock_logger.info.call_args_list[1]
        assert "[Operation] 処理完了" in str(end_call)

    async def test_timeit_execution_time_accuracy(self, mock_logger):
        """実行時間の精度テスト"""
        sleep_duration = 0.2

        start_time = time.time()
        async with timeit("精度テスト"):
            await asyncio.sleep(sleep_duration)
        actual_duration = time.time() - start_time

        # 終了ログから実行時間を抽出
        end_call = mock_logger.info.call_args_list[1]
        end_log_msg = str(end_call)

        # ログメッセージから実行時間を抽出（正規表現使用）
        import re

        time_match = re.search(r"実行時間: (\d+\.\d+)秒", end_log_msg)
        assert time_match is not None

        logged_duration = float(time_match.group(1))

        # 実際の実行時間とログに記録された時間の差が小さいことを確認
        # 0.05秒の誤差を許容（システムの処理時間を考慮）
        assert abs(logged_duration - sleep_duration) < 0.05
        assert abs(logged_duration - actual_duration) < 0.05

    async def test_timeit_nested_context(self, mock_logger):
        """ネストしたコンテキストのテスト"""
        async with timeit("外側"):
            await asyncio.sleep(0.05)
            async with timeit("内側"):
                await asyncio.sleep(0.05)

        # 4回のログ呼び出し（外側開始、内側開始、内側終了、外側終了）
        assert mock_logger.info.call_count == 4

        calls = [str(call) for call in mock_logger.info.call_args_list]
        assert "[外側] 処理開始" in calls[0]
        assert "[内側] 処理開始" in calls[1]
        assert "[内側] 処理完了" in calls[2]
        assert "[外側] 処理完了" in calls[3]

    async def test_timeit_concurrent_execution(self, mock_logger):
        """並行実行のテスト"""

        async def task(name: str, duration: float):
            async with timeit(f"タスク{name}"):
                await asyncio.sleep(duration)

        # 3つのタスクを並行実行
        await asyncio.gather(task("A", 0.1), task("B", 0.15), task("C", 0.05))

        # 6回のログ呼び出し（3タスク × 2回ずつ）
        assert mock_logger.info.call_count == 6

        calls = [str(call) for call in mock_logger.info.call_args_list]

        # すべてのタスクの開始と終了ログが出力されることを確認
        start_logs = [call for call in calls if "処理開始" in call]
        end_logs = [call for call in calls if "処理完了" in call]

        assert len(start_logs) == 3
        assert len(end_logs) == 3

        # 各タスクのログが含まれていることを確認
        all_logs = " ".join(calls)
        assert "タスクA" in all_logs
        assert "タスクB" in all_logs
        assert "タスクC" in all_logs

    async def test_timeit_with_custom_exception(self, mock_logger):
        """カスタム例外での例外伝播テスト"""

        class CustomError(Exception):
            pass

        with pytest.raises(CustomError, match="カスタムエラー"):
            async with timeit("カスタムエラーテスト"):
                raise CustomError("カスタムエラー")

        # 例外が発生してもログは出力される
        assert mock_logger.info.call_count == 2

    async def test_timeit_zero_duration(self, mock_logger):
        """極短時間実行のテスト"""
        async with timeit("瞬時実行"):
            pass  # 何もしない

        assert mock_logger.info.call_count == 2

        # 終了ログに実行時間が含まれている
        end_call = mock_logger.info.call_args_list[1]
        end_log_msg = str(end_call)
        assert "実行時間:" in end_log_msg
        assert "秒" in end_log_msg

    async def test_decolator(self, mock_logger):
        @timeit("TEST DECOLATOR")
        async def test_func():
            await asyncio.sleep(0.1)

        @timeit("TEST DECOLATOR2")
        async def test_func2():
            await asyncio.sleep(0.1)

        # WHEN
        await test_func()
        await test_func2()
        # THEN
        assert mock_logger.info.call_count == 4

        # 終了ログに実行時間が含まれている
        end_call = mock_logger.info.call_args_list[1]
        end_log_msg = str(end_call)
        assert "実行時間:" in end_log_msg
        assert "秒" in end_log_msg


# パフォーマンステスト用のクラス
class TestTimeitPerformance:
    """timeitのパフォーマンステスト"""

    @pytest.mark.skip
    async def test_timeit_overhead(self):
        """timeitコンテキストマネージャーのオーバーヘッドテスト"""
        # timeitなしでの実行時間
        start = time.time()
        await asyncio.sleep(0.1)
        without_timeit = time.time() - start

        # timeitありでの実行時間
        with patch("src.helper.helper.logger"):  # ログ出力を無効化
            start = time.time()
            async with timeit("オーバーヘッドテスト"):
                await asyncio.sleep(0.1)
            with_timeit = time.time() - start

        # オーバーヘッドが極小であることを確認（1ms以下）
        overhead = with_timeit - without_timeit
        assert overhead < 0.001  # 1ms未満

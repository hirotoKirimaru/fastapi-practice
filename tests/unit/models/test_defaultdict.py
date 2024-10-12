from collections import defaultdict
import sys

from operator import attrgetter
from itertools import groupby


import pytest

class TestDefaultDict:
    def test_defaultdict_basic(self):
        d1 = defaultdict(int)
        assert d1['新しいキー'] == 0
        d1['apple'] += 1
        d1['banana'] += 2
        assert dict(d1) == {'新しいキー': 0, 'apple': 1, 'banana': 2}

    def test_defaultdict_list(self):
        d2 = defaultdict(list)
        d2['fruits'].append('apple')
        d2['fruits'].append('banana')
        d2['vegetables'].append('carrot')
        assert dict(d2) == {'fruits': ['apple', 'banana'], 'vegetables': ['carrot']}

    def test_defaultdict_custom_function(self):
        def default_value():
            return "未知の項目"
        d3 = defaultdict(default_value)
        assert d3['存在しないキー'] == "未知の項目"

    def test_defaultdict_lambda(self):
        d4 = defaultdict(lambda: sys.maxsize)
        assert d4['任意のキー'] == sys.maxsize

    def test_nested_defaultdict(self):
        d5 = defaultdict(lambda: defaultdict(int))
        d5['外部キー1']['内部キー1'] += 1
        d5['外部キー1']['内部キー2'] += 2
        d5['外部キー2']['内部キー1'] += 3
        assert dict(d5) == {'外部キー1': {'内部キー1': 1, '内部キー2': 2}, '外部キー2': {'内部キー1': 3}}

    def test_defaultdict_vs_dict(self):
        normal_dict = {}
        with pytest.raises(KeyError):
            normal_dict['存在しないキー'] += 1

        d6 = defaultdict(int)
        d6['存在しないキー'] += 1
        assert dict(d6) == {'存在しないキー': 1}

    def test_defaultdict_type_conversion(self):
        d7 = defaultdict(int, {'a': 1, 'b': 2})
        assert dict(d7) == {'a': 1, 'b': 2}
        assert list(d7.keys()) == ['a', 'b']
        assert list(d7.values()) == [1, 2]

    def test_defaultdict_memory_usage(self):
        d8 = defaultdict(int)
        initial_size = sys.getsizeof(d8)
        for i in range(1000):
            d8[f'key_{i}'] = i
        final_size = sys.getsizeof(d8)
        assert final_size > initial_size



class TestGroupBy:
    class _Test:
        def __init__(self, user_id, group_id):
            self.user_id = user_id
            self.group_id = group_id

    @pytest.fixture
    def parameters(self):
        return [
            self._Test(1, 'A'),
            self._Test(2, 'A'),
            self._Test(3, 'B'),
            self._Test(4, 'A'),
            self._Test(5, 'B'),
        ]

    class TestDefaultDict:
        def test_group_by(self, parameters):
            grouped_data = defaultdict(list)
            for user in parameters:
                grouped_data[user.group_id].append(user.user_id)
            expected = {'A': [1, 2, 4], 'B': [3, 5]}
            assert dict(grouped_data) == expected

    class TestItertools:
        def test_group_by(self, parameters):
            # NOTE: ソートがかかっていないと正しくgroup_byされない
            non_continuous_data = {k: [user.user_id for user in v] for k, v in groupby(parameters, key=attrgetter('group_id'))}
            expected = {'A': [4], 'B': [5]}
            assert non_continuous_data == expected

            sorted_users = sorted(parameters, key=attrgetter('group_id'))

            grouped_data = {k: [user.user_id for user in v] for k, v in groupby(sorted_users, key=attrgetter('group_id'))}
            expected = {'A': [1, 2, 4], 'B': [3, 5]}
            assert grouped_data == expected


# defaultdictとitertools.groupbyの比較
# シンプルさ:
# defaultdictの実装はより直感的で理解しやすいです。
# itertools.groupbyの実装は、ソートと複雑なリスト内包表記を使用しています。
# パフォーマンス:
# defaultdictの実装は、データを1回だけ走査するため、一般的に高速です。
# itertools.groupbyの実装は、事前にデータをソートする必要があるため、大規模なデータセットでは遅くなる可能性があります。
# メモリ使用:
# defaultdictは全てのデータをメモリに保持します。
# itertools.groupbyはイテレータベースで動作するため、理論的にはメモリ効率が良いですが、この実装では結果を辞書に格納しているため、実質的な違いはありません。
# 順序の保持:
# defaultdictは元のデータの順序を保持しません。
# itertools.groupbyは、ソートされたデータの順序を保持します。
# 柔軟性:
# defaultdictの実装は、グループ化のキーを動的に変更するのが容易です。
# itertools.groupbyの実装は、キーを変更する場合、ソート関数も変更する必要があります。
# 連続したグループ化:
# defaultdictは非連続なグループでも問題なく動作します。
# itertools.groupbyは連続したグループにのみ効果的で、非連続なグループには適していません。
# 結論として、シンプルさと柔軟性を重視する場合はdefaultdictを、データが既にソートされている場合や厳密な順序が必要な場合はitertools.groupbyを選択するのが良いでしょう。多くの一般的なユースケースでは、defaultdictの実装が適していると言えます。
#
# def test_defaultdict():
#     print("## defaultdictの基本的な使用法")
#
#     # int型のデフォルト値を持つdefaultdict
#     d1 = defaultdict(int)
#     print(f"1. 存在しないキーへのアクセス: {d1['新しいキー']}")
#     d1['apple'] += 1
#     d1['banana'] += 2
#     print(f"2. 要素の追加後: {dict(d1)}")
#
#     print("\n## list型のデフォルト値")
#     d2 = defaultdict(list)
#     d2['fruits'].append('apple')
#     d2['fruits'].append('banana')
#     d2['vegetables'].append('carrot')
#     print(f"3. リストを値として持つdefaultdict: {dict(d2)}")
#
#     print("\n## カスタム関数をデフォルト値として使用")
#     def default_value():
#         return "未知の項目"
#     d3 = defaultdict(default_value)
#     print(f"4. カスタム関数の結果: {d3['存在しないキー']}")
#
#     print("\n## lambda関数をデフォルト値として使用")
#     d4 = defaultdict(lambda: sys.maxsize)
#     print(f"5. システムの最大整数値: {d4['任意のキー']}")
#
#     print("\n## ネストされたdefaultdict")
#     d5 = defaultdict(lambda: defaultdict(int))
#     d5['外部キー1']['内部キー1'] += 1
#     d5['外部キー1']['内部キー2'] += 2
#     d5['外部キー2']['内部キー1'] += 3
#     print(f"6. ネストされたdefaultdict: {dict(d5)}")
#
#     print("\n## defaultdictとdict型の比較")
#     normal_dict = {}
#     try:
#         normal_dict['存在しないキー'] += 1
#     except KeyError:
#         print("7. 通常のdictでは存在しないキーにアクセスするとKeyErrorが発生")
#
#     d6 = defaultdict(int)
#     d6['存在しないキー'] += 1
#     print(f"8. defaultdictでは問題なく動作: {dict(d6)}")
#
#     print("\n## defaultdictの型変換")
#     d7 = defaultdict(int, {'a': 1, 'b': 2})
#     print(f"9. defaultdictからdictへの変換: {dict(d7)}")
#     print(f"10. defaultdictのキーのリスト: {list(d7.keys())}")
#     print(f"11. defaultdictの値のリスト: {list(d7.values())}")
#
#     print("\n## defaultdictのメモリ使用")
#     d8 = defaultdict(int)
#     print(f"12. 空のdefaultdictのサイズ: {sys.getsizeof(d8)} バイト")
#     for i in range(1000):
#         d8[f'key_{i}'] = i
#     print(f"13. 1000要素追加後のサイズ: {sys.getsizeof(d8)} バイト")
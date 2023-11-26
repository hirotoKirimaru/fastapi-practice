from enum import Enum

class CsvHeaderColumn(int, Enum):
    """
    intを継承しているとvalueにアクセスしなくてもアクセスできる

    """
    ID = 1
    NAME = 2
    EMAIL = 3
    ADMIN_FLG = 4

def add(num1: int, num2: CsvHeaderColumn):
    return num1 + num2

class Test:
    def test_normal(self):
        # 正しくはこちらのアクセス
        assert CsvHeaderColumn.ID.value == 1

        assert CsvHeaderColumn.ID == 1
        assert CsvHeaderColumn.NAME == 2
        assert CsvHeaderColumn.EMAIL == 3
        assert CsvHeaderColumn.ADMIN_FLG == 4
        assert len(CsvHeaderColumn) == 4, f"定義している数({4})が一致していること"

    def test_add(self):
        assert add(1, CsvHeaderColumn.ID) == 2



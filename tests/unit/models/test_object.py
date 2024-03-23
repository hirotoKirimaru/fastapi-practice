class Hoge:
    def __init__(self, name: str):
        super().__init__()
        self.name = name


class Fuga(object):
    def __init__(self, name: str):
        super().__init__()
        self.name = name


class TestHogeFuga:
    async def test_01(self):
        hoge = Hoge(name="aiueo")
        assert hoge.name == "aiueo"
        assert type(hoge) is Hoge
        assert issubclass(Hoge, object)

        fuga = Fuga(name="aiueo")
        assert fuga.name == "aiueo"
        assert type(fuga) is Fuga
        assert issubclass(Fuga, object)

        assert type(hoge) is not type(fuga)

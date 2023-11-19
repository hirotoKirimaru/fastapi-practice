class TestDefaultParameter:
    def target_1(self, value, list=[]):
        list.append(value)
        return list

    def test_01(self):
        """
        デフォルト引数をミュータブルにするとダメ.

        https://docs.python.org/ja/3/reference/compound_stmts.html#grammar-token-python-grammar-parameter:~:text=%E3%83%86%E3%82%99%E3%83%95%E3%82%A9%E3%83%AB%E3%83%88%E5%BC%95%E6%95%B0%E3%81%AE%E5%BC%8F%E3%81%AF%E9%96%A2%E6%95%B0%E3%81%8B%E3%82%99%E5%AE%9A%E7%BE%A9%E3%81%95%E3%82%8C%E3%82%8B%E3%81%A8%E3%81%8D%E3%81%AB%E3%81%9F%E3%81%9F%E3%82%99%E4%B8%80%E5%BA%A6%E3%81%9F%E3%82%99%E3%81%91%E8%A9%95%E4%BE%A1%E3%81%95%E3%82%8C%E3%80%81%E5%90%8C%E3%81%97%E3%82%99%20%22%E8%A8%88%E7%AE%97%E6%B8%88%E3%81%BF%E3%81%AE%22%20%E5%80%A4%E3%81%8B%E3%82%99%E5%91%BC%E3%81%B2%E3%82%99%E5%87%BA%E3%81%97%E3%81%AE%E3%81%9F%E3%81%B2%E3%82%99%E3%81%AB%E4%BD%BF%E7%94%A8%E3%81%95%E3%82%8C%E3%82%8B%E3%81%93%E3%81%A8%E3%82%92%E6%84%8F%E5%91%B3%E3%81%97%E3%81%BE%E3%81%99%E3%80%82
        """
        a = self.target_1("1")
        assert len(a) == 1
        b = self.target_1("2")
        # print(a)
        # print(b)
        assert len(a) == 2
        assert len(b) == 2
        assert a is b

    def target_2(self, value, list=None):
        if list is None:
            list = []
        # list = list or []
        list.append(value)
        return list

    def test_02(self):
        a = self.target_2("1")
        assert len(a) == 1
        b = self.target_2("2")
        # print(a)
        # print(b)
        assert len(a) == 1
        assert len(b) == 1

    # def target_2(self, value, tax=10):
    #     return value + value * (tax / 100)

    # def test_02(self):
    #     a = self.target_2(100);
    #     assert a == 110
    #     b = self.target_2(200);
    #     # print(a)
    #     # print(b)
    #     assert a == 110
    #     assert b == 220

    # def target_3(self, value, author="きり丸"):
    #     return f{""}

    # def test_03(self):
    #     a = self.target_2(1);
    #     assert 1 == 1
    #     b = self.target_2(2);
    #     # print(a)
    #     # print(b)
    #     assert a == 1
    #     assert b == 2
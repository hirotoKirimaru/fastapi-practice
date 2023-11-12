class TestDefaultParameter:
    def target_1(self, value, list=[]):
        list.append(value)
        return list

    def test_01(self):
        a = self.target_1("1");
        assert len(a) == 1
        b = self.target_1("2");
        # print(a)
        # print(b)
        assert len(a) == 2
        assert len(b) == 2

    def target_2(self, value, list=None):
        if list is None:
            list = []
        # list = list or []
        list.append(value)
        return list

    def test_02(self):
        a = self.target_2("1");
        assert len(a) == 1
        b = self.target_2("2");
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
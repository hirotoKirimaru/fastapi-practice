class CustomAssert:
    @staticmethod
    def shallow_equal(
        actual, expected, ignore_column_list=["id", "created_at", "updated_at"]
    ) -> None:
        """
        DBの値を比較するための項目。
        NOTE: _sa_instance_stateに関しては、主キーが一致していれば一致するようだが、DBと比較する前のインスタンスだと設定できないので、無視するようにする

        :param actual: 実際の値
        :param expected: 期待値
        :param ignore_column_list: 項目を無視するリスト
        """
        for key, value in actual.__dict__.items():
            # 自作型は無視するようにする
            if is_primitive(value):
                continue
            # いい感じに無視したい
            if ignore_column_list.__contains__(key):
                continue

            # TODO: エラーメッセージがあんまり綺麗ではないので、いい感じに出力できるようにしたい。
            assert (
                value == expected.__dict__[key]
            ), f"""
            比較に失敗しました。
            assertError: 項目名：{key} actual: {value} expected: {expected.__dict__[key]} 
            インスタンスの比較： 
            actual: 
            {actual.__dict__} 
            expected: 
            {expected.__dict__}
            """

    @staticmethod
    def deep_equal(
        actual, expected, ignore_column_list=["id", "created_at", "updated_at"]
    ) -> None:
        """
        DBの値を比較するための項目。
        NOTE: _sa_instance_stateに関しては、主キーが一致していれば一致するようだが、DBと比較する前のインスタンスだと設定できないので、無視するようにする

        :param actual: 実際の値
        :param expected: 期待値
        :param ignore_column_list: 項目を無視するリスト
        :return:
        """
        for key, value in actual.__dict__.items():
            # 自作型も全部比較する
            # いい感じに無視したい
            if ignore_column_list.__contains__(key):
                continue

            # TODO: エラーメッセージがあんまり綺麗ではないので、いい感じに出力できるようにしたい。
            assert (
                value == expected.__dict__[key]
            ), f"""
            比較に失敗しました。
            assertError: 項目名：{key} actual: {value} expected: {expected.__dict__[key]} 
            インスタンスの比較： 
            actual: 
            {actual.__dict__} 
            expected: 
            {expected.__dict__}
            """


def is_primitive(object) -> bool:
    """
    Primitive-obsessionの確認？
    """
    return "." in str(type(object))

from io import StringIO
from typing import Any

import polars


class Csvs:
    @classmethod
    def create_row_data(cls, *, data: list[Any], first: bool = False) -> bytes:
        encoding = "utf_8"
        if first:
            encoding = "utf_8_sig"

        df = polars.DataFrame(data)
        stream = StringIO()
        _ = df.to_csv(stream, index=False, header=False, encoding=encoding)

        return stream.getvalue().encode(encoding)

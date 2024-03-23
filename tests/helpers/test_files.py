import tempfile
from io import StringIO
from typing import AsyncGenerator

import polars


class TestFiles:
    @classmethod
    async def create_file(cls, csv_data: str) -> AsyncGenerator:
        datafile = StringIO(csv_data)
        df = polars.read_csv(datafile, skipinitialspace=True, dtype=str)
        with tempfile.NamedTemporaryFile() as tmp:
            df.to_csv(tmp.name, index=False)
            with open(tmp.name, "rb") as file:
                yield file

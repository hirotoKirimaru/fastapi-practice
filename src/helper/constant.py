import os
from typing import Literal


class Constant:
    ENV: Literal["local", "prod"] = os.environ["ENV"]  # type: ignore

from datetime import datetime

import jwt
from pydantic import BaseModel


class JwtToken(BaseModel):
    id: int
    exp: int | datetime
    iss: str


async def test_expected_same_token():
    KEY = "SECRET"
    ALGORITHM = "HS256"
    json_token = {"id": 1, "exp": 9999999999, "iss": "kirimaru"}

    pydantic_token = JwtToken(**json_token).model_dump()

    # NOTE: JSON のキーの順番が違ってもTrue になる
    assert json_token == pydantic_token

    # NOTE: JWTの payload の順番が違ったら別のトークンになるのでソートしたら True になる
    json_encode = jwt.encode(dict(sorted(json_token.items())), KEY, algorithm=ALGORITHM)
    pydantic_encode = jwt.encode(
        dict(sorted(pydantic_token.items())), KEY, algorithm=ALGORITHM
    )
    assert json_encode == pydantic_encode

    # NOTE: ソートしなくても別のトークンから同じJSONに戻せることのチェック
    json_encode = jwt.encode(json_token, KEY, algorithm=ALGORITHM)
    pydantic_encode = jwt.encode(pydantic_token, KEY, algorithm=ALGORITHM)
    json_decode = jwt.decode(json_encode, KEY, algorithms=ALGORITHM)
    pydantic_decode = jwt.decode(pydantic_encode, KEY, algorithms=ALGORITHM)

    assert json_decode == pydantic_decode

import os
import socket
import tempfile
import uuid
from io import StringIO

import polars
import pytest

from src.helper.aws import Aws

# compose の storage (adobe/s3mock) に作られるバケット
# （COM_ADOBE_TESTING_S3MOCK_STORE_INITIAL_BUCKETS で起動時に作られる）
BUCKET = "tmp.local"


def _storage_reachable() -> bool:
    """アプリが見ている S3 のエンドポイントに TCP で届くかどうか。

    compose を起動していないローカルでは届かないので、その場合は skip する。
    api コンテナ内（CI もここ）では relay (socat) が localhost:9000 で受けて
    S3Mock の 9090 へ渡すので届く。
    """
    host, _, port = os.getenv("S3_URL", "localhost:9000").partition(":")
    try:
        with socket.create_connection((host, int(port or "80")), timeout=1):
            return True
    except (OSError, ValueError):
        return False


# 以前は testcontainers の MinioContainer で MinIO を起動していたが、
#   1. MinIO の公開イメージが Docker Hub と quay.io の両方から無くなり、
#      MinioContainer が引けるイメージが存在しなくなった
#   2. そもそも CI では pytest を api コンテナ内で実行しており、docker socket を
#      渡していないので testcontainers は動かせない（これが元の skip 理由）
# という2つの理由で成立しなくなった。compose で既に立っている storage を使う形に
# 変え、CI でも実際に走るようにしている。
class TestAws:
    @pytest.mark.skipif(
        not _storage_reachable(),
        reason="S3 のエンドポイントに届かない（docker compose up を実行していない）",
    )
    async def test_01(self) -> None:
        csv_data = """
        氏名,メールアドレス
        ユーザ1,test1@example.com
        ユーザ2,test2@example.com
        """
        key = f"test-aws-{uuid.uuid4().hex}"

        await TestAwsHelper.upload_s3(csv_data=csv_data, bucket=BUCKET, key=key)

        # 読み出しもアプリ自身のクライアントで行う。boto3 の設定（endpoint_url や
        # addressing style）が S3Mock と噛み合っているかまで含めて確認したいため
        client = Aws.Storage.s3_client()
        stored = client.get_object(Bucket=BUCKET, Key=key)["Body"].read()

        stored_csv = polars.read_csv(StringIO(stored.decode("utf-8")))
        original_csv = polars.read_csv(StringIO(csv_data))

        assert stored_csv.equals(original_csv)


class TestAwsHelper:
    @classmethod
    async def upload_s3(cls, csv_data: str, bucket: str, key: str) -> None:
        datafile = StringIO(csv_data)
        df = polars.read_csv(datafile, encoding="utf-8")
        with tempfile.NamedTemporaryFile() as tmp:
            df.write_csv(tmp.name)
            with open(tmp.name, "rb") as file:
                await Aws.Storage.file_upload(file=file, bucket=bucket, key=key)

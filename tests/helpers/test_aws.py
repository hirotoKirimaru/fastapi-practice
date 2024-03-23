import os
import tempfile
from datetime import datetime
from io import StringIO

import polars
from testcontainers.minio import MinioContainer

from src.helper.aws import Aws


class TestAws:
    async def test_01(self):
        # https://github.com/testcontainers/testcontainers-python/blob/c9c6f92348299a2cc04988af8d69a53a23a7c7d5/modules/minio/testcontainers/minio/__init__.py#L45
        #         image: str = "minio/minio:RELEASE.2022-12-02T19-19-22Z",
        # なぜか、変に古いバージョンで固定されている
        config = MinioContainer(
            access_key="minio", secret_key="minio1234", image="minio/minio"
        )
        # for _ in create_minio_container():
        with config as minio:
            minio_client = minio.get_client()
            minio_client.make_bucket("tmp.local")
            # 接続情報の上書き
            os.environ["S3_URL"] = minio.get_config()["endpoint"]

            csv_data = """
            氏名,メールアドレス
            ユーザ1,test1@example.com
            ユーザ2,test2@example.com
            """
            # bucket = os.getenv("S3_BUCKET")
            bucket = "tmp.local"
            key = datetime.now().strftime("%Y%m%d%H%M%S")
            await TestAwsHelper.upload_s3(csv_data=csv_data, bucket=bucket, key=key)

            minio_data = minio_client.get_object(bucket, key).data

            minio_csv = polars.read_csv(StringIO(minio_data.decode("utf-8")))
            original_csv = polars.read_csv(StringIO(csv_data))

            # csv_data2222 = """
            # 氏名,メールアドレス
            # ユーザ1,test1@example.com
            # """
            # original_csv2222 = polars.read_csv(StringIO(csv_data2222))
            # breakpoint()

            assert minio_csv.equals(original_csv)


class TestAwsHelper:
    @classmethod
    async def upload_s3(cls, csv_data: str, bucket: str, key: str) -> None:
        datafile = StringIO(csv_data)
        df = polars.read_csv(datafile, encoding="utf-8")
        with tempfile.NamedTemporaryFile() as tmp:
            df.write_csv(tmp.name)
            with open(tmp.name, "rb") as file:
                await Aws.Storage.file_upload(file=file, bucket=bucket, key=key)

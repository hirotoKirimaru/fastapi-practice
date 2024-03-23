import tempfile
from datetime import datetime
from io import StringIO

import polars

from src.helper.aws import Aws


class TestAws:
    async def test_01(self):
        csv_data = """
        氏名,メールアドレス
        ユーザ1,test1@example.com
        ユーザ2,test2@example.com
        """
        # bucket = os.getenv("S3_BUCKET")
        bucket = "tmp.local"
        key = datetime.now().strftime("%Y%m%d%H%M%S")
        await TestAwsHelper.upload_s3(csv_data=csv_data, bucket=bucket, key=key)


class TestAwsHelper:
    @classmethod
    async def upload_s3(cls, csv_data: str, bucket: str, key: str) -> None:
        datafile = StringIO(csv_data)
        df = polars.read_csv(datafile)
        with tempfile.NamedTemporaryFile() as tmp:
            df.write_csv(tmp.name)
            with open(tmp.name, "rb") as file:
                await Aws.Storage.file_upload(file=file, bucket=bucket, key=key)

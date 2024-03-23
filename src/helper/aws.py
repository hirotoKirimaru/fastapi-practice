from typing import Any

import boto3  # type: ignore


class Aws:
    class Storage:
        @classmethod
        def s3_client(cls):
            # breakpoint()
            # if os.getenv("ENV") == "local":
            return boto3.client(
                "s3",
                endpoint_url="http://localhost:9000",
                aws_access_key_id="minio",
                aws_secret_access_key="minio1234",
                # aws_access_key_id=os.getenv("AWS_S3_ACCESS_KEY"),
                # aws_secret_access_key=os.getenv("AWS_S3_SECRET_KEY")
            )
            # else:
            #     pass

        @classmethod
        # async def file_upload(cls, file: Any, bucket: str, key: str, client=Depends(s3_client)):
        async def file_upload(cls, file: Any, bucket: str, key: str):
            client = cls.s3_client()
            client.upload_fileobj(file, bucket, key)

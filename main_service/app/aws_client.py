import json
import boto3

from app.config import (
    AWS_REGION,
    LOCALSTACK_URL,
    AWS_SECRET_ACCESS_KEY,
    AWS_ACCESS_KEY_ID,
)


class AWSServiceClient:
    def __init__(
        self,
        region_name: str,
        endpoint_url: str,
        secret_access_key: str,
        access_key_id: str,
    ):
        """
        Initialize the S3 client.

        :param region_name: The AWS region where the SQS and SNS services are located.
        :param endpoint_url: The custom endpoint URL (e.g., for LocalStack).
        """
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self.secret_access_key = secret_access_key
        self.access_key_id = access_key_id
        self.queue_url: str | None = None
        self.sqs_client = None
        self.sns_client = None
        self.s3_client = None


    def connect_to_s3_client(self):
        """
        connects to the S3 client.
        """
        if not self.s3_client:
            self.s3_client = boto3.client(
                "s3",
                region_name=self.region_name,
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
            )

    def connect_to_clients(self):
        """
        connects to all clients.
        """
        self.connect_to_s3_client()

    def close_clients(self):
        # Boto3 doesn't provide a direct close method, but you can reset the clients if needed.
        self.s3_client = None


    def put_to_s3(self, data: list | dict, file_name: str, bucket_name: str):
        # Upload the report to S3
        self.s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=json.dumps(data),
            ContentType="application/json",
        )


aws_service_client = AWSServiceClient(
    region_name=AWS_REGION,
    endpoint_url=LOCALSTACK_URL,
    access_key_id=AWS_ACCESS_KEY_ID,
    secret_access_key=AWS_SECRET_ACCESS_KEY,
)

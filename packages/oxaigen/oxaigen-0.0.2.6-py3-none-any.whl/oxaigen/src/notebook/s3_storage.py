# -*- coding: utf-8 -*-
import boto3

from ..settings.settings import BaseSettingsInterface


class S3ClientStorage:
    def __init__(self, settings: BaseSettingsInterface) -> None:
        """
        Initializes the S3Storage class.

        Args:
            settings (BaseSettingsInterface): The settings instance containing AWS and S3 configurations.
        """
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.S3_ENDPOINT,
            region_name=settings.S3_REGION,
            use_ssl=settings.S3_SSL.lower() == 'true'
        )
        self.bucket_name = settings.CLIENT_BUCKET

    def save_file(
            self,
            file_path: str,
            s3_path: str
    ) -> None:
        """
        Saves a file to the S3 bucket.

        Args:
            file_path (str): The local path to the file.
            s3_path (str): The name to use for the file in the S3 bucket.
        """
        self.s3_client.upload_file(file_path, self.bucket_name, s3_path)

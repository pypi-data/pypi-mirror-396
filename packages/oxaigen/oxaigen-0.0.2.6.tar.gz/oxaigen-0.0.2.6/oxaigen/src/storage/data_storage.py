# -*- coding: utf-8 -*-
import boto3
import pickle
from s3transfer import S3Transfer
from typing import Optional, Any

from ..util.exception import OxaigenSDKException
from ..util.util import UploadProgressPercentageCallback
from ..config import (
    S3_REGION,
    S3_SSL,
    S3_ENDPOINT,
    S3_ACCESS_KEY_ID,
    S3_SECRET_ACCESS_KEY
)


class OxaigenDataStorage:
    """
    Oxaigen Asset class for interacting with the Oxaigen Orchestration data storage.
    """

    def __init__(
            self,
            endpoint_url: Optional[str] = None,
            access_key_id: Optional[str] = None,
            secret_access_key: Optional[str] = None,
            use_ssl: Optional[bool] = None,
            region_name: Optional[str] = None
    ):
        """
        Initializes the OxaigenDataStorage class.

        Args:
            endpoint_url (Optional[str]): The endpoint URL for the S3 service.
            access_key_id (Optional[str]): The access key ID for the S3 service.
            secret_access_key (Optional[str]): The secret access key for the S3 service.
            use_ssl (Optional[bool]): Whether to use SSL.
            region_name (Optional[str]): The region name for the S3 service.

        Defaults:
            Reads from CONFIG if parameters are not provided.
        """
        self._endpoint_url = endpoint_url or S3_ENDPOINT
        self._access_key_id = access_key_id or S3_ACCESS_KEY_ID
        self._secret_access_key = secret_access_key or S3_SECRET_ACCESS_KEY
        self._use_ssl = use_ssl if use_ssl is not None else S3_SSL
        self._region_name = region_name or S3_REGION

        try:
            self._s3_client = boto3.client(
                service_name='s3',
                endpoint_url=self._endpoint_url,
                aws_access_key_id=self._access_key_id,
                aws_secret_access_key=self._secret_access_key,
                use_ssl=self._use_ssl,
                region_name=self._region_name
            )
            self._transfer = S3Transfer(client=self._s3_client)
        except Exception:
            raise OxaigenSDKException(message="Could not initialise OxaigenDataStorage, invalid credentials")

    def upload_file(self, bucket: str, file: str, key: str) -> bool:
        """
        Uploads a file to the Oxaigen Orchestration data storage.

        Args:
            bucket (str): The local path of the file to upload.
            file (str): the file (path) to upload
            key (str): The S3 key where the file will be stored.

        Returns:
            bool: True if the upload was successful, False otherwise.
        """
        try:
            self._transfer.upload_file(
                filename=file,
                bucket=bucket,
                key=key,
                callback=UploadProgressPercentageCallback(file)
            )
            return True
        except Exception as e:
            print(f"Failed to upload file: {e}")
            return False

    def download_file(self, bucket: str, key: str, file: str) -> bool:
        """
        Downloads a file from the Oxaigen data storage to disk.

        Args:
            bucket (str): The local path of the file to upload.
            key (str): The S3 key to download
            file (str): the file (path) where the file will be stored.

        Returns:
            bool: True if the download was successful, False otherwise.
        """
        try:
            self._transfer.download_file(
                bucket=bucket,
                key=key,
                filename=file,
            )
            return True
        except Exception as e:
            print(f"Failed to download file: {e}")
            return False

    @staticmethod
    def open_file(file: str) -> Any:
        """
        Open a file from the Oxaigen Orchestration data storage into a Python object.

        Args:
            file (str): The name of the file to load.

        Returns:
            Any: The loaded Python object if the file is pickled, or the raw file content if not.

        Raises:
            OxaigenSDKException: If any error occurs during file loading.
        """
        try:
            with open(file, 'rb') as f:
                try:
                    return pickle.load(f)
                except (pickle.UnpicklingError, AttributeError):
                    f.seek(0)  # Reset the file pointer to the beginning
                    return f.read()
        except FileNotFoundError:
            raise OxaigenSDKException(message=f"File not found: {file}. Please check the file path and try again.")
        except IOError:
            raise OxaigenSDKException(message=f"IO error occurred while accessing the file: {file}")
        except Exception:
            raise OxaigenSDKException(message=f"An unexpected error occurred while loading the file: {file}.")

# -*- coding: utf-8 -*-
import os
import pickle
import shutil
import logging
import requests
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..util.api import run_api_query
from ..util.exception import OxaigenSDKException, OxaigenApiException
from ..config import USER_ROOT_DIR

S3_ASSET_DOWNLOAD_LINK = "getS3AssetDownloadLink"
FILE_NAME = "fileName"
FILE_SIZE = "fileSize"
FILE_TYPE = "fileType"
DOWNLOAD_URL = "downloadUrl"
LAST_MODIFIED = "lastModified"


class OxaigenAsset:
    """
    Oxaigen Asset class
    """

    def __init__(self):
        super().__init__()

    def get_asset(
            self,
            asset_key: List[str],
            file_path: Optional[List[str]] = None,
            run_id: Optional[str] = None,
            use_cache: bool = True
    ) -> Optional[Any]:
        """
        Download an Asset from the Oxaigen Orchestration data plane

        Args:
            asset_key (List[str]): The key identifying the asset.
            file_path (Optional[List[str]], optional): The path to save the downloaded asset. Defaults to None.
            run_id (Optional[str], optional): The ID of the run. Defaults to None.
            use_cache (bool, optional): Whether to use the cache. Defaults to True.

        Returns:
            Optional[Any]: The downloaded asset.
        """
        if use_cache:
            return self._get_asset_from_cache(asset_key=asset_key, file_path=file_path, run_id=run_id)
        else:
            return self.download_asset(asset_key=asset_key, file_path=file_path, run_id=run_id)

    def _get_asset_from_cache(
            self,
            asset_key: List[str],
            file_path: Optional[List[str]],
            run_id: Optional[str] = None
    ) -> Optional[Any]:
        """
        Function to get an Asset from the DataPlane from cache (local file storage)

        Args:
            asset_key (List[str]): The key identifying the asset.
            file_path (Optional[List[str]]): The path to save the downloaded asset.
            run_id (Optional[str], optional): The ID of the run. Defaults to None.

        Returns:
            Optional[Any]: The downloaded asset.
        """
        if not file_path:
            file_path = asset_key

        data = self._get_download_asset_link(asset_key=asset_key, run_id=run_id)
        file_name = data[S3_ASSET_DOWNLOAD_LINK][FILE_NAME]
        clean_file_name = os.path.basename(file_name)
        full_path = os.path.join(USER_ROOT_DIR, *file_path)
        file = os.path.join(full_path, clean_file_name)

        asset = self.get_asset_from_file(file=file)

        # fallback to fresh download
        if asset is None:
            return self.download_asset(asset_key=asset_key, file_path=file_path, run_id=run_id)

        return asset

    def download_asset(
            self,
            asset_key: List[str],
            file_path: Optional[List[str]] = None,
            run_id: Optional[str] = None
    ) -> Optional[Any]:
        """
        Download an Asset from the Oxaigen Orchestration data plane

        Args:
            asset_key (List[str]): The key identifying the asset.
            file_path (Optional[List[str]], optional): The path to save the downloaded asset. Defaults to None.
            run_id (Optional[str], optional): The ID of the run. Defaults to None.

        Returns:
            Optional[Any]: The downloaded asset.
        """
        if not file_path:
            file_path = asset_key
        try:
            data = self._get_download_asset_link(asset_key=asset_key, run_id=run_id)

            # Check if the asset was not found
            if 'getS3AssetDownloadLink' in data and data['getS3AssetDownloadLink']['__typename'] == 'AssetNotFound':
                error_message = data['getS3AssetDownloadLink']['errorMessage']
                raise OxaigenSDKException(message=f"Asset not found: {error_message}")

            # Check if there's an error message
            if 'errorMessage' in data:
                error_message = data['errorMessage']
                raise OxaigenSDKException(message=f"Error occurred: {error_message}")

            url = data[S3_ASSET_DOWNLOAD_LINK][DOWNLOAD_URL]
            file_name = data[S3_ASSET_DOWNLOAD_LINK][FILE_NAME]
            file_size = data[S3_ASSET_DOWNLOAD_LINK][FILE_SIZE]
            clean_file_name = os.path.basename(file_name)

            logging.info(msg=f"Downloading file {clean_file_name} ({file_size}) into this directory: {file_path}")
            self._download_asset_file(url=url, file_path=file_path, file_name=clean_file_name)

            full_path = os.path.join(USER_ROOT_DIR, *file_path)
            file = os.path.join(full_path, clean_file_name)

            asset = self.get_asset_from_file(file=file)
            if asset is None:
                raise OxaigenSDKException(message=f"Could not open downloaded asset, try again")

            return asset

        except (OxaigenSDKException, OxaigenApiException):
            # Rethrow the exception
            raise

        except Exception as e:
            # Catch all other exceptions
            raise OxaigenSDKException(message=f"Could not download asset, Error: {str(e)}")

    @staticmethod
    def _get_download_asset_link(
            asset_key: List[str],
            run_id: Optional[str]
    ) -> Optional[Dict]:
        """
        Function to get a temporary download link from the Oxaigen Client API to a file in the Oxaigen data plane

        Args:
            asset_key (List[str]): The key identifying the asset.
            run_id (Optional[str]): The ID of the run.

        Returns:
            Optional[Dict]: Temporary download link data.
        """
        if not run_id:
            run_id = ""

        query = """
    query GetDownloadLink($assetKey: [String!]!, $runId: String = "") {
      getS3AssetDownloadLink(assetKey: $assetKey, runId: $runId) {
        ... on AssetDownloadLink {
          __typename
          downloadUrl
          fileSize
          fileType
          fileName
          lastModified
        }
        ... on AssetNotFound {
          __typename
          errorMessage
        }
        ... on AssetDownloadError {
          __typename
          errorMessage
        }
        ... on AuthenticationError {
          __typename
          errorMessage
        }
        ... on AuthorizationError {
          __typename
          errorMessage
        }
      }
    }
                """

        variables = {
            "assetKey": asset_key,
            "runId": run_id
        }

        return run_api_query(query=query, variables=variables)

    @staticmethod
    def _download_asset_file(url: str, file_path: List[str], file_name: str):
        """
         Function to download a file from bucket storage system using an S3 generated URL (with one-time-use credentials)

         Args:
             url (str): The URL to download the file from.
             file_path (List[str]): The path to save the downloaded asset.
             file_name (str): The name of the file to be downloaded.
         """
        # Create directory with path prefix
        full_path = os.path.join(USER_ROOT_DIR, *file_path)
        os.makedirs(full_path, exist_ok=True)
        full_file_path = os.path.join(full_path, file_name)

        # Check if the file exists before moving it
        if os.path.exists(full_file_path):
            if os.path.exists(full_path):
                file_size_mb = os.path.getsize(full_file_path) / (1024 * 1024)
                if file_size_mb < 200:
                    backup_name = f"{file_name}__backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    backup_path = os.path.join(full_path, backup_name)
                    shutil.move(full_file_path, backup_path)
                else:
                    logging.warning(
                        msg=f"Existing asset size ({str(file_size_mb)}) too large (>200mb), will not create backup")

        # Download the file
        response = requests.get(url, stream=True)
        with open(full_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logging.info(f"File {str(full_file_path)} downloaded!")

    @staticmethod
    def get_asset_from_file(file: str) -> Optional[Any]:
        """
        get an Asset from the Oxaigen Orchestration data plane from the internal User Cache

        Args:
            file (str): The path to the asset file.

        Returns:
            Optional[Any]: The asset data.
        """
        try:
            with open(file, 'rb') as f:
                data = pickle.load(f)
            return data
        except Exception as e:
            logging.warning(msg=f"Error reading asset file ({str(file)}) from disk. Error: {str(e)}")
            return None

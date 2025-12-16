# -*- coding: utf-8 -*-
"""
Created by Luca Roggeveen
"""
import os
import logging
import warnings
from typing import Protocol, Optional
from pydantic import PostgresDsn
from dagster_postgres.utils import get_conn_string

from ..constant import DEFAULT_REPORTS_DIR


class BaseSettingsInterface(Protocol):
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    S3_REGION: str
    S3_ENDPOINT: str
    S3_SSL: str
    DAGSTER_BUCKET: str
    CLIENT_BUCKET: str
    ENVIRONMENT: str
    DEPLOYMENT_NAME: str
    PROJECT_NAME: str
    CLIENT_NAME: str
    POSTGRES_CLIENT_SERVER_IP: str
    POSTGRES_CLIENT_SERVER_PORT: int
    POSTGRES_CLIENT_PASSWORD: str
    POSTGRES_CLIENT_DB_USER: str
    POSTGRES_CLIENT_DB_NAME: str
    SQLALCHEMY_DATABASE_SOURCE: Optional[PostgresDsn]
    SQLALCHEMY_DATABASE_URI: str
    PSYCOPG_DATABASE_URI: Optional[str]
    CLIENT_DAGSTER_CONNECTION_STRING: str
    SQLALCHEMY_DATABASE_CLIENT_SOURCE: Optional[PostgresDsn]
    SQLALCHEMY_CLIENT_DATABASE_URI: str
    PSYCOPG_CLIENT_DATABASE_URI: Optional[str]
    MLFLOW_TRACKING_URI: str
    MLFLOW_REGISTRY_URI: str
    REPORTS_DIR: str
    REPORTS_FILES_DIR: str


class Settings(BaseSettingsInterface):
    """
    config yaml values from the ENVIRONMENT default to 'N/A' if none are specified / cannot be found
    """
    # ENVIRONMENT: "DEVELOPMENT" | "STAGING" | "PROD"
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "DEVELOPMENT")
    DEPLOYMENT_NAME: str = os.environ.get("DAGSTER_DEPLOYMENT", "DEVELOPMENT")

    # GENERAL SETTINGS
    PROJECT_NAME: str = os.environ.get("PROJECT_NAME", "DEVELOPMENT")
    CLIENT_NAME: str = os.environ.get("CLIENT_NAME", "DEVELOPMENT")

    # CLIENT DATABASE
    POSTGRES_CLIENT_SERVER_IP: str = os.environ["POSTGRES_CLIENT_SERVER_IP"]
    POSTGRES_CLIENT_SERVER_PORT: int = int(os.environ["POSTGRES_CLIENT_SERVER_PORT"])
    POSTGRES_CLIENT_PASSWORD: str = os.environ["POSTGRES_CLIENT_DB_PASSWORD"]
    POSTGRES_CLIENT_DB_USER: str = os.environ["POSTGRES_CLIENT_DB_USER"]
    POSTGRES_CLIENT_DB_NAME: str = os.environ["POSTGRES_CLIENT_DB_NAME"]

    # DATABASE URI
    CLIENT_DAGSTER_CONNECTION_STRING: str = get_conn_string(
        username=POSTGRES_CLIENT_DB_USER,
        password=POSTGRES_CLIENT_PASSWORD,
        hostname=POSTGRES_CLIENT_SERVER_IP,
        port=str(POSTGRES_CLIENT_SERVER_PORT),
        db_name=POSTGRES_CLIENT_DB_NAME,
    )

    SQLALCHEMY_DATABASE_CLIENT_SOURCE: Optional[PostgresDsn] = PostgresDsn.build(
        scheme="postgresql",
        username=POSTGRES_CLIENT_DB_USER,
        password=POSTGRES_CLIENT_PASSWORD,
        host=POSTGRES_CLIENT_SERVER_IP,
        port=POSTGRES_CLIENT_SERVER_PORT,  # type: ignore
        path=POSTGRES_CLIENT_DB_NAME,
    )
    SQLALCHEMY_CLIENT_DATABASE_URI: str = str(SQLALCHEMY_DATABASE_CLIENT_SOURCE)

    PSYCOPG_CLIENT_DATABASE_URI: Optional[str] = (
        f"dbname={POSTGRES_CLIENT_DB_NAME} "
        f"user={POSTGRES_CLIENT_DB_USER} "
        f"password={POSTGRES_CLIENT_PASSWORD} "
        f"host={POSTGRES_CLIENT_SERVER_IP} "
        f"port={POSTGRES_CLIENT_SERVER_PORT} "
        f"connect_timeout=1"
    )

    # CLIENT BUCKET
    S3_ENDPOINT: str = os.environ["S3_ENDPOINT"]
    S3_REGION: str = os.environ["S3_REGION"]
    S3_SSL: str = os.environ["S3_SSL"]
    AWS_ACCESS_KEY_ID: str = os.environ["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY: str = os.environ["AWS_SECRET_ACCESS_KEY"]
    CLIENT_BUCKET: str = os.environ["CLIENT_BUCKET"]

    # CLIENT MLFLOW SERVER
    MLFLOW_TRACKING_URI: str = os.environ["MLFLOW_TRACKING_URI"]
    MLFLOW_REGISTRY_URI: str = os.environ["MLFLOW_REGISTRY_URI"]

    DAGSTER_BUCKET: str = os.environ["DAGSTER_BUCKET"]

    # DAGSTER REPORTS
    REPORTS_DIR: str = os.environ.get("CLIENT_ENGINE_REPORTS_PATH", DEFAULT_REPORTS_DIR)
    REPORTS_FILES_DIR: str = os.path.join(REPORTS_DIR, "files")

    # Check if reports dir exists, otherwise create it.
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
        logging.info(f"Created reports directory at {REPORTS_DIR}")

    # Check if reports files dir exists, otherwise create it
    if not os.path.exists(REPORTS_FILES_DIR):
        os.makedirs(REPORTS_FILES_DIR)
        logging.info(f"Created reports files directory at {REPORTS_FILES_DIR}")

    S3_IO_MANAGER_CONFIG: dict = {
        "region_name": os.environ["S3_REGION"],
        "endpoint_url": os.environ["S3_ENDPOINT"],
        "use_ssl": os.environ["S3_SSL"].lower() in ("1", "true", "yes"),
        "aws_access_key_id": os.environ["AWS_ACCESS_KEY_ID"],
        "aws_secret_access_key": os.environ["AWS_SECRET_ACCESS_KEY"],
    }

    class Config:
        case_sensitive = True

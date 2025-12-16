# -*- coding: utf-8 -*-
"""
Created by Luca Roggeveen
"""
import os
from typing import Optional

CLIENT_SERVER_IP_ENV_VAR = "CLIENT_SERVER_IP"
CLIENT_SERVER_PORT_ENV_VAR = "CLIENT_SERVER_PORT"
ROOT_DIR_ENV_VAR = "ROOT_DIR"
JUPYTERHUB_ROOT_DIR_ENV_VAR = "JUPYTERHUB_ROOT_DIR"


def get_env_var_with_fallback(primary: str, fallback: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieves an environment variable value with a fallback to another variable if the primary one is not set.

    Args:
        primary (str): The primary environment variable to retrieve.
        fallback (str): The fallback environment variable to use if the primary one is not set.
        default (Optional[str], optional): Default value to return if both primary and fallback variables are not set.
            Defaults to None.

    Returns:
        Optional[str]: The value of the primary environment variable if set, otherwise the value of the fallback
            environment variable, or the default value if neither are set.
    """
    return os.getenv(primary) or os.getenv(fallback, default)


# General configuration
USER_ROOT_DIR = get_env_var_with_fallback(ROOT_DIR_ENV_VAR, JUPYTERHUB_ROOT_DIR_ENV_VAR)

# API configuration
API_ENDPOINT = f"http://{os.environ.get(CLIENT_SERVER_IP_ENV_VAR)}:{os.environ.get(CLIENT_SERVER_PORT_ENV_VAR)}/v1/graphql"

# Data Storage configuration
S3_ENDPOINT = get_env_var_with_fallback('S3_ENDPOINT', 'JUPYTERLAB_S3_ENDPOINT')
S3_ACCESS_KEY_ID = get_env_var_with_fallback('S3_ACCESS_KEY_ID', 'JUPYTERLAB_S3_ACCESS_KEY_ID')
S3_SECRET_ACCESS_KEY = get_env_var_with_fallback('S3_SECRET_ACCESS_KEY', 'JUPYTERLAB_S3_SECRET_ACCESS_KEY')
S3_SSL = get_env_var_with_fallback('S3_SSL', 'JUPYTERLAB_S3_SSL', 'true').lower() == 'true'
S3_REGION = get_env_var_with_fallback('S3_REGION', 'JUPYTERLAB_S3_REGION')


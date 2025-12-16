# -*- coding: utf-8 -*-
import os
import requests
from typing import Dict, Any

from ..constant import CLIENT_ACCESS_TOKEN
from ..config import API_ENDPOINT
from .exception import OxaigenApiException


def run_api_query(query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
    """
    Util function to call the Oxaigen Private Client API and handles authorization errors
    """
    try:
        access_token = os.environ.get(CLIENT_ACCESS_TOKEN)

        # Define the payload
        payload = {
            "query": query,
            "variables": variables
        }
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        # Send the request
        response = requests.post(API_ENDPOINT, json=payload, headers=headers)
        if response.status_code != 200:
            raise OxaigenApiException(message=f"Oxaigen Client API connection error: {str(response.text)}")

        response_data = response.json()

        if "data" not in response_data:
            raise KeyError("Unknown API response, invalid query or input arguments provided.")

        response_data_dict: Dict = response_data["data"]

        return response_data_dict
    except Exception as e:
        raise OxaigenApiException(message=f"Could not perform API call, error: {str(e)}")

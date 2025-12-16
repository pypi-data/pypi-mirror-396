# # -*- coding: utf-8 -*-
# import os
# import json
# import logging
# import requests
# from typing import Dict, Any, Optional
#
# from ..constant import ACCESS_TOKEN
# from ..config import TOKEN_FILE_PATH, API_ENDPOINT
# from .exception import OxaigenApiException, OxaigenSDKException
#
#
# def verify_access_token() -> bool:
#     # Define the GraphQL mutation
#     mutation = '''
#     query TokenVerification() {
#       verifyAccessToken(username: $username, password: $password) {
#         ... on AccessTokenReturn {
#           __typename
#           userName
#         }
#         ... on InvalidAccessToken {
#           __typename
#           message
#         }
#       }
#     }
#     '''
#     # Define the payload
#     payload = {
#         "query": mutation,
#         "variables": {}
#     }
#     headers = {
#         "Authorization": f"Bearer {os.environ.get(ACCESS_TOKEN)}"
#     }
#     # Send the request
#     response = requests.post(API_ENDPOINT, json=payload, headers=headers)
#     if response.status_code != 200:
#         raise OxaigenApiException(message=f"Oxaigen Client API error: {str(response.text)}")
#
#     response_data = response.json()
#
#     if response_data['verifyAccessToken']['__typename'] == 'AccessTokenReturn':
#         return True
#
#     return False
#
#
# def refresh_tokens():
#     # Define the GraphQL mutation
#     mutation = '''
#     mutation RefreshToken() {
#       refreshAccessToken(refreshToken: refreshToken) {
#         ... on InvalidRefreshToken {
#           __typename
#           message
#         }
#         ... on TokenReturn {
#           __typename
#           accessToken
#           accessTokenExpirationDatetime
#           refreshToken
#           tokenType
#         }
#       }
#     }
#     '''
#     refresh_token = get_refresh_token_from_token_file()
#
#     if not refresh_token:
#         raise OxaigenSDKException(message=f"No token file available, please login")
#
#     # Define the payload
#     payload = {
#         "query": mutation,
#         "variables": {
#             "refreshToken": refresh_token,
#         }
#     }
#     # Send the request
#     response = requests.post(API_ENDPOINT, json=payload, headers={})
#     if response.status_code != 200:
#         raise OxaigenApiException(message=f"Oxaigen Client API error: {str(response.text)}")
#
#     # handle return
#     response_data = response.json()
#     token_return = response_data.get("data", {}).get("refreshAccessToken", {})
#
#     if token_return == {}:
#         raise OxaigenApiException(message=f"Cannot refresh tokens, new login required")
#
#     if token_return['__typename'] != 'InvalidRefreshToken':
#         raise OxaigenApiException(message=f"Cannot refresh tokens, new login required")
#
#     process_token_return(token_return=token_return)
#     logging.info("Tokens refreshed!")
#
#
# def process_token_return(token_return: Dict[str, Any]):
#     if token_return.get("__typename") == "TokenReturn":
#         access_token = token_return.get("accessToken")
#
#         # Set the access token as an environment variable
#         os.environ[ACCESS_TOKEN] = access_token
#
#         # Store the token data as a JSON file
#         token_data = {
#             "accessToken": access_token,
#             "accessTokenExpirationDatetime": token_return.get("accessTokenExpirationDatetime"),
#             "refreshToken": token_return.get("refreshToken"),
#             "tokenType": token_return.get("tokenType")
#         }
#
#         os.makedirs(os.path.dirname(TOKEN_FILE_PATH), exist_ok=True)
#
#         with open(TOKEN_FILE_PATH, "w") as token_file:
#             json.dump(token_data, token_file, indent=4)
#     else:
#         raise OxaigenSDKException(message="Invalid TokenReturn")
#
#
# def get_access_token_from_token_file() -> Optional[str]:
#     """
#     Get refresh
#     """
#     try:
#         with open(TOKEN_FILE_PATH, "r") as token_file:
#             token = json.load(token_file)
#         return token['accessToken']
#     except Exception as e:
#         return None
#
#
# def get_refresh_token_from_token_file() -> Optional[str]:
#     """
#     Get refresh
#     """
#     try:
#         with open(TOKEN_FILE_PATH, "r") as token_file:
#             token = json.load(token_file)
#         return token['refreshToken']
#     except Exception as e:
#         return None

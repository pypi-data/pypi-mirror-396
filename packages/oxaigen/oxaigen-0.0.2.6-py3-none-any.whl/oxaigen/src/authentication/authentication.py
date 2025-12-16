# # -*- coding: utf-8 -*-
# import getpass
# import requests
# import logging
#
# from ..config import API_ENDPOINT
# from ..util.token import process_token_return
# from ..util.exception import OxaigenApiException, OxaigenSDKException
#
#
# class OxaigenAuthentication:
#     """
#     Oxaigen Authentication class for handling user login and token management.
#     """
#
#     def __init__(self):
#         super().__init__()
#
#     @staticmethod
#     def login() -> None:
#         """
#         Handles user login by prompting for username and password, sending a GraphQL mutation
#         to the Oxaigen API, and processing the response.
#
#         Raises:
#             OxaigenSDKException: If there is an invalid login input or an unknown error during login.
#             OxaigenApiException: If the API returns a connection error or an invalid token response.
#         """
#         try:
#             username = input("Enter your username:")
#             password = getpass.getpass("Enter your password: ")
#         except Exception as e:
#             raise OxaigenSDKException(message='Invalid login input, try again!')
#
#         # Define the GraphQL mutation
#         mutation = '''
#         mutation LoginMutation($username: String!, $password: String!) {
#           login(username: $username, password: $password) {
#             ... on TokenReturn {
#               __typename
#               accessToken
#               accessTokenExpirationDatetime
#               refreshToken
#               tokenType
#             }
#             ... on InvalidLogin {
#               __typename
#               message
#             }
#           }
#         }
#         '''
#         # Define the payload
#         payload = {
#             "query": mutation,
#             "variables": {
#                 "username": username,
#                 "password": password
#             }
#         }
#
#         try:
#             # Send the request
#             response = requests.post(API_ENDPOINT, json=payload)
#
#             if response.status_code != 200:
#                 raise OxaigenApiException(message='Could not login to Oxaigen Client API, connection error')
#
#             response_data = response.json()
#
#             # Check if login was successful
#             token_return = response_data.get("data", {}).get("login", {})
#
#             if token_return == {}:
#                 raise OxaigenApiException(message="Invalid TokenReturn from login")
#
#             process_token_return(token_return=token_return)
#
#             logging.info("Login successful! Token stored!")
#
#         except OxaigenApiException:
#             raise
#         except Exception as e:
#             raise OxaigenSDKException(message=f"Login failed due to unknown error: {str(e)}")

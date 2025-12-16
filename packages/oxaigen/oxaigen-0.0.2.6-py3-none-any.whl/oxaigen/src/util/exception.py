# -*- coding: utf-8 -*-
from typing import Optional, Any

from .logging import logger


class OxaigenException(Exception):
    """
    Raise when an Oxaigen error is thrown
    """

    def __init__(self, message, *args):
        self.message = message
        logger.error(message)
        super().__init__(message, *args)


class OxaigenSDKException(OxaigenException):
    """
    Raised when an Oxaigen SDK error occurs.
    """

    def __init__(self, message, *args):
        log_message = f"Oxaigen SDK Exception occurred: {message}"
        logger.debug(log_message)
        super().__init__(message, *args)


class OxaigenApiException(OxaigenException):
    """
    Raised when an API related error occurs.
    """

    def __init__(self, message, *args):
        log_message = f"Oxaigen API Exception occurred: {message}"
        logger.debug(log_message)
        super().__init__(message, *args)

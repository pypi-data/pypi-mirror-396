# -*- coding: utf-8 -*-
from .src.main import Oxaigen

from .src.orchestration import (
    create_oxaigen_dbt_translator_class,
    OxaigenDbIOManager
)


def validate_oxaigen_sdk_import():
    """
    Validates the import of the Oxaigen SDK.

    This function checks if the Oxaigen SDK is properly imported and prints a success message if it is.

    Returns:
        None
    """
    print("Success!")


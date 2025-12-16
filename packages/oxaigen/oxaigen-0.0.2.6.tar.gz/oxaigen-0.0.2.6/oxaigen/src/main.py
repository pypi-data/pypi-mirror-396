# -*- coding: utf-8 -*-
from .asset.asset import OxaigenAsset
from .storage.data_storage import OxaigenDataStorage


class Oxaigen:
    """
    Oxaigen SDK Class
    """

    def __init__(self):
        self.asset = OxaigenAsset()
        self.storage = OxaigenDataStorage()

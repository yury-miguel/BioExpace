# -*- coding: utf-8 -*-

# Author: Yury
# Data: 04/10/2025

import os
import sys
from typing import Union
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orm import database

class HandlerDatabase():
    """Database user interface"""
    def __init__(self):
        self.db = database.Database()

    def call(self, func_name: str, **kwargs):
        """Call any function dynamically from Database"""
        if not hasattr(self.db, func_name):
            raise AttributeError(f"Function '{func_name}' not found in Database class.")
        func = getattr(self.db, func_name)
        return func(**kwargs)
# Copyright (C) 2015, Fortishield Inc.
# Created by Fortishield, Inc. <info@fortishield.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2

from unittest.mock import patch

with patch('fortishield.common.fortishield_uid'):
    with patch('fortishield.common.fortishield_gid'):
        from fortishield.core.results import AffectedItemsFortishieldResult


class CustomAffectedItems(AffectedItemsFortishieldResult):
    """Mock custom values that are needed in controller tests"""

    def __init__(self, empty: bool = False):
        if not empty:
            super().__init__(dikt={'dikt_key': 'dikt_value'},
                             affected_items=[{'id': '001'}])
        else:
            super().__init__()

    def __getitem__(self, key):
        return self.render()[key]

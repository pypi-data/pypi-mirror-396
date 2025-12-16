#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Administration Scripts
# Copyright (c) 2008-2025 Hive Solutions Lda.
#
# This file is part of Hive Administration Scripts.
#
# Hive Administration Scripts is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Administration Scripts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Administration Scripts. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__copyright__ = "Copyright (c) 2008-2025 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

configurations = (
    {
        "ignores": (
            "E501",
            "E203",
            "W293",
            "E701",
            "W291",
            "E231",
            "E251",
            "E302",
            "E121",
            "E261",
            "E713",
            "E502",
            "E711",
            "E128",
            "E126",
            "E702",
            "E122",
            "E129",
            "E721",
            "E262",
            "E712",
            "E124",
            "E127",
            "E125",
            "E131",
            "E123",
            "E402",
            "E731",
            "E704",
        ),
        "recursive": True,
        "file_exclusion": ("android-sdk",),
    },
)

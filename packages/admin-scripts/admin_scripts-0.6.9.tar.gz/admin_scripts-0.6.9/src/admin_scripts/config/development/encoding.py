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

__author__ = "Luís Martinho <lmartinho@hive.pt> & João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__copyright__ = "Copyright (c) 2008-2025 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

configurations = (
    {
        "recursive": True,
        "source_encoding": "Cp1252",
        "target_encoding": "utf-8",
        "windows_newline": True,
        "replacements_list": (),
        "file_extensions": (
            "js",
            "php",
            "cs",
            "java",
            "cpp",
            "c",
            "m",
            "mm",
            "hpp",
            "h",
            "cl",
            "pch",
            "lua",
            "cs",
            "st",
            "ctp",
            "xml",
            "xsd",
            "html",
            "xhtml",
            "wiki",
            "wik",
            "prl",
            "json",
            "yml",
            "txt",
            "hxml",
            "hx",
            "as",
            "mxml",
            "bat",
            "tpl",
            "vcproj",
            "csproj",
            "sln",
            "sol",
            "strings",
            "conf",
            "luquid",
            "go",
            "md",
            "swift",
            "Dockerfile",
            "vue",
            "gradle",
        ),
        "file_exclusion": ("android-sdk",),
    },
    {
        "recursive": True,
        "source_encoding": "Cp1252",
        "target_encoding": "utf-8",
        "windows_newline": True,
        "replacements_list": (
            ("# -*- coding: Cp1252 -*-\n", "# -*- coding: utf-8 -*-\n"),
        ),
        "file_extensions": ("py",),
        "file_exclusion": ("android-sdk",),
    },
    {
        "recursive": True,
        "source_encoding": "Cp1252",
        "target_encoding": "utf-8",
        "windows_newline": True,
        "replacements_list": (("# encoding: Cp1252\n", "# encoding: utf-8\n"),),
        "file_extensions": ("rb",),
        "file_exclusion": ("android-sdk",),
    },
    {
        "recursive": True,
        "source_encoding": "Cp1252",
        "target_encoding": "utf-8",
        "windows_newline": True,
        "replacements_list": (
            (
                '@charset "Cp1252";\n',
                '@charset "utf-8";\n',
            ),
        ),
        "file_extensions": ("css",),
        "file_exclusion": ("android-sdk",),
    },
    {
        "recursive": True,
        "source_encoding": "Cp1252",
        "target_encoding": "utf-8",
        "windows_newline": True,
        "replacements_list": (
            (
                "encoding/<project>=Cp1252\n",
                "encoding/<project>=utf-8\n",
            ),
        ),
        "file_extensions": ("prefs",),
        "file_exclusion": ("android-sdk",),
    },
    {
        "recursive": True,
        "source_encoding": "Cp1252",
        "target_encoding": "utf-8",
        "windows_newline": False,
        "replacements_list": (
            ("# -*- coding: Cp1252 -*-\n", "# -*- coding: utf-8 -*-\n"),
        ),
        "file_extensions": ("sh", "drg", "am", "m4", "kt", "asm", "rs"),
        "file_exclusion": ("android-sdk",),
    },
)

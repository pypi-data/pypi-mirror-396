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

import re

import legacy

CSS_COMMENTS = re.compile(r"/\*.*?\*/", re.MULTILINE | re.DOTALL)
HEX_COLOR = re.compile(r"#\w{2}\w{2}\w{2}")


def uniqify(all):
    unique = dict()
    for each in all:
        unique[each] = 1
    return unique.keys()


def simplify_hex_colors(text):
    """
    Replace all color declarations where pairs repeat.
    (eg: #aabbcc becomes #abc).

    :type text: String
    :param text: The payload text value that is going to
    have the color values simplified.
    :rtype: String
    :return: The simplified value according to the defined
    set of rules.
    """

    colour_replacements = {}
    all_hex_encodings = HEX_COLOR.findall(text)

    for e in uniqify(all_hex_encodings):
        if e[1] == e[2] and e[3] == e[4] and e[5] == e[6]:
            colour_replacements[e] = "#" + e[1] + e[3] + e[5]

    for key, value in colour_replacements.items():
        text = text.replace(key, value)

    return text


def css_slimmer(css):
    """
    Removes repeating whitespace characters like tab, newline
    or any other characters.

    :type css: String
    :param css: The string that contains the complete set of
    css code that is going to the "slimmed".
    :rtype: String
    :return: The final simplified/reduced set of css code that
    should represent the same original logic.
    """

    # verifies the data type of the provided string
    # value in case it's bytes it must be decoded
    # using the pre-defined fallback decoder
    is_bytes = type(css) == legacy.BYTES
    if is_bytes:
        css = css.decode("utf-8")

    remove_next_comment = 1
    for css_comment in CSS_COMMENTS.findall(css):
        if css_comment[-3:] == "\*/":
            remove_next_comment = 0
            continue
        if remove_next_comment:
            css = css.replace(css_comment, "")
        else:
            remove_next_comment = 1

    css = re.sub(r"\s\s+", " ", css)
    css = re.sub(r"\s+\n", "", css)

    for char in ("{", "}", ":", ";", ","):
        css = re.sub(char + r"\s", char, css)
        css = re.sub(r"\s" + char, char, css)
    css = re.sub(r"\s+</", r"</", css)
    css = re.sub(r"}\s(#|\w)", r"}\1", css)
    css = re.sub(r";}", r"}", css)
    css = re.sub(r"}//-->", r"}\n//-->", css)
    css = simplify_hex_colors(css)
    css.strip()

    # re-encodes the value into the default encoding so that it
    # becomes ready to be written into a bytes buffer object
    css = css.encode("utf-8")
    return css

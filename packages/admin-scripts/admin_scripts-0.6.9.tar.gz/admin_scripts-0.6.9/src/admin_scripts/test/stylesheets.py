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

import legacy
import unittest

import admin_scripts.base.stylesheets as stylesheets


class StylesheetsTest(unittest.TestCase):

    def test_rules(self):
        input = b""".property>.sub  >   .sub-sub  ,
        .property2    >.sub  >   .sub-sub  {
    margin   : 80px auto;
     border: 0;


      max-width: 1170px;;;
  padding: 0px 0px 32px 0px
  border-radius: 2px;
  -webkit-border-radius: 2px;;
   }
"""
        expected = """.property > .sub > .sub-sub,
.property2 > .sub > .sub-sub {
    border: none;
    border-radius: 2px 2px 2px 2px;
    -o-border-radius: 2px 2px 2px 2px;
    -ms-border-radius: 2px 2px 2px 2px;
    -moz-border-radius: 2px 2px 2px 2px;
    -khtml-border-radius: 2px 2px 2px 2px;
    -webkit-border-radius: 2px 2px 2px 2px;
    margin: 80px auto 80px auto;
    max-width: 1170px;
    padding: 0px 0px 32px 0px;
}
"""
        buffer = legacy.BytesIO(input)
        result = stylesheets.cleanup_properties(
            buffer,
            windows_newline=False,
            property_order=(
                "border",
                "border-radius",
                "-o-border-radius",
                "-ms-border-radius",
                "-moz-border-radius",
                "-khtml-border-radius",
                "-webkit-border-radius",
                "margin",
                "max-width",
                "padding",
            ),
        )
        result.seek(0)
        result = result.read()
        self.assertEqual(result, expected)

    def test_sub_rules(self):
        input = b"""@media     (max-width: 539px)    and     (min-width:   375px)   {
        slave {
max-width: 1170px;;;
  border   : 0;
        }

main,
            master {
  padding   : 0;
   -webkit-border-radius: 3px;;;
        }
}
"""
        expected = """@media (max-width: 539px) and (min-width: 375px) {
    slave {
        border: none;
        max-width: 1170px;
    }

    main,
    master {
        border-radius: 3px 3px 3px 3px;
        -o-border-radius: 3px 3px 3px 3px;
        -ms-border-radius: 3px 3px 3px 3px;
        -moz-border-radius: 3px 3px 3px 3px;
        -khtml-border-radius: 3px 3px 3px 3px;
        -webkit-border-radius: 3px 3px 3px 3px;
        padding: 0px 0px 0px 0px;
    }
}
"""
        buffer = legacy.BytesIO(input)
        result = stylesheets.cleanup_properties(
            buffer,
            windows_newline=False,
            property_order=(
                "border",
                "border-radius",
                "-o-border-radius",
                "-ms-border-radius",
                "-moz-border-radius",
                "-khtml-border-radius",
                "-webkit-border-radius",
                "max-width",
                "padding",
            ),
        )
        result.seek(0)
        result = result.read()
        self.assertEqual(result, expected)

    def test_keyframes_rules(self):
        input = b"""@keyframes line-scale {
    0%,
    40%,
    100% {
        transform: scaleY(0.4);
    }
    20% {
        transform: scaleY(1);
    }
}
"""
        expected = """@keyframes line-scale {
    0%,
    40%,
    100% {
        transform: scaleY(0.4);
        -o-transform: scaleY(0.4);
        -ms-transform: scaleY(0.4);
        -moz-transform: scaleY(0.4);
        -khtml-transform: scaleY(0.4);
        -webkit-transform: scaleY(0.4);
    }
    20% {
        transform: scaleY(1);
        -o-transform: scaleY(1);
        -ms-transform: scaleY(1);
        -moz-transform: scaleY(1);
        -khtml-transform: scaleY(1);
        -webkit-transform: scaleY(1);
    }
}
"""
        buffer = legacy.BytesIO(input)
        result = stylesheets.cleanup_properties(
            buffer,
            windows_newline=False,
            property_order=(
                "transform",
                "-o-transform",
                "-ms-transform",
                "-moz-transform",
                "-khtml-transform",
                "-webkit-transform",
            ),
        )
        result.seek(0)
        result = result.read()
        self.assertEqual(result, expected)

    def test_at_rules(self):
        input = b"""@charset "utf-8";"""
        expected = """@charset "utf-8";
"""
        buffer = legacy.BytesIO(input)
        result = stylesheets.cleanup_properties(buffer, windows_newline=False)
        result.seek(0)
        result = result.read()
        self.assertEqual(result, expected)

    def test_prefix_rules(self):
        input = b""".line-scale {
    animation: fade-in 1s ease-in-out;
}
"""
        expected = """.line-scale {
    animation: fade-in 1s ease-in-out;
    -o-animation: fade-in 1s ease-in-out;
    -ms-animation: fade-in 1s ease-in-out;
    -moz-animation: fade-in 1s ease-in-out;
    -khtml-animation: fade-in 1s ease-in-out;
    -webkit-animation: fade-in 1s ease-in-out;
}
"""
        buffer = legacy.BytesIO(input)
        result = stylesheets.cleanup_properties(
            buffer,
            windows_newline=False,
            property_order=(
                "animation",
                "-o-animation",
                "-ms-animation",
                "-moz-animation",
                "-khtml-animation",
                "-webkit-animation",
            ),
        )
        result.seek(0)
        result = result.read()
        self.assertEqual(result, expected)

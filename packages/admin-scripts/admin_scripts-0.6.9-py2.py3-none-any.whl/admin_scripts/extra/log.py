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

import sys

USE_STDERR = True
FLUSH_STREAM = True
STDOUT = sys.stdout
STDERR = sys.stderr if USE_STDERR else STDOUT


class StreamWrapper(object):

    def __init__(self, stream):
        self.stream = stream
        self.counter = 0

    def __getattr__(self, name):
        if hasattr(self.stream, name):
            return getattr(self.stream, name)
        raise AttributeError("'%s' not found" % name)

    @classmethod
    def wrap(cls, stream):
        if hasattr(stream, "counter"):
            return stream
        return cls(stream)

    def write(self, *args, **kwargs):
        self.counter += 1
        self.stream.write(*args, **kwargs)

    def written(self):
        return self.counter > 0


def echo(message):
    STDOUT.write(message + "\n")
    STDOUT.flush()


def warn(message):
    STDERR.write("WARNING: " + message + "\n")
    STDERR.flush()


def error(message):
    STDERR.write("ERROR: " + message + "\n")
    STDERR.flush()


def has_errors():
    return STDERR.written()


def wrap_all():
    global STDOUT
    global STDERR
    STDOUT = StreamWrapper.wrap(STDOUT)
    STDERR = StreamWrapper.wrap(STDERR)


wrap_all()

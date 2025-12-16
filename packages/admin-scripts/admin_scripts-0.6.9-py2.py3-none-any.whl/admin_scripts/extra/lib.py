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

import os
import sys
import json

import legacy

NT_PLATFORM = "nt"
""" The nt platform reference string value to be
used in operative system detection """

DOS_PLATFORM = "dos"
""" The dos platform used as a fallback reference
value for operation system detection mechanisms """

WINDOWS_PLATFORMS = (NT_PLATFORM, DOS_PLATFORM)
""" The windows platform values that may be used
to detect any environment running any version of windows """

LONG_PATH_PREFIX = legacy.UNICODE("\\\\?\\")
""" The windows long path prefix, used for special
construction of path values in windows """

IGNORE_FILE = ".cignore"
""" The name of the file that is going to be used to determine
if a path tree should be ignored and no operation should be
performed for any of its children """


def handle_ignore(directory_name, names, token=None):
    """
    Tries to handle the ignore operation for the provided
    set of names, this should include the changing of the
    names list in case its required.

    :type directory_name: String
    :param directory_name: The name of the current directory in the walk.
    :type names: List
    :param names: The list of directory names that are meant
    to be verified/handled for the ignore file.
    :type token: String
    :param token: The token that is going to be used to determine
    if the ignore operation should be performed.
    :rtype: bool
    :return: If the ignore operation has been processed for
    the current list of names.
    """

    if not IGNORE_FILE in names:
        return False

    ignore_file = open(os.path.join(directory_name, IGNORE_FILE), encoding="utf-8")
    is_full_ignore = False

    try:
        ignore_data = json.load(ignore_file)
    except json.JSONDecodeError:
        is_full_ignore = True

    if is_full_ignore:
        del names[:]
        return True

    for key, value in ignore_data.items():
        if not isinstance(value, list):
            value = [value]
        if value == None or token in value:
            names.remove(key)

    return False


def normalize_path(path):
    """
    Normalizes the given path, using the characteristics
    of the current environment.

    In windows this function adds support for long path names
    as defined in windows specification.

    :type path: String
    :param path: The path (to file) value that is going to
    be returned as normalized.
    :rtype: String
    :return: The normalized path, resulting from a series of
    normalization processes applied to the "original" path.-
    """

    # retrieves the current os name, as it's going to be used
    # to determine if windows normalization should be applied
    os_name = os.name

    # in case the current operative system is windows based and
    # the normalized path does start with the long path prefix it
    # must be removed to allow a "normal" path normalization
    if os_name in WINDOWS_PLATFORMS and path.startswith(LONG_PATH_PREFIX):
        # removes the long path prefix from the path
        path = path[4:]

    # checks if the path is absolute, as it will be used to determine
    # if the path should be normalized as absolute or not
    is_absolute_path = os.path.isabs(path)

    # in case the path is not absolute (creates problem in windows
    # long path support)
    if os_name in WINDOWS_PLATFORMS and not is_absolute_path:
        # converts the path to absolute
        path = os.path.abspath(path)

    # normalizes the path, using the underlying python function
    # that provided simple normalization process
    normalized_path = os.path.normpath(path)

    # in case the current operative system is windows based and
    # the normalized path does not start with the long path prefix
    if os_name in WINDOWS_PLATFORMS and not normalized_path.startswith(
        LONG_PATH_PREFIX
    ):
        # creates the path in the windows mode, adds
        # the support for long path names with the prefix token
        normalized_path = LONG_PATH_PREFIX + normalized_path

    # returns the "final" normalized path value resulting from
    # the various normalization processes applied to original path
    return normalized_path


def configuration(file_path=None, **kwargs):
    """
    Retrieves the configuration map(s) for the given arguments,
    the keyword based arguments are used as the configuration
    in case no valid configuration file exits (fallback).

    :type file_path: String
    :param file_path: The path to the file that is going to be
    processed as the configuration file in context.
    :rtype: Dictionary
    :return: The configuration structure/map, taking into account
    the current location structure.
    """

    # in case the configuration file path is defined, meaning that
    # a configuration file is expected to be loaded
    if file_path:
        # retrieves the configuration directory from the configuration
        # file path (the directory is going to be used to include the module)
        directory_path = os.path.dirname(file_path)
        directory_path = os.path.abspath(directory_path)

        # in case the (configuration directory) path is valid inserts it into the
        # system path, so that it's possible to load python files from it
        directory_path and sys.path.insert(0, directory_path)

        # retrieves the configuration file base path from the configuration file path
        file_base_path = os.path.basename(file_path)

        # retrieves the configuration module name and the configuration module extension
        # by splitting the configuration base path into base name and extension
        module_name, _module_extension = os.path.splitext(file_base_path)

        # imports the configuration module and retrieves the configurations
        # variable containing the "final" configuration structure
        configuration = __import__(module_name)
        configurations = configuration.configurations

    # otherwise the provided arguments (through keyword) are going to be used
    # as the basis for the creation of the configurations
    else:
        # creates the configurations tuple with the base configurations
        # coming from the keyword based arguments (as expected)
        configurations = (kwargs,)

    return configurations

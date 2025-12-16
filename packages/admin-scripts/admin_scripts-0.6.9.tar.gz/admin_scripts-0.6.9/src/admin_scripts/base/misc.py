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
import getopt

import legacy

import admin_scripts.extra as extra

USAGE_MESSAGE = "misc [-r] [-w exclusion_1, exclusion_2, ...] [-c configuration_file]"
""" The usage message to be printed in case there's an
error with the command line or help is requested. """


def chmod_file(file_path, mode):
    """
    Runs the change permission operation file process
    as defined by a series of specifications.

    :type file_path: String
    :param file_path: The path to the file that is going
    to have its permissions changed.
    :type mode: int
    :param mode: The target permissions mode for the file.
    """

    os.chmod(file_path, mode)


def misc_file(file_path, configuration):
    """
    Runs the misc set of operations on the file associated
    with the provided path.

    This operation should fail with an exception in case the
    structure of the XML document is not the expected one.

    :type file_path: String
    :param file_path: The path to the file that is going to
    subject to the misc operations.
    :type configuration: Dictionary
    :param configuration: The map of configuration that is
    going to be used while running the misc operations.
    """

    chmod = configuration.get("chmod", {})
    _base, extension = os.path.splitext(file_path)
    mode = chmod.get(extension.lstrip("."), None)
    if not mode == None:
        chmod_file(file_path, mode)


def misc_walker(arguments, directory_name, names):
    """
    Walker method to be used by the path walker for running the
    normalization misc process.

    :type arguments: Tuple
    :param arguments: The arguments tuple sent by the walker method.
    :type directory_name: String
    :param directory_name: The name of the current directory in the walk.
    :type names: List
    :param names: The list of names in the current directory.
    """

    # unpacks the arguments tuple into its values
    file_exclusion, configuration = arguments

    # retrieves the complete set of extensions registered for the chmod
    # operations and then gathers their keys as the basis for the extension
    # based filtering operations (optimization)
    chmod = configuration.get("chmod", {})
    extensions = legacy.keys(chmod)
    extensions = tuple(extensions)

    # tries to run the handle ignore operation for the current set of names and
    # in case there's a processing returns the control flow immediately as no
    # more handling is meant to occur for the current operation (ignored)
    if extra.handle_ignore(directory_name, names, token="misc"):
        return

    # removes the complete set of names that are meant to be excluded from the
    # current set names to be visit (avoid visiting them)
    for exclusion in file_exclusion:
        if not exclusion in names:
            continue
        names.remove(exclusion)

    # retrieves the valid names for the names list (removes directory entries)
    valid_complete_names = [
        directory_name + "/" + name
        for name in names
        if not os.path.isdir(directory_name + "/" + name)
    ]

    # filters the names with non valid file extensions so that only the
    # ones that conform with the misc source ones are selected
    valid_complete_names = [
        os.path.normpath(name)
        for name in valid_complete_names
        if name.endswith(tuple(extensions))
    ]

    # iterates over all the valid complete names with valid structure
    # as defined by the misc file structure definition
    for valid_complete_name in valid_complete_names:
        # print a message a message about the misc
        # operation that is going to be performed and
        # then runs the operation with the correct path
        extra.echo("Running the misc operations on file: %s" % valid_complete_name)
        misc_file(valid_complete_name, configuration)


def misc_recursive(directory_path, file_exclusion, configuration):
    """
    Runs the misc operations in recursive mode.
    All the options are arguments to be passed to the
    walker function.

    :type directory_path: String
    :param directory_path: The path to the (entry point) directory.
    :type file_exclusion: List
    :param file_exclusion: The list of file exclusion to be used.
    :type configuration: Dictionary
    :param configuration: The configuration structure to be used
    for the execution of the misc operations
    """

    legacy.walk(directory_path, misc_walker, (file_exclusion, configuration))


def _config(name):
    base_path = os.path.dirname(__file__)
    base_path = os.path.abspath(base_path)
    config_path = os.path.join(base_path, "..", "config")
    extra_path = os.path.join(config_path, "extra")
    name_path = os.path.join(extra_path, name)
    name_path = os.path.normpath(name_path)
    return name_path


def main():
    """
    Main function used for the misc source file normalization.
    """

    # in case the number of arguments
    # is not sufficient
    if len(sys.argv) < 2:
        # prints a series of message related with he
        # correct usage of the command line and then
        # exits the process with error indication
        extra.echo("Invalid number of arguments")
        extra.echo("Usage: " + USAGE_MESSAGE)
        sys.exit(2)

    # sets the default values for the parameters
    # this values are going to be used as the basis
    # for the generation of the configuration
    path = sys.argv[1]
    recursive = False
    file_exclusion = None
    configuration_file_path = None

    try:
        options, _arguments = getopt.getopt(sys.argv[2:], "rw:c:", [])
    except getopt.GetoptError:
        # prints a series of messages about the
        # correct usage of the command line and
        # exits the current process with an error
        extra.echo("Invalid number of arguments")
        extra.echo("Usage: " + USAGE_MESSAGE)
        sys.exit(2)

    # iterates over all the options, retrieving the option
    # and the value for each
    for option, value in options:
        if option == "-r":
            recursive = True
        elif option == "-w":
            file_exclusion = [value.strip() for value in value.split(",")]
        elif option == "-c":
            configuration_file_path = value

    # retrieves the configurations from the command line arguments
    # either from the command line or configuration file
    configurations = extra.configuration(
        file_path=configuration_file_path,
        recursive=recursive,
        file_exclusion=file_exclusion,
    )

    # iterates over all the configurations, executing them
    for configuration in configurations:
        # retrieves the configuration values
        recursive = configuration["recursive"]
        file_exclusion = configuration["file_exclusion"]

        # in case the recursive flag is set, normalizes the multiple
        # found misc source configuration file
        if recursive:
            misc_recursive(path, file_exclusion, configuration)
        # otherwise it's a "normal" iteration and runs the
        # misc normalization process in it
        else:
            misc_file(path, configuration)

    # verifies if there were messages printed to the standard
    # error output and if that's the case exits in error
    sys.exit(1 if extra.has_errors() else 0)


if __name__ == "__main__":
    main()
else:
    __path__ = []

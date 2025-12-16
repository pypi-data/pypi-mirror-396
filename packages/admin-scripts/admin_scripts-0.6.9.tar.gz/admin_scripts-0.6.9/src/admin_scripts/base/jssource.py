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

USAGE_MESSAGE = (
    "jssource [-r] [-w exclusion_1, exclusion_2, ...] [-c configuration_file]"
)
""" The usage message to be printed in case there's an
error with the command line or help is requested. """


def jssource_file(file_path, beautify=True, encoding="utf-8"):
    """
    Runs the javascript source file verification/validation process
    as defined by a series of specifications.

    :type file_path: String
    :param file_path: The path to the file that is going to be
    changed according to the jssource operation.
    :type beautify: bool
    :param beautify: If the beautification process should be
    run for the provided file for verification.
    :type encoding: String
    :param encoding: The encoding that is going to be used as the
    default one for the decoding operation in the source file.
    """

    try:
        import jsbeautifier
    except ImportError:
        jsbeautifier = None

    is_min = file_path.endswith("min.js")

    if jsbeautifier and beautify and not is_min:
        # reads the complete set of contents from the original
        # file and then tries to decode such contents using the
        # default encoding (as expected by the processor)
        file = open(file_path, "rb")
        try:
            contents = file.read()
        finally:
            file.close()
        contents = contents.decode(encoding)

        # creates the dictionary that will contain the complete
        # set of options to be applied in the beautify operation
        # and then uses such values to run the beautification process
        opts = jsbeautifier.default_options()
        opts.wrap_line_length = 120
        opts.end_with_newline = True
        opts.preserve_newlines = True
        opts.operator_position = "after-newline"
        opts.eol = "\r\n"
        result = jsbeautifier.beautify(contents, opts=opts)

        # determines if the result from the beautification process
        # is a bytes or unicode value and if it's not runs the encoding
        # and the re-writes the file with the new contents
        is_unicode = legacy.is_unicode(result)
        if is_unicode:
            result = result.encode(encoding)
        file = open(file_path, "wb")
        try:
            file.write(result)
        finally:
            file.close()


def jssource_walker(arguments, directory_name, names):
    """
    Walker method to be used by the path walker for running the
    normalization jssource process.

    :type arguments: Tuple
    :param arguments: The arguments tuple sent by the walker method.
    :type directory_name: String
    :param directory_name: The name of the current directory in the walk.
    :type names: List
    :param names: The list of names in the current directory.
    """

    # unpacks the arguments tuple
    (file_exclusion,) = arguments

    # tries to run the handle ignore operation for the current set of names and
    # in case there's a processing returns the control flow immediately as no
    # more handling is meant to occur for the current operation (ignored)
    if extra.handle_ignore(directory_name, names, token="jssource"):
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
    # ones that conform with the javascript source ones are selected
    valid_complete_names = [
        os.path.normpath(name)
        for name in valid_complete_names
        if name.endswith((".js", ".json"))
    ]

    # iterates over all the valid complete names with valid structure
    # as defined by the javascript file structure definition
    for valid_complete_name in valid_complete_names:
        # print a message a message about the jssource
        # operation that is going to be performed and
        # then runs the operation with the correct path
        extra.echo(
            "Transforming JavaScript source file (beautify): %s" % valid_complete_name
        )
        jssource_file(valid_complete_name)


def jssource_recursive(directory_path, file_exclusion):
    """
    Normalizes jssource in recursive mode.
    All the options are arguments to be passed to the
    walker function.

    :type directory_path: String
    :param directory_path: The path to the (entry point) directory.
    :type file_exclusion: List
    :param file_exclusion: The list of file exclusion to be used.
    """

    legacy.walk(directory_path, jssource_walker, (file_exclusion,))
    extra.shell_exec(
        "jshint",
        [directory_path, "--config", _config("jshint.json")],
        tester=["jshint", "--version"],
    )


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
    Main function used for the jssource file normalization.
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
        # found jssource configuration file
        if recursive:
            jssource_recursive(path, file_exclusion)
        # otherwise it's a "normal" iteration and runs the
        # jssource normalization process in it
        else:
            jssource_file(path)

    # verifies if there were messages printed to the standard
    # error output and if that's the case exits in error
    sys.exit(1 if extra.has_errors() else 0)


if __name__ == "__main__":
    main()
else:
    __path__ = []

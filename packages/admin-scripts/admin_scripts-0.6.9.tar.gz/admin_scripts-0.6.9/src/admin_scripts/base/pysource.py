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
    "pysource [-r] [-w exclusion_1, exclusion_2, ...] [-c configuration_file]"
)
""" The usage message to be printed in case there's an
error with the command line or help is requested. """


def pysource_file(file_path, run_pep8=True, ignores=()):
    """
    Runs the python source file verification/validation process
    as defined by a series of specifications.

    :type file_path: String
    :param file_path: The path to the file that contains the
    pysource configuration specification in xml.
    :type run_pep8: bool
    :param run_pep8: If the pep8 verification process should be
    run for the provided file for verification.
    :type ignores: Tuple
    :param ignores: A sequence of string values that define the
    various tests (in pep8) that are going to be ignored.
    """

    try:
        import pep8
    except ImportError:
        pep8 = None

    if pep8:

        class ErrorReport(pep8.StandardReport):
            def get_file_results(self):
                self._deferred_print.sort()
                for line_number, offset, code, text, doc in self._deferred_print:
                    extra.STDERR.write(
                        self._fmt
                        % dict(
                            path=self.filename,
                            row=self.line_offset + line_number,
                            col=offset + 1,
                            code=code,
                            text=text,
                        )
                        + "\n"
                    )
                    if self._show_pep8 and doc:
                        extra.STDERR.write("    " + doc.strip() + "\n")
                    extra.STDERR.flush()
                return self.file_errors

    if pep8 and run_pep8:
        checker = pep8.Checker(file_path, reporter=ErrorReport)
        checker.check_all(expected=ignores)


def pysource_walker(arguments, directory_name, names):
    """
    Walker method to be used by the path walker for running the
    normalization pysource process.

    :type arguments: Tuple
    :param arguments: The arguments tuple sent by the walker method.
    :type directory_name: String
    :param directory_name: The name of the current directory in the walk.
    :type names: List
    :param names: The list of names in the current directory.
    """

    # unpacks the arguments tuple
    file_exclusion, ignores = arguments

    # tries to run the handle ignore operation for the current set of names and
    # in case there's a processing returns the control flow immediately as no
    # more handling is meant to occur for the current operation (ignored)
    if extra.handle_ignore(directory_name, names, token="pysource"):
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
    # ones that conform with the python source ones are selected
    valid_complete_names = [
        os.path.normpath(name) for name in valid_complete_names if name.endswith(".py")
    ]

    # iterates over all the valid complete names with valid structure
    # as defined by the python file structure definition
    for valid_complete_name in valid_complete_names:
        # print a message a message about the pysource
        # operation that is going to be performed and
        # then runs the operation with the correct path
        extra.echo("Validation Python source file: %s" % valid_complete_name)
        pysource_file(valid_complete_name, ignores=ignores)


def pysource_recursive(directory_path, file_exclusion, ignores=()):
    """
    Normalizes pysource in recursive mode.
    All the options are arguments to be passed to the
    walker function.

    :type directory_path: String
    :param directory_path: The path to the (entry point) directory.
    :type file_exclusion: List
    :param file_exclusion: The list of file exclusion to be used.
    :type ignores: Tuple
    :param ignores: A sequence of string values that define the
    various tests (in pep8) that are going to be ignored.
    """

    legacy.walk(directory_path, pysource_walker, (file_exclusion, ignores))


def main():
    """
    Main function used for the pysource file normalization.
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
        ignores = configuration.get("ignores", ())

        # in case the recursive flag is set, normalizes the multiple
        # found pysource configuration file
        if recursive:
            pysource_recursive(path, file_exclusion, ignores=ignores)
        # otherwise it's a "normal" iteration and runs the
        # pysource normalization process in it
        else:
            pysource_file(path, ignores=ignores)

    # verifies if there were messages printed to the standard
    # error output and if that's the case exits in error
    sys.exit(1 if extra.has_errors() else 0)


if __name__ == "__main__":
    main()
else:
    __path__ = []

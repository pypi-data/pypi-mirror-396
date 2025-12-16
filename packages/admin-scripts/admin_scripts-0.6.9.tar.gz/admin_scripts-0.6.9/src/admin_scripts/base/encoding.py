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

import os
import sys
import getopt

import legacy

import admin_scripts.extra as extra

USAGE_MESSAGE = "encoding path [-r]\
[-s source_encoding]\
[-t target_encoding]\
[-u]\
[-x replacement_from_1, replacement_to_1, replacement_from_2, replacement_to_2, ...]\
[-e file_extension_1, file_extension_2, ...]\
[-w exclusion_1, exclusion_2, ...]\
[-c configuration_file]"
""" The usage message, to be printed when help is required
or when a command line error exists """

BOM_SEQUENCE = b"\xef\xbb\xbf"
""" The byte based sequence that defines the start of
an utf-8 bom encoded text file """


def has_encoding(string_buffer, encoding):
    """
    Determines if the provided buffer is encoded in the provided encoding.

    :type string_buffer: String
    :param string_buffer: The string buffer.
    :type encoding: String
    :param encoding: The encoding against which to test the string buffer.
    """

    # initializes the has encoding flag
    has_encoding = None

    try:
        # tries to decode the provided buffer, using the specified encoding
        # setting the has encoding flag to valid in case nothing fails
        string_buffer.decode(encoding)
        has_encoding = True
    except Exception:
        # sets the has encoding flag as false as there was an error while
        # trying to decode the buffer with the requested encoding
        has_encoding = False

    # returns the has encoding flag
    return has_encoding


def apply_replacements_list(string_buffer, replacements_list):
    """
    Applies a list of replacements to the provided string buffer.

    :type string_buffer: String
    :param string_buffer: The string to which the replacements are to be applied to.
    :type replacements_list: List
    :param replacements_list: The list of replacements to apply.
    """

    # iterates over all the replacements to be performed and applies
    # each of them to the provided string "buffer"
    for replacement in replacements_list:
        # unpacks the replacement tuple so that the source and the target
        # strings may be retrieved, and then performs the replacements
        replacement_from, replacement_to = replacement
        replacement_from = legacy.bytes(replacement_from)
        replacement_to = legacy.bytes(replacement_to)
        string_buffer = string_buffer.replace(replacement_from, replacement_to)

    # returns the replaced string buffer
    return string_buffer


def convert_encoding(
    file_path,
    source_encoding,
    target_encoding,
    windows_newline=True,
    replacements_list=None,
):
    """
    Converts the encoding of the specified file.

    :type file_path: String
    :param file_path: The path to the file to have its encoding converted.
    :type source_encoding: String
    :param source_encoding: The encoding from which the file is to be converted from.
    :type target_encoding: String
    :param target_encoding: The encoding to which the file is to be converted.
    :type windows_newline: bool
    :param windows_newline: If the windows newline should be used.
    :type replacements_list: List
    :param replacements_list: The list of replacements to perform.
    """

    # normalizes the file path and uses it as the path to
    # open the reference to it (in reading mode)
    file_path_normalized = extra.normalize_path(file_path)
    file = open(file_path_normalized, "rb")

    try:
        # reads the complete string contents from the file and
        # checks if the file already has the target encoding
        string_value = file.read()
        string_value = string_value.replace(b"\r\n", b"\n")
        string_value = string_value.replace(b"\r", b"\n")
        has_target_encoding = has_encoding(string_value, target_encoding)

        # in case the retrieved string value starts with the bom
        # (byte order mark) sequence it's removed as it's considered
        # deprecated as a method of detecting utf encoding
        if string_value.startswith(BOM_SEQUENCE):
            string_value = string_value[len(BOM_SEQUENCE) :]

        # decodes the string value from the specified source encoding, this
        # operation may fail as the source encoding may only be a guess on
        # the true encoding of the file, the encodes the string value again
        # in the target encoding for the file
        string_value_decoded = (
            not has_target_encoding
            and string_value.decode(source_encoding)
            or string_value
        )
        string_value_encoded = (
            not has_target_encoding
            and string_value_decoded.encode(target_encoding)
            or string_value_decoded
        )

        # applies the replacements if they're requested to be applied
        # so that the final string value is "normalized"
        string_value_encoded_replaced = (
            replacements_list
            and apply_replacements_list(string_value_encoded, replacements_list)
            or string_value_encoded
        )

        # applies the windows newline if specified, it does so by replacing
        # the simple newline character with the windows specific newline
        string_value_encoded_replaced = (
            windows_newline
            and string_value_encoded_replaced.replace(b"\n", b"\r\n")
            or string_value_encoded_replaced
        )
    finally:
        # closes the file for reading (as it's not longer required)
        file.close()

    # opens the file for writing then writes the file string value
    # with the proper string values replaced and re-encoded into the
    # target character encoding (as expected)
    file = open(file_path_normalized, "wb")
    try:
        file.write(string_value_encoded_replaced)
    finally:
        file.close()


def convert_encoding_walker(arguments, directory_name, names):
    """
    Walker method to be used by the path walker for the encoding conversion.

    :type arguments: Tuple
    :param arguments: The arguments tuple sent by the walker method.
    :type directory_name: String
    :param directory_name: The name of the current directory in the walk.
    :type names: List
    :param names: The list of names in the current directory.
    """

    # unpacks the arguments tuple
    (
        source_encoding,
        target_encoding,
        windows_newline,
        replacements_list,
        file_extensions,
        file_exclusion,
    ) = arguments

    # tries to run the handle ignore operation for the current set of names and
    # in case there's a processing returns the control flow immediately as no
    # more handling is meant to occur for the current operation (ignored)
    if extra.handle_ignore(directory_name, names, token="encoding"):
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

    # filters the names with non valid file extensions
    valid_complete_names = [
        os.path.normpath(name)
        for name in valid_complete_names
        if file_extensions == None
        or os.path.split(name)[-1].split(".")[-1] in file_extensions
    ]

    # creates the string based value of the windows newline taking into
    # account the boolean value of it
    windows_newline_s = "windows newline" if windows_newline else "unix newline"

    # iterates over all the valid complete names with extension filter
    # to convert the respective file into the target encoding
    for valid_complete_name in valid_complete_names:
        # prints a message about the file that is not going to be converted
        # into the proper target encoding as defined in the specification
        extra.echo(
            "Convert encoding in file: %s (%s to %s) (%s)"
            % (valid_complete_name, source_encoding, target_encoding, windows_newline_s)
        )

        try:
            # converts the encoding for the provided (path) name according to
            # a set of defined options, for various reasons this operation may
            # fail if such thing happens the operation is skipped
            convert_encoding(
                valid_complete_name,
                source_encoding,
                target_encoding,
                windows_newline,
                replacements_list,
            )
        except Exception:
            extra.warn(
                "Failed converting encoding in file: %s (%s to %s)"
                % (valid_complete_name, source_encoding, target_encoding)
            )


def convert_encoding_recursive(
    directory_path,
    source_encoding,
    target_encoding,
    windows_newline,
    replacements_list=None,
    file_extensions=None,
    file_exclusion=None,
):
    """
    Converts the file encoding in recursive mode.
    All the options are arguments to be passed to the
    walker function.

    :type directory_path: String
    :param directory_path: The path to the (entry point) directory.
    :type source_encoding: String
    :param source_encoding: The source encoding from which the file is to be
    converted.
    :type target_encoding: String
    :param target_encoding: The target encoding to which the file is to be
    converted to.
    :type replacements_list: List
    :param replacements_list: The list of replacements to perform.
    :type file_extensions: List
    :param file_extensions: The list of file extensions to be used.
    :type file_exclusion: List
    :param file_exclusion: The list of file exclusion to be used.
    """

    legacy.walk(
        directory_path,
        convert_encoding_walker,
        (
            source_encoding,
            target_encoding,
            windows_newline,
            replacements_list,
            file_extensions,
            file_exclusion,
        ),
    )


def main():
    """
    Main function used for the encoding conversion.
    """

    # in case the number of arguments
    # is not sufficient
    if len(sys.argv) < 2:
        # prints a series of messages about the command line
        # error that occurred and then exits with an error
        extra.echo("Invalid number of arguments")
        extra.echo("Usage: " + USAGE_MESSAGE)
        sys.exit(2)

    # sets the default values for the parameters
    path = sys.argv[1]
    recursive = False
    source_encoding = None
    target_encoding = None
    windows_newline = None
    replacements_list = None
    file_extensions = None
    file_exclusion = None
    configuration_file_path = None

    try:
        options, _arguments = getopt.getopt(sys.argv[2:], "rs:t:x:e:w:c:", [])
    except getopt.GetoptError:
        # prints a series of messages about the command line
        # error that occurred and then exits with an error
        extra.echo("Invalid number of arguments")
        extra.echo("Usage: " + USAGE_MESSAGE)
        sys.exit(2)

    # iterates over all the options, retrieving the option
    # and the value for each
    for option, value in options:
        if option == "-r":
            recursive = True
        elif option == "-s":
            source_encoding = value
        elif option == "-t":
            target_encoding = value
        elif option == "-u":
            windows_newline = value
        elif option == "-x":
            replacements_list = [value.strip() for value in value.split(",")]
        elif option == "-e":
            file_extensions = [value.strip() for value in value.split(",")]
        elif option == "-w":
            file_exclusion = [value.strip() for value in value.split(",")]
        elif option == "-c":
            configuration_file_path = value

    # retrieves the configurations from the command line arguments
    configurations = extra.configuration(
        file_path=configuration_file_path,
        recursive=recursive,
        source_encoding=source_encoding,
        target_encoding=target_encoding,
        windows_newline=windows_newline,
        replacements_list=replacements_list,
        file_extensions=file_extensions,
        file_exclusion=file_exclusion,
    )

    # iterates over all the configurations, executing them
    for configuration in configurations:
        # retrieves the configuration values
        recursive = configuration["recursive"]
        source_encoding = configuration["source_encoding"] or "utf-8"
        target_encoding = configuration["target_encoding"] or "utf-8"
        windows_newline = configuration["windows_newline"] or True
        replacements_list = configuration["replacements_list"] or ()
        file_extensions = configuration["file_extensions"] or ()
        file_exclusion = configuration["file_exclusion"] or ()

        # in case the recursive flag is set must converts the files
        # using the recursive mode
        if recursive:
            convert_encoding_recursive(
                path,
                source_encoding,
                target_encoding,
                windows_newline,
                replacements_list,
                file_extensions,
                file_exclusion,
            )
        # otherwise it's a "normal" iteration, must converts the
        # encoding (for only one file)
        else:
            convert_encoding(
                path,
                source_encoding,
                target_encoding,
                windows_newline,
                replacements_list,
            )

    # verifies if there were messages printed to the standard
    # error output and if that's the case exits in error
    sys.exit(1 if extra.has_errors() else 0)


if __name__ == "__main__":
    main()
else:
    __path__ = []

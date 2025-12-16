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
import re
import sys
import getopt

import xml.dom.minidom

import legacy

import admin_scripts.extra as extra

USAGE_MESSAGE = "pydev [-r] [-w exclusion_1, exclusion_2, ...] [-c configuration_file]"
""" The usage message to be printed in case there's an
error with the command line or help is requested. """

PREFIX_REGEX = re.compile("/[^/]+")
""" The prefix regular expression used to match the initial
part of the source directory file path """

VALID_PROPERTIES = (
    "org.python.pydev.PYTHON_PROJECT_VERSION",
    "org.python.pydev.PYTHON_PROJECT_INTERPRETER",
)
""" The sequence that defines the complete set of properties that
are considered valid under the current pydev specification """


def pydev_file(file_path, fix=True):
    """
    Runs the pydev configuration file normalization that consists
    in the definition in order of each of the XML lines.

    This operation should fail with an exception in case the
    structure of the XML document is not the expected one.

    :type file_path: String
    :param file_path: The path to the file that contains the
    pydev configuration specification in XML.
    :type fix: bool
    :param fix: If any "fixable" error in the pydev project
    file should be automatically fixes using the known heuristics,
    this is a dangerous option as errors may be created.
    """

    paths = []
    properties = dict()
    buffer = []

    xmldoc = xml.dom.minidom.parse(file_path)
    nodes = xmldoc.getElementsByTagName("pydev_property")

    for node in nodes:
        value = text_value(node)
        name = node.attributes["name"].value
        properties[name] = value

    nodes = xmldoc.getElementsByTagName("pydev_pathproperty")
    nodes = nodes[0].childNodes if nodes else []

    for node in nodes:
        value = text_value(node)
        if not value:
            continue
        paths.append(value)

    for key in legacy.keys(properties):
        if key in VALID_PROPERTIES:
            continue
        raise RuntimeError("Invalid property '%s'" % key)

    if fix:
        paths, properties = fix_values(paths, properties)

    python_version = properties.get("org.python.pydev.PYTHON_PROJECT_VERSION", None)
    if not python_version:
        extra.warn("No python version defined")
    elif not python_version == "python 3.6":
        extra.warn("Python version not 3.6")

    for path in paths:
        if path.startswith("/${PROJECT_DIR_NAME}"):
            continue
        extra.warn("Project directory path not normalized '%s'" % path)

    property_keys = legacy.keys(properties)
    property_keys.sort()

    buffer.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
    buffer.append('<?eclipse-pydev version="1.0"?><pydev_project>\n')
    if paths:
        buffer.append(
            '<pydev_pathproperty name="org.python.pydev.PROJECT_SOURCE_PATH">\n'
        )
    for path in paths:
        buffer.append("<path>%s</path>\n" % path)
    if paths:
        buffer.append("</pydev_pathproperty>\n")
    for key in property_keys:
        value = properties[key]
        buffer.append('<pydev_property name="%s">%s</pydev_property>\n' % (key, value))
    buffer.append("</pydev_project>\n")

    result = "".join(buffer)
    result = result.encode("utf-8")

    file = open(file_path, "wb")
    try:
        file.write(result)
    finally:
        file.close()


def fix_values(paths, properties):
    """
    Runs the fixer of the various loaded values from the pydev
    configuration file.

    These set of operations should be able to fix most of the
    known errors in the pydev configuration, this is a dangerous
    operation as it may cause problems in data structure.

    :type paths: List
    :param paths: The sequences of paths that should represent
    the main entry points for the python source code in project.
    :type properties: Dictionary
    :param properties: The map containing the option name to value
    associations that were loaded from the source pydev file.
    :rtype: Tuple
    :return: The resulting values from the provided configurations
    these values should have been fixed.
    """

    _paths = []

    for path in paths:
        if not path:
            continue
        if not "/" in path:
            _paths.append(path)
        elif path.startswith("/${PROJECT_DIR_NAME}"):
            _paths.append(path)
        else:
            _paths.append(PREFIX_REGEX.sub("/${PROJECT_DIR_NAME}", path, 1))

    return _paths, properties


def text_value(node):
    """
    Retrieves the text/XML string value for the provided
    node, this is a recursive approach and the child nodes
    are used as the entry point.

    :type node: Element
    :param node: The base element node from which the values
    are going to be retrieved.
    :rtype: String
    :return: The string/textual part of the XML element node
    provided.
    """

    nodes = node.childNodes

    data = []
    for node in nodes:
        if not node.nodeType == node.TEXT_NODE:
            continue
        data.append(node.data)

    return "".join(data)


def pydev_walker(arguments, directory_name, names):
    """
    Walker method to be used by the path walker for running the
    normalization pydev process.

    :type arguments: Tuple
    :param arguments: The arguments tuple sent by the walker method.
    :type directory_name: String
    :param directory_name: The name of the current directory in the walk.
    :type names: List
    :param names: The list of names in the current directory.
    """

    # unpacks the arguments tuple
    file_exclusion, fix = arguments

    # tries to run the handle ignore operation for the current set of names and
    # in case there's a processing returns the control flow immediately as no
    # more handling is meant to occur for the current operation (ignored)
    if extra.handle_ignore(directory_name, names, token="pydev"):
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
    # ones that conform with the pydev project ones are selected
    valid_complete_names = [
        os.path.normpath(name)
        for name in valid_complete_names
        if name.endswith(".pydevproject")
    ]

    # iterates over all the valid complete names with valid structure
    # as defined by the pydev project specification
    for valid_complete_name in valid_complete_names:
        # print a message a message about the pydev
        # operation that is going to be performed and
        # then runs the operation with the correct path
        extra.echo("Normalizing pydev configuration file: %s" % valid_complete_name)
        pydev_file(valid_complete_name, fix=fix)


def pydev_recursive(directory_path, file_exclusion, fix=True):
    """
    Normalizes pydev in recursive mode.
    All the options are arguments to be passed to the
    walker function.

    :type directory_path: String
    :param directory_path: The path to the (entry point) directory.
    :type file_exclusion: List
    :param file_exclusion: The list of file exclusion to be used.
    :type fix: bool
    :param fix: If any "fixable" error in the pydev project
    file should be automatically fixes using the known heuristics,
    this is a dangerous option as errors may be created.
    """

    legacy.walk(directory_path, pydev_walker, (file_exclusion, fix))


def main():
    """
    Main function used for the pydev file normalization.
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
        fix = configuration.get("fix", True)

        # in case the recursive flag is set, normalizes the multiple
        # found pydev configuration file
        if recursive:
            pydev_recursive(path, file_exclusion, fix=fix)
        # otherwise it's a "normal" iteration and runs the
        # pydev normalization process in it
        else:
            pydev_file(path, fix=fix)

    # verifies if there were messages printed to the standard
    # error output and if that's the case exits in error
    sys.exit(1 if extra.has_errors() else 0)


if __name__ == "__main__":
    main()
else:
    __path__ = []

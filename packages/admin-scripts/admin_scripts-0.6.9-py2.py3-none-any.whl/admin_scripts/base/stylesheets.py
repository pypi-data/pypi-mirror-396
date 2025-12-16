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
import re
import sys
import getopt
import traceback

import legacy

import admin_scripts.extra as extra

USAGE_MESSAGE = "cleanup-stylesheets-python path [-r] [-u] [-n]\
[-p property_name_1, property_name_2, ...]\
[-s rule_skip_1, rule_skip_2, ...]\
[-e file_extension_1, file_extension_2, ...]\
[-w exclusion_1, exclusion_2, ...]\
[-c configuration_file]"
""" The usage message, that is going to be displayed
once it's requested or an error occurs """

COLOR_REGEX_VALUE = r"(.*:)(.*#)([0-9a-fA-F]+)(.*)"
""" The color regex value """

COLOR_REGEX = re.compile(COLOR_REGEX_VALUE)
""" The color regex """

VALID_COLOR_LENGTHS = (3, 6)
""" The list of valid color declaration lengths
meaning that only colors of these size are allowed
by the stylesheet analyser """

AT_RULES_REGEX_VALUE = r"\@charset|\@import .*;"
""" The at rules regex value """

AT_RULES_REGEX = re.compile(AT_RULES_REGEX_VALUE)
""" The at rules regex """

URL_REGEX_VALUE = r"url\([\"'](.*)[\"']\)"
""" The URL regex value """

URL_REGEX = re.compile(URL_REGEX_VALUE)
""" The URL regex """

URL_REPLACEMENT_VALUE = "url(\g<1>)"
""" The URL replacement regex value """

PROPERTY_LINE_REGEX_VALUE = r"^[ ]*([\w\-]*)[ ]*:[ ]*(\S*)"
""" The property line regex value """

PROPERTY_LINE_REGEX = re.compile(PROPERTY_LINE_REGEX_VALUE)
""" The property line regex """

PROPERTY_LINE_REPLACEMENT_VALUE = "\g<1>: \g<2>"
""" The property line replacement value """

TOKEN_REGEX_VALUE = r"\s*([>\+\s])\s*"
""" The regex value meant to catch the various css related
tokens that are separated with a space compatible character """

TOKEN_REGEX = re.compile(TOKEN_REGEX_VALUE)
""" The regex meant to catch the various css related
tokens that are separated with a space compatible character """

COMMA_REGEX_VALUE = r"\s*(,)\s*"
""" The regex value that defines a valid comma under css,
note that multiple characters before and after are allowed """

COMMA_REGEX = re.compile(COMMA_REGEX_VALUE)
""" The regex that defines a valid comma under css,
note that multiple characters before and after are allowed """

SPACE_REGEX_VALUE = r"\s+"
""" The regex value that defines a valid space under css,
note that multiple characters are allowed """

SPACE_REGEX = re.compile(SPACE_REGEX_VALUE)
""" The regex that defines a valid space under css,
note that multiple characters are allowed """

RULES_MAP = {
    "left": ("zero_to_zero_px",),
    "top": ("zero_to_zero_px",),
    "right": ("zero_to_zero_px",),
    "bottom": ("zero_to_zero_px",),
    "border": ("zero_to_none",),
    "margin": ("zero_to_multiple", "one_to_multiple", "two_to_multiple"),
    "padding": ("zero_to_multiple", "one_to_multiple", "two_to_multiple"),
    "border-radius": ("zero_to_multiple", "one_to_multiple", "two_to_multiple"),
}
""" The map that associates various property names
with the various rules that should be applied to them """

BROWSER_PREFIXES = ("-o", "-ms", "-moz", "-khtml", "-webkit")
""" The sequence that defines the complete set of accepted
browser prefixes for the stylesheet usage """

PREFIXED_NAMES = (
    "animation",
    "animation-delay",
    "animation-duration",
    "animation-name",
    "appearance",
    "backface-visibility",
    "background-clip",
    "border-bottom-left-radius",
    "border-bottom-right-radius",
    "border-radius",
    "border-top-left-radius",
    "border-top-right-radius",
    "box-shadow",
    "box-sizing",
    "column-count",
    "column-gap",
    "filter",
    "font-smoothing",
    "hyphens",
    "opacity",
    "osx-font-smoothing",
    "outline",
    "overflow-scrolling",
    "perspective",
    "print-color-adjust",
    "tab-size",
    "highlight-color",
    "fill-color",
    "text-shadow",
    "touch-callout",
    "transform",
    "transform-origin",
    "transform-style",
    "transition",
    "transition-delay",
    "transition-duration",
    "transition-property",
    "transition-timing-function",
    "user-select",
    "zoom",
)
""" The complete set of property names that should be prefixed
with proper browser prefixes (complex properties) """


def get_property_index(property_line, property_order, line_number):
    """
    Retrieves the index for the property specified in the provided property
    line, this index may be used to correctly position the property.

    :type property_line: String
    :param property_line: The property line containing the property.
    :type property_order: List
    :param property_order: The list of property names in order.
    :type line_number: int
    :param line_number: The approximate line number for this processing.
    :rtype: int
    :return: The index of the property line, note that in case an index
    value is not found for the rule a large index is returned instead.
    """

    # splits the property name, to retrieve the property value
    # this first splits tries to find also the number of values
    # present in the current line
    property_line_splitted = property_line.split(":")

    # in case the property line did not correctly split must
    # returns immediately with the provided property order
    if len(property_line_splitted) < 2:
        return len(property_order)

    # runs a second split operation that limits the number of splits
    # in the line to two so that no extra problems are raised and then
    # retrieves the name of the current property
    property_line_splitted = property_line.split(":", 1)
    property_name, property_value = property_line_splitted
    property_name = property_name.strip()
    property_value = property_value.strip()

    # in case the property name or value are empty, raises an exception indicating
    # the problem to be handled at the top layers
    if not property_name:
        raise Exception("property name is empty")
    if not property_value:
        raise Exception("property value is empty")

    # in case the property is not in the order
    if not property_name in property_order:
        # warns about the missing property name and returns the
        # largest possible index value for any property name
        extra.warn(
            "Order for property %s not defined at line %d"
            % (property_name, line_number)
        )
        return len(property_order)

    # in case the property value starts with a separator it's considered
    # that the value is a extra/duplicated separator
    if property_value[0] == ":":
        # warns about the extra values in the line, so that the duplicated
        # information may be properly removed and considered
        extra.warn("Extra values found at line %d" % line_number)

    # determines the index for the property name and returns
    # the value to the caller method
    property_index = property_order.index(property_name)
    return property_index


def write_lines(output_buffer, lines, windows_newline=True, avoid_empty=False):
    """
    Writes the provided lines to the output buffer, considering the windows
    newline option.

    :type output_buffer: StringBuffer
    :param output_buffer: The output buffer.
    :type lines: List
    :param lines: The list of lines to output.
    :type windows_newline: bool
    :param windows_newline: If the windows newline should be used.
    :type avoid_empty: bool
    :param avoid_empty: If the empty lines (after strip operation)
    should be considered invalid and not written to buffer.
    """

    # iterates over the complete set of lines that are going
    # to be written to the buffer and writes their value
    for line in lines:
        write_line(
            output_buffer,
            line,
            windows_newline=windows_newline,
            avoid_empty=avoid_empty,
        )


def write_line(output_buffer, line, windows_newline=True, avoid_empty=False):
    """
    Writes the provided line to the output buffer, considering the windows
    newline option. This is considered a normalization operation.

    :type output_buffer: StringBuffer
    :param output_buffer: The output buffer.
    :type line: List
    :param line: The line that is going to be written to output buffer.
    :type windows_newline: bool
    :param windows_newline: If the windows newline should be used.
    :type avoid_empty: bool
    :param avoid_empty: If the empty lines (after strip operation)
    should be considered invalid and not written to buffer.
    """

    # right strips the line so that no extra space characters
    # are present in the line and then writes the line to the
    # string buffer (flush operation)
    line = line.rstrip()
    output_buffer.write(line)

    # in case the avoid empty flag is set and the line value
    # is considered invalid/empty, it's ignored
    if avoid_empty and not line:
        return

    # in case the newline mode is of type windows writes the
    # typical carriage return new line values otherwise writes
    # the unix simpler value with just a newline character
    if windows_newline:
        output_buffer.write("\r\n")
    else:
        output_buffer.write("\n")


def process_property_lines(
    property_lines, line_number, indentation=0, avoid_empty=False
):
    """
    Processes the property lines, this process should be
    iterative for each of the lines passed in the list.

    :type property_lines: List
    :param property_lines: The property lines to process.
    :type line_number: int
    :param line_number: The approximate line number for this processing.
    :type avoid_empty: bool
    :param avoid_empty: If the empty lines should avoid any
    kind of processing (extra errors may occur).
    :type indentation: int
    :param indentation: The level of indentation to be used for the processing
    of the various property lines, this value is going to be used in the
    operation of pre-pending spaced to the property rules.
    :rtype: List
    :return: The processed property lines.
    """

    # processes the property lines one by one so that the
    # properly represent the same semantic value but with
    # a better/standard representation of the value
    processed_property_lines = [
        process_property_line(property_line, line_number, indentation)
        for property_line in property_lines
        if not avoid_empty or property_line.strip()
    ]

    # runs the initial process of simplifying the property lines
    # by running the various rules for the current property lines
    processed_property_lines = process_rules_g(
        processed_property_lines, line_number, indentation
    )

    # runs an extra step to check for any duplicated line
    # in the set of processed property lines
    check_duplicates(processed_property_lines, line_number)

    # returns the processed property lines
    return processed_property_lines


def process_rules_g(property_lines, line_number, indentation):
    # creates the dictionary that is going to hold the multiple
    # properly lines indexed by their name
    property_lines_m = dict()

    # iterates over the complete set of property lines to split
    # them into name and value and populate the map of properties
    for property_line in property_lines:
        parts = property_line.split(":", 1)
        if len(parts) == 1:
            parts += [""]
        name, value = parts
        name = name.strip()
        value = value.strip()
        property_lines_m[name] = value

    # runs the complete set of global rules against the property
    # lines map so that it gets properly updated, running then the
    # re-creation of the properly lines list (should re-run ordering)
    process_rule_all_g(property_lines_m)
    property_lines = [
        "%s%s: %s" % (indentation * " " * 4, name, value)
        for name, value in legacy.items(property_lines_m)
    ]
    return property_lines


def process_rule_all_g(property_lines_m):
    process_rule_prefixes_g(property_lines_m)


def process_rule_prefixes_g(property_lines_m):
    prefixes = [""] + list(BROWSER_PREFIXES)

    for name in PREFIXED_NAMES:
        exists = False

        for prefix in prefixes:
            name_p = prefix + "-" + name if prefix else name
            if not name_p in property_lines_m:
                continue
            exists = True
            break

        if not exists:
            continue

        value = property_lines_m[name_p]

        for prefix in prefixes:
            name_p = prefix + "-" + name if prefix else name
            property_lines_m[name_p] = value

    return property_lines_m


def check_duplicates(property_lines, line_number):
    # retrieves the complete set of names for the rules, this is
    # going to be used as the base unit for duplicate checking
    names = [line.strip().split(":", 1)[0] for line in property_lines]

    # starts the sequence/list that is going to store the already
    # visited sequence of names (for duplicate detection)
    visited = []

    # iterates over the complete set of names to detect any duplicated
    # value printing a warning message for such situation
    for name in names:
        if name in visited:
            extra.warn("Duplicated property line '%s' at line %s" % (name, line_number))
        visited.append(name)


def process_property_line(property_line, line_number, indentation):
    # in case the property line is empty, when stripped the property
    # is considered to be empty (warning required) logs the message
    # and then returns the line itself (no processing)
    if not property_line.strip():
        extra.warn("Empty stylesheet property at line %s" % line_number)
        return property_line

    # in case no separator is present between the name of the property
    # the value of it a warning is raised and the value returned immediately
    # to avoid further (unavoidable) errors
    if not ":" in property_line:
        extra.warn("No value set for property at line %s" % line_number)
        return property_line

    # strips the line to the right so that no newline characters
    # exist (much simpler to manage lines without newlines)
    property_line = property_line.rstrip()
    property_line = property_line.rstrip(";")

    # runs the initial process of simplifying the property by running
    # the various rules for the current property name
    property_line = process_rules(property_line, line_number)

    # ensures the property line is correctly indented and
    # the property name and value are correctly separated
    padding = indentation * " " * 4
    property_line = PROPERTY_LINE_REGEX.sub(
        padding + PROPERTY_LINE_REPLACEMENT_VALUE, property_line
    )

    # ensures the property line and an ending semicolon
    # adding it to the property line in case it does not
    # exists (for processing)
    is_valid = property_line.endswith(";")
    if not is_valid:
        property_line += ";"

    # replaces the urls so that no double quotes are used in
    # them and instead the value is used directly
    property_line = URL_REGEX.sub(URL_REPLACEMENT_VALUE, property_line)

    # processes the color definitions, so that the complete
    # color value is used in the processing
    property_line = process_color_definition(property_line, line_number)

    # returns the processed property line
    return property_line


def rule_zero_to_zero_px(name, value):
    if not value in ("0",):
        return
    return "%s: 0px;" % name


def rule_zero_to_multiple(name, value):
    if not value in ("0", "0px"):
        return
    return "%s: 0px 0px 0px 0px;" % name


def rule_zero_to_none(name, value):
    if not value in ("0", "0px"):
        return
    return "%s: none;" % name


def rule_one_to_multiple(name, value):
    parts = value.split()
    if not len(parts) == 1:
        return
    if value in ("initial", "inherit"):
        return
    return "%s: %s %s %s %s;" % (name, value, value, value, value)


def rule_two_to_multiple(name, value):
    parts = value.split()
    if not len(parts) == 2:
        return
    if value in ("initial", "inherit"):
        return
    return "%s: %s %s;" % (name, value, value)


def process_rules(property_line, line_number):
    # retrieves the initial value for the property name
    # by splitting the line value, this value is going to
    # be used for the resolution of the final rules (set)
    property_name, _property_value = property_line.split(":", 1)
    property_name = property_name.strip()

    # constructs the base name, by removing the complete set
    # of browser prefixes, this value is going to be used as
    # the basis for the retrieval of rules (wildcard retrieval)
    base_name = property_name
    for prefix in BROWSER_PREFIXES:
        if not base_name.startswith(prefix):
            continue
        base_name = base_name[len(prefix) + 1 :]

    # tries to retrieve the set of rules (as strings) that are
    # going to be applied to the current property and then runs
    # the iteration cycle to apply each of them on the line
    rules = RULES_MAP.get(base_name, [])
    for rule in rules:
        # creates the (rule) method name by appending the name of
        # the current rule to the prefix and tries to retrieve a
        # global function with such name in case it does not exists
        # continues the current loop (nothing to be done)
        method_name = "rule_" + rule
        method = globals().get(method_name, None)
        if not method:
            continue

        # unpacks the property line into name and value so that proper
        # per name rule application is possible for the line
        property_name, property_value = property_line.split(":", 1)
        property_name = property_name.strip()
        property_value = property_value.strip()
        property_value = property_value.rstrip(";")

        # calls the proper rule method with the (current) property name
        # and value and verifies if a valid result is returned in case
        # it does replaces the property line value with the new value
        result = method(property_name, property_value)
        if not result:
            continue
        property_line = result

    # returns the "final" processed line according to the defined
    # set of rules for the property (name)
    return property_line


def process_color_definition(property_line, line_number):
    # tries to match the color regex and retrieves the resulting
    # set of groups from the match, in case there's no matching
    # the control flow is returned immediately to the caller
    line_match = COLOR_REGEX.match(property_line)
    line_groups = line_match.groups() if line_match else None
    if not line_groups:
        return property_line

    # unpacks the various line groups into the appropriate
    # variables to be used in the processing of the color
    property_name, pre_color, color, post_color = line_groups

    try:
        # runs the fixing color operation and then, re-joins the
        # various groups again into a single string (from list)
        color = fix_color(color)
        line_groups = [property_name, pre_color, color, post_color]
        property_line = "".join(line_groups)
    except Exception as exception:
        # converts the exception to string and then
        # prints a warning to the proper output
        exception_string = legacy.UNICODE(exception)
        extra.warn("%s near line %d" % (exception_string, line_number))

    # returns the property line
    return property_line


def fix_color(color):
    # computes the color length and the runs the lowercase
    # operation in (as it's expected)
    color_length = len(color)
    color = color.lower()

    # in case the color length is not in the valid range
    # raises an exception indicating the problem
    if not color_length in VALID_COLOR_LENGTHS:
        raise Exception("invalid color length")

    # in case the color is compacted must expand the
    # string value to double the size (as expected)
    if color_length == 3:
        color_list = [value * 2 for value in color]
        color = "".join(color_list)

    # returns the fixed color
    return color


def skip_rule(start_line, rules_skip):
    """
    Determines if the rule started by the provided line should be skipped.

    :type start_line: String
    :param start_line: The line which starts the rule.
    :type rules_skip: List
    :param rules_skip: The list of rules to skip.
    """

    # initializes the skip rule flag
    skip_rule = None

    # for each of the rules to skip
    for rule_skip in rules_skip:
        # checks if the rule is to be skipped
        # and if that's the case breaks the loop
        skip_rule = rule_skip in start_line
        if skip_rule:
            break

    # returns the skip rule value
    return skip_rule


def cleanup_properties(
    input_buffer,
    windows_newline=True,
    fix_extra_newlines=True,
    property_order=(),
    rules_skip=(),
):
    """
    Cleans up the property lines. Sorts the css properties in the file,
    by the specified property order.

    Ensures that all property lines are correctly terminated with semicolon.

    :type input_buffer: StringBuffer
    :param input_buffer: The input buffer.
    :type windows_newline: bool
    :param windows_newline: If the windows newline should be used.
    :type windows_newline: bool
    :param windows_newline: If the extra newlines should be fixed.
    :type fix_extra_newlines: bool
    :param fix_extra_newlines: If the extra newlines should be fixed.
    :type property_order: List
    :param property_order: The list with the explicit order of property names.
    :type rules_skip: List
    :param rules_skip: The list of specific rules to skip.
    """

    # reads the input lines and counts the number of lines
    # in the buffer setting it as the number of "original" lines
    lines = input_buffer.readlines()
    number_original_lines = len(lines)

    # creates a string buffer that will hold the output of the
    # cleanup operation over the current stylesheet file
    output_buffer = legacy.StringIO()

    # initializes a series of state variables that will control
    # the way the parser/generator will work through the file
    rule_started = False
    line_number = 0
    open_rule_count = 0
    newlines = 0
    comments_started = 0
    needs_newline = False

    # for each of the input lines it's going to run the iteration
    # loop and match it against the proper rules
    for line in lines:
        # decodes the current line as a processing using unicode
        # characters is required for correct results
        line = line.decode("utf-8")

        # increments the line number as one more line is going
        # to be processes through the current iteration
        line_number += 1

        # updates the comparison key function
        get_comparison_key = lambda property_line: get_property_index(
            property_line, property_order, line_number
        )

        # in case the line contains a single line comment,
        # does nothing, will write the line as is
        if "/*" in line and "*/" in line and not "*/*/" in line:
            pass

        # in case the line contains the end of multiline comment
        elif "*/" in line:
            # in case the comment mode is currently not enabled prints
            # a warning as we're trying to close a comment without opening
            if not comments_started:
                extra.error(
                    "Found closing comment without corresponding opening at line %d"
                    % line_number
                )

            # in case there's more that one closing comment defined under
            # the same line prints an error as this is not allowed
            if line.count("*/") > 1:
                extra.error("More that one closing comment at line %d" % line_number)

            # decrements the comments started counter and then
            # enables the needs newline flag
            comments_started = 0
            needs_newline = True

        # in case the line contains a the start of multiline comment
        elif "/*" in line:
            # in case the comment mode is already enabled (at least one)
            # prints a waning about the double opening
            if comments_started:
                extra.warn(
                    "Found opening comment inside open comment at line %d" % line_number
                )

            # in case there's more that one opening comment defined under
            # the same line prints an error as this is not allowed
            if line.count("/*") > 1:
                extra.error("More that one opening comment at line %d" % line_number)

            # increments the comments started counter
            comments_started += 1

        # in case this is a comment line (comment started)
        # does nothing, will just write the line as is
        elif comments_started:
            pass

        # in case the line contains an at rule specification
        elif AT_RULES_REGEX.match(line):
            # after an at rule, a newline must follow
            needs_newline = True

        # in case the line contains a full rule specification
        # does nothing, will just write line as is as there's
        # very few thing possible to optimize under this situation
        elif "{" in line and "}" in line:
            line = line.strip()
            needs_newline = True
            rule_started = False

        # in case this is a rule start line
        elif "{" in line:
            # increments the open rule count
            open_rule_count += 1

            # in case this is an actual rule, meaning that the open rule
            # count value is positive (assertion valid)
            if open_rule_count > 0:
                # resets the rule lines
                rule_lines = []

                # signals the rule started flag,
                # in case the rule is no to be skipped
                rule_started = not skip_rule(line, rules_skip)

            # replaces the various css tokens with proper separators
            # meaning that no extra spaces between them are allowed
            line = TOKEN_REGEX.sub(r" \1 ", line)

            # runs the space replacement operation so that the
            # extra spaces in the line (not required) are removed
            # and the line is simplified
            line = SPACE_REGEX.sub(" ", line)
            line = line.strip()

            # calculates the space padding that is going to be pre-pended
            # to the line and then adds it to the line note that the open
            # rule count is decremented by one (opened on this line)
            padding = (open_rule_count - 1) * 4 * " "
            line = padding + line

            # flushes the current line value to the output buffer and then
            # continues the current loop (avoids general operations)
            write_line(output_buffer, line, windows_newline)
            continue

        elif "}" in line:
            # decrements the open rule count
            open_rule_count -= 1

            # in case there is a mismatch in open and closed rules
            # must raise an exception indicating the problem
            if open_rule_count < 0:
                raise Exception("mismatched rules found")

            # strips the current line removing any extra (not expected)
            # values and simplifying the current line value
            padding = open_rule_count * 4 * " "
            line = line.strip()
            line = padding + line

            # in case the rule set does not contain any property
            # must log an information message about the empty rule
            if rule_started and not rule_lines:
                extra.warn("Empty stylesheet rule at line %d" % line_number)

            # updates the flag to signal the rule has ended
            rule_started = False

            # sorts the various property lines and the processes them
            property_lines = sorted(rule_lines, key=get_comparison_key)
            property_lines = process_property_lines(
                property_lines,
                line_number,
                indentation=open_rule_count + 1,
                avoid_empty=fix_extra_newlines,
            )
            property_lines = sorted(property_lines, key=get_comparison_key)

            # writes the lines to the buffer, considering the windows newline
            # and then writes the line
            write_lines(
                output_buffer,
                property_lines,
                windows_newline=windows_newline,
                avoid_empty=fix_extra_newlines,
            )
            write_line(output_buffer, line, windows_newline=windows_newline)

            # resets the newlines counter and then
            # enables the needs newline flag
            newlines = 0
            needs_newline = True
            rule_lines = []

            # skips further processing
            continue

        # in case this is part of rule selector declaration
        # the typical rule replacement operations are applied
        elif line.rstrip().endswith(","):
            line = TOKEN_REGEX.sub(r" \1 ", line)
            line = SPACE_REGEX.sub(" ", line)
            line = COMMA_REGEX.sub(r"\1", line)
            line = line.strip()

        # in case this line is part of a valid rule set
        elif rule_started:
            # appends the line to the rule set, and then
            # skips outputting the line to the buffer
            rule_lines.append(line)
            continue

        # in case the between rules mode is active
        elif not rule_started and not line.strip():
            # increments the newlines count
            newlines += 1

            # otherwise in case this is an extra newline, must either
            # remove it or print a warning message depending on mode
            if not needs_newline and newlines > 1:
                if fix_extra_newlines:
                    continue
                else:
                    extra.warn("Found extra newline at line %d" % line_number)

            # disables the needs newline flag
            needs_newline = False

        else:
            # warns about the statement outside a valid rule
            extra.warn("Found statement outside rule at line %d" % line_number)

        # "calculates" the padding string value taking into account the
        # current open rule count value and then removes any left space
        # compatible values and replaces them with proper indentation
        padding = open_rule_count * 4 * " "
        line = line.lstrip()
        line = padding + line

        # writes the line to the output buffer taking into
        # account the windows newline control flag
        write_line(output_buffer, line, windows_newline)

    # in case there is a mismatch in open and closed rules
    # must raise an exception indicating the problem
    if not open_rule_count == 0:
        raise Exception("mismatched rules found")

    # retrieves the output buffer value and then counts the
    # number of lines contained in it (assertion validation)
    output_buffer_value = output_buffer.getvalue()
    number_lines = output_buffer_value.count("\n")

    if not number_lines == number_original_lines and not fix_extra_newlines:
        raise Exception(
            "number of lines in processed file (%d) is different from original file (%d)"
            % (number_lines, number_original_lines)
        )

    return output_buffer


def cleanup_stylesheets(
    file_path_normalized,
    windows_newline,
    fix_extra_newlines,
    property_order,
    rules_skip,
):
    """
    Cleans up stylesheets. Sorts the css properties in the file, by the specified property order.
    Ensures that all property lines are correctly terminated with semicolon.

    :type file_path_normalized: String
    :param file_path_normalized: The file path normalized.
    :type windows_newline: bool
    :param windows_newline: If the windows newline should be used.
    :type fix_extra_newlines: bool
    :param fix_extra_newlines: If the extra newlines should be fixed.
    :type property_order: List
    :param property_order: The list with the explicit order of property names.
    :type rules_skip: List
    :param rules_skip: The list of specific rules to skip.
    """

    # opens the file for reading in text mode so that the
    # lines are read in normalized mode
    file = open(file_path_normalized, "rb")

    try:
        # applies the property cleaning, this should run the
        # complete set of rules and clean the file
        string_buffer = cleanup_properties(
            file,
            windows_newline=windows_newline,
            fix_extra_newlines=fix_extra_newlines,
            property_order=property_order,
            rules_skip=rules_skip,
        )

        # retrieves the string value from the output
        # buffer to be written to the file and then
        # encodes it using the default encoding of css
        string_value = string_buffer.getvalue()
        string_value = string_value.encode("utf-8")
    except Exception as exception:
        # retrieves the exception string and uses it in the log
        # message to be printed to the standard output, then logs
        # the complete traceback messages to the same output
        exception_string = legacy.UNICODE(exception)
        extra.error("%s. Skipping file %s" % (exception_string, file_path_normalized))
        traceback.print_exc(file=sys.stdout)

        # skips writing to the file
        return
    finally:
        # closes the file for reading
        file.close()

    # opens the file for writing and then outputs the
    # final normalized stylesheet contents into it
    file = open(file_path_normalized, "wb")
    try:
        file.write(string_value)
    finally:
        file.close()


def cleanup_stylesheets_walker(arguments, directory_name, names):
    """
    Walker method to be used by the path walker for the cleanup
    of stylesheets.

    :type arguments: Tuple
    :param arguments: The arguments tuple sent by the walker method.
    :type directory_name: String
    :param directory_name: The name of the current directory in the walk.
    :type names: List
    :param names: The list of names in the current directory.
    """

    # unpacks the arguments tuple
    (
        windows_newline,
        fix_extra_newlines,
        property_order,
        rules_skip,
        file_extensions,
        file_exclusion,
    ) = arguments

    # tries to run the handle ignore operation for the current set of names and
    # in case there's a processing returns the control flow immediately as no
    # more handling is meant to occur for the current operation (ignored)
    if extra.handle_ignore(directory_name, names, token="stylesheets"):
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

    # filters the names with non valid file extensions so that
    valid_complete_names = [
        os.path.normpath(name)
        for name in valid_complete_names
        if file_extensions == None
        or os.path.split(name)[-1].split(".")[-1] in file_extensions
    ]

    # iterates over all the valid complete names with extension filter
    for valid_complete_name in valid_complete_names:
        extra.echo("Cleaning stylesheet file: %s" % valid_complete_name)

        # removes the cleanups the stylesheet for the (path) name
        cleanup_stylesheets(
            valid_complete_name,
            windows_newline,
            fix_extra_newlines,
            property_order,
            rules_skip,
        )


def cleanup_stylesheets_recursive(
    directory_path,
    windows_newline,
    fix_extra_newlines,
    property_order=[],
    rules_skip=[],
    file_extensions=None,
    file_exclusion=None,
):
    """
    Cleans up stylesheets in recursive mode.
    All the options are arguments to be passed to the
    walker function.

    :type directory_path: String
    :param directory_path: The path to the (entry point) directory.
    :type windows_newline: bool
    :param windows_newline: If the windows newline should be used.
    :type fix_extra_newlines: bool
    :param fix_extra_newlines: If the extra newlines should be fixed.
    :type property_order: List
    :param property_order: The list with the explicit order of property names.
    :type rules_skip: List
    :param rules_skip: The list of specific rules to skip.
    :type file_extensions: List
    :param file_extensions: The list of file extensions to be used.
    :type file_exclusion: List
    :param file_exclusion: The list of file exclusion to be used.
    """

    legacy.walk(
        directory_path,
        cleanup_stylesheets_walker,
        (
            windows_newline,
            fix_extra_newlines,
            property_order,
            rules_skip,
            file_extensions,
            file_exclusion,
        ),
    )


def main():
    """
    Main function used for the processing of the stylesheet
    files so that a normalized form is outputted.
    """

    # in case the number of arguments
    # is not sufficient
    if len(sys.argv) < 2:
        # prints a series of message about the correct
        # usage of the command line and the exits the
        # current process with an error code
        extra.echo("Invalid number of arguments")
        extra.echo("Usage: " + USAGE_MESSAGE)
        sys.exit(2)

    # sets the default values for the parameters
    path = sys.argv[1]
    recursive = False
    windows_newline = True
    fix_extra_newlines = False
    property_order = None
    rules_skip = None
    file_extensions = None
    file_exclusion = None
    configuration_file_path = None

    try:
        options, _arguments = getopt.getopt(sys.argv[2:], "rp:e:w:c:", [])
    except getopt.GetoptError:
        # prints a series of message about the correct
        # usage of the command line and the exits the
        # current process with an error code
        extra.echo("Invalid number of arguments")
        extra.echo("Usage: " + USAGE_MESSAGE)
        sys.exit(2)

    # iterates over all the options, retrieving the option
    # and the value for each
    for option, value in options:
        if option == "-r":
            recursive = True
        if option == "-u":
            windows_newline = True
        if option == "-n":
            fix_extra_newlines = True
        if option == "-p":
            property_order = [value.strip() for value in value.split(",")]
        if option == "-s":
            rules_skip = [value.strip() for value in value.split(",")]
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
        windows_newline=windows_newline,
        fix_extra_newlines=fix_extra_newlines,
        property_order=property_order,
        rules_skip=rules_skip,
        file_extensions=file_extensions,
        file_exclusion=file_exclusion,
    )

    # iterates over all the configurations, executing them
    for configuration in configurations:
        # retrieves the configuration values
        recursive = configuration["recursive"]
        windows_newline = configuration["windows_newline"]
        fix_extra_newlines = configuration["fix_extra_newlines"]
        property_order = configuration["property_order"] or ()
        rules_skip = configuration["rules_skip"] or ()
        file_extensions = configuration["file_extensions"] or ()
        file_exclusion = configuration["file_exclusion"] or ()

        # in case the recursive flag is set, removes the trailing
        # spaces in recursive mode
        if recursive:
            cleanup_stylesheets_recursive(
                path,
                windows_newline,
                fix_extra_newlines,
                property_order,
                rules_skip,
                file_extensions,
                file_exclusion,
            )
        # otherwise it's a "normal" iteration, removes the trailing
        # spaces (for only one file)
        else:
            cleanup_stylesheets(
                path, windows_newline, fix_extra_newlines, property_order, rules_skip
            )

    # verifies if there were messages printed to the standard
    # error output and if that's the case exits in error
    sys.exit(1 if extra.has_errors() else 0)


if __name__ == "__main__":
    main()
else:
    __path__ = []

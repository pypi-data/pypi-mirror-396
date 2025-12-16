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


class JavascriptMinify(object):
    """
    Class used to minify javascript code.
    The minification is done using a classic
    parsing approach.
    """

    def _out_a(self):
        """
        Outputs the "first" value to the output
        file buffer.
        This method works like a flushing utility
        for the first value.
        """

        self.output_file.write(self.theA)

    def _out_b(self):
        self.output_file.write(self.theB)

    def _get(self):
        """
        return the next character from stdin. Watch out for lookahead. If
        the character is a control character, translate it to a space or
        linefeed.
        """

        # tries to retrieves the character
        # from the look ahead and then unsets
        # the look ahead
        character = self.look_ahead
        self.look_ahead = None

        # in case the look ahead character is not
        # found (need to read from the input file
        # buffer)
        if character == None:
            # reads a character from the input
            # file buffer
            character = self.input_file.read(1)

        # in case the character is a "normal" alpha
        # numeric character
        if character >= " " or character == "\n":
            # returns the character
            return character

        # in case not character is found
        # end of file is reached
        if character == "":
            # returns the end of string character
            return "\0"

        # in case the character is a carriage return
        # (windows newline present)
        if character == "\r":
            # returns "just" the normal
            # newline character
            return "\n"

        # as a "failover" return the space
        # character
        return " "

    def _peek(self):
        # retrieves the current item from
        # the input buffer
        self.look_ahead = self._get()

        # returns the look ahead character
        # as the "read" character
        return self.look_ahead

    def _next(self):
        """
        get the next character, excluding comments. peek() is used to see
        if a '/' is followed by a '/' or '*'.
        """

        # retrieves the current character
        # (removes the character from "input buffer")
        character = self._get()

        # in case the current character represents
        # a possible comment character (possible
        # line removal)
        if character == "/":
            # peeks the next character to be sure
            # that this is a comment
            next_character = self._peek()

            if next_character == "/":
                character = self._get()

                while character > "\n":
                    character = self._get()

                return character

            if next_character == "*":
                character = self._get()

                # iterates continuously
                while True:
                    character = self._get()

                    if character == "*":
                        if self._peek() == "/":
                            self._get()
                            return " "

                    if character == "\0":
                        # raises a runtime error
                        raise RuntimeError("unterminated comment")

        # returns the current character
        return character

    def _action(self, action):
        """
        do something! What you do is determined by the argument:
        1   Output A. Copy B to A. Get the next B.
        2   Copy B to A. Get the next B. (Delete A).
        3   Get the next B. (Delete B).
        action treats a string as a single character. Wow!
        action recognizes a regular expression if it is preceded by ( or , or =.
        """

        if action <= 1:
            self._out_a()

        if action <= 2:
            self.theA = self.theB
            if self.theA == "'" or self.theA == '"':
                while True:
                    self._out_a()
                    self.theA = self._get()
                    if self.theA == self.theB:
                        break
                    if self.theA <= "\n":
                        raise RuntimeError("unterminated string literal")
                    if self.theA == "\\":
                        self._out_a()
                        self.theA = self._get()

        if action <= 3:
            self.theB = self._next()

            if self.theB == "/" and (
                self.theA == "("
                or self.theA == ","
                or self.theA == "="
                or self.theA == ":"
                or self.theA == "["
                or self.theA == "?"
                or self.theA == "!"
                or self.theA == "&"
                or self.theA == "|"
                or self.theA == ";"
                or self.theA == "{"
                or self.theA == "}"
                or self.theA == "\n"
            ):
                self._out_a()
                self._out_b()

                # iterates continuously
                while True:
                    self.theA = self._get()
                    if self.theA == "/":
                        break
                    elif self.theA == "\\":
                        self._out_a()
                        self.theA = self._get()
                    elif self.theA <= "\n":
                        # raises a runtime error
                        raise RuntimeError("unterminated regular expression")
                    self._out_a()

                self.theB = self._next()

    def _jsmin(self):
        """
        Copy the input to the output, deleting the characters which are
        insignificant to JavaScript. Comments will be removed. Tabs will be
        replaced with spaces. Carriage returns will be replaced with linefeeds.
        Most spaces and linefeeds will be removed.
        """
        self.theA = "\n"
        self._action(3)

        while self.theA != "\0":
            if self.theA == " ":
                if is_alpha(self.theB):
                    self._action(1)
                else:
                    self._action(2)
            elif self.theA == "\n":
                if self.theB in ["{", "[", "(", "+", "-"]:
                    self._action(1)
                elif self.theB == " ":
                    self._action(3)
                else:
                    if is_alpha(self.theB):
                        self._action(1)
                    else:
                        self._action(2)
            else:
                if self.theB == " ":
                    if is_alpha(self.theA):
                        self._action(1)
                    else:
                        self._action(3)
                elif self.theB == "\n":
                    if self.theA in ["}", "]", ")", "+", "-", '"', "'"]:
                        self._action(1)
                    else:
                        if is_alpha(self.theA):
                            self._action(1)
                        else:
                            self._action(3)
                else:
                    self._action(1)

    def minify(self, input_file, output_file):
        # sets the file values
        self.input_file = input_file
        self.output_file = output_file

        # sets some of the minifications variables
        self.theA = "\n"
        self.theB = None
        self.look_ahead = None

        # runs the minification
        self._jsmin()

        # closes the input file
        self.input_file.close()


def javascript_minify(string_value):
    """
    "Minifies" the given string value assuming it
    contains javascript code in it.
    The heuristics used in the minification should not
    change the normal behavior of the file.

    :type string_value: String
    :param string_value: The string containing the value
    to be minified, may be an normal or byte string.
    :rtype: String
    :return: The minified string value.
    """

    # verifies the data type of the provided string
    # value in case it's bytes it must be decoded
    # using the pre-defined fallback decoder
    is_bytes = type(string_value) == legacy.BYTES
    if is_bytes:
        string_value = string_value.decode("utf-8")

    # creates a new string buffer with the given
    # string value (for the input) and then creates
    # new empty string buffer for the result
    string_buffer = legacy.StringIO(string_value)
    string_buffer_result = legacy.StringIO()

    # creates a new javascript minify object
    # and runs the minification
    javascript_minify = JavascriptMinify()
    javascript_minify.minify(string_buffer, string_buffer_result)

    # retrieves the string value (result) from the
    # string buffer
    string_value_result = string_buffer_result.getvalue()

    # in case the string value of result is valid and starts
    # with a newline character (need to strip)
    if string_value_result and string_value_result[0] == "\n":
        # removes the newline character from the string value
        string_value_result = string_value_result[1:]

    # encodes the string value result using the default
    # javascript encoding and returns it to the caller
    string_value_result = string_value_result.encode("utf-8")
    return string_value_result


def is_alpha(character):
    """
    Checks if the given character represents an alphabet
    letter. This is a complex operation as many comparison
    operations must be performed.

    :rtype: bool
    :return: If the given character represents an alphabet
    letter.
    """

    return (
        (character >= "a" and character <= "z")
        or (character >= "0" and character <= "9")
        or (character >= "A" and character <= "Z")
        or character == "_"
        or character == "$"
        or character == "\\"
        or (character is not None and ord(character) > 126)
    )

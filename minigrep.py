#!/usr/bin/env python3
"""By Guy Chait
minigrep.py - Search for regular expressions in local files
Usage: [python3] minigrep.py [-h] [-c | -m] regex files [files ...]
Run the script with "--help" for more usage information.
Please excuse me for having more than PEP8 E501's maximum line length of 79, I agree with Django.
"""

from argparse import ArgumentParser
from platform import platform
from re import finditer
import ctypes


class GrepFormatter:
    """This class simply formats grep results, exposing a single non-encapsulated method to call.
    There are 3 allowed formats: base (normal), color (for match highlighting), machine (for machine readability).
    """
    def __init__(self, color, machine):
        """Initialize a GrepFormatter instance."""
        if color:
            # Just in case someone uses this code not via the CLI
            if machine:
                raise ValueError('Color mode and machine mode cannot be used together.')

            # Windows needs something extra in order to display colored text
            elif platform().startswith('Windows-10'):
                self._enable_windows_colored_output()

        self._color = color
        self._machine = machine

    @staticmethod
    def _enable_windows_colored_output():
        """Enable VT100 to make ANSI colors visible in Windows."""
        kernel32 = ctypes.WinDLL('kernel32')
        h_stdout = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(h_stdout, ctypes.byref(mode))
        mode.value |= 4
        kernel32.SetConsoleMode(h_stdout, mode)

    @staticmethod
    def _base_format(file_name, line_num, line):
        """The base output format, doesn't color or provide machine-readability."""
        # Add 1 because the first index is 0 and humans or editors don't have a line 0
        return f'{file_name}, line {line_num + 1}: "{line}"'

    @staticmethod
    def _machine_format(file_name, line_num, re_matches):
        """The machine-readable output format, can produce multiple lines for multiple matches in the same line."""
        # Add 1 because the first index is 0 and humans or editors don't have a line 0 or a column 0
        # Of course we are dealing with a machine here, but it doesn't have to start indexing from 0
        return '\n'.join(f'{file_name}:{line_num + 1}:{match.start() + 1}:{match.group(0)}' for match in re_matches)

    def _color_format(self, file_name, line_num, line, re_matches):
        """The colored output format, which highlights regular expression matches in red."""
        color_start = '\033[91m'   # Red color code
        color_reset = '\033[0m'   # Default color code
        color_formatted_line = ''
        last_match_end = 0

        # Insert the color codes in the right positions
        for match in re_matches:
            start_pos, end_pos = match.span()
            color_formatted_line += line[last_match_end:start_pos]
            color_formatted_line += color_start
            color_formatted_line += line[start_pos:end_pos]
            color_formatted_line += color_reset
            last_match_end = end_pos
        color_formatted_line += line[last_match_end:]

        # Reuse the base format, using an already colored line
        return self._base_format(file_name, line_num, color_formatted_line)

    def formatter(self, file_name, line_num, line, re_matches):
        """This returns the formatted result using the format methods and the user's format choice."""
        if self._color:
            return self._color_format(file_name, line_num, line, re_matches)
        elif self._machine:
            return self._machine_format(file_name, line_num, re_matches)
        else:
            return self._base_format(file_name, line_num, line)


def get_file_lines(file_name):
    """Takes a file's name and returns its lines."""
    with open(file_name, 'r') as f:
        return f.read().splitlines()


def get_re_matches(regex, lines):
    """Searches the given lines for the given regular expression, generates the results."""
    # For each line's index and the line itself
    for line_num, line in enumerate(lines):
        # Save regular expression matches in the line
        re_matches = tuple(match for match in finditer(regex, line))

        # If the are any matches
        if re_matches:
            # Yielding provides some output almost as soon as it is found, instead of all results at the end
            yield line_num, line, re_matches


def grep(color, machine, regex, files):
    """Takes the arguments the user has provided, greps for the regular expression in the files."""
    # Initialize a grep formatter instance using the mode combination
    grep_formatter = GrepFormatter(color, machine)

    # For each file specified
    for file_name in files:
        # For each regular expression result, format and print it
        for line_match in get_re_matches(regex, get_file_lines(file_name)):
            print(grep_formatter.formatter(file_name, *line_match))


if __name__ == '__main__':
    # Initialize an argument parser
    parser = ArgumentParser()

    # Color mode and machine mode cannot be used together, bool arguments
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--color', action='store_true', help='Highlight matches. Cannot be used with --machine.')
    group.add_argument('-m', '--machine', action='store_true', help='Print in a machine-readable format.')

    # The user has to specify an expression and file(s)
    parser.add_argument('regex', help='The regular expression you want to search for.')   # str
    parser.add_argument('files', nargs='+', help='The file(s) you want to search in.')   # list

    # Do the grep the user has requested
    grep(**vars(parser.parse_args()))


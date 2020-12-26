#!/usr/bin/env python3
"""By Guy Chait
test_minigrep.py - Test that the minigrep.py script functions as expected
Usage: python[3] -m pytest [-v] test_minigrep.py
Python must be able to find minigrep.py, I suggest putting it in the same directory or using PYTHONPATH.
I'm not trying to achieve full test coverage here.
"""

from minigrep import *
from os import path
import pytest


@pytest.fixture()
def files(tmpdir):
    """Creates files in a temporary directory provided by another fixture, then returns their paths."""
    # Define some lines for the files
    samples = {
        'do': ('Hello world, yellow world!',
               'Ducks are great in doing things.',
               'The first duck to travel in time wins it all.'),

        're': ('The first thing to be called a duck has already won it all.',
               'And that is because we are all constantly traveling in time.',
               'The vast majority of duck species are not even yellow!'),

        'mi': ('This file is neither empty nor eternal.',),

        'fa': ('The stars of the show are ducks, obviously.',),

        'sol': ('',)
    }

    # Write the files, collect and return their paths
    paths = []
    for base_name, sample in samples.items():
        with open(path.join(tmpdir, base_name), 'w') as f:
            f.write('\n'.join(sample))
            paths.append(f.name)
    return paths


def test_machine_with_color():
    """Tests that color mode and machine mode cannot be used together."""
    with pytest.raises(ValueError):
        GrepFormatter(color=True, machine=True)


def test_base_formatting():
    """Tests that the base formatting works, using None as a dummy because the matches won't be needed."""
    base_formatter = GrepFormatter(color=False, machine=False)
    output = base_formatter.formatter(file_name='cool_name', line_num=42, line='This line is cool.', re_matches=None)
    assert output == 'cool_name, line 43: "This line is cool."'


@pytest.mark.parametrize('regex,line_endings', [('(a )?duck', ('do:3:11:duck', 're:1:30:a duck',
                                                               're:3:22:duck', 'fa:1:27:duck')),
                                                ('i.?s', ('do:3:6:irs', 'do:3:35:ins', 're:1:6:irs',
                                                          're:2:10:is', 're:3:31:ies', 'mi:1:3:is', 'mi:1:11:is'))])
def test_grep_machine(files, capfd, regex, line_endings):
    """This essentially tests the entire flow of the machine mode grep, except the CLI. Twice."""
    # Run the main grep function using the above parameters and a machine format, capture the results
    grep(color=False, machine=True, regex=regex, files=files)
    stdout_lines = capfd.readouterr()[0].splitlines()

    # Test that all lines expected are present and end as they should, as the start depends on the directory
    assert len(stdout_lines) == len(line_endings)
    for line, ending in zip(stdout_lines, line_endings):
        assert line.endswith(ending)

#!/usr/bin/env python

"""
Shortcut for running application tests...
automatically tests all registered application modules
takes arguments, ./test.py --help for more details
"""


import os
import sys


from django.conf import settings


def test():
    """Run test tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.app.test')

    flags = sys.argv[1:]

    if "test" in flags:
        flags.remove("test")

    command = ["test.py", "test", *flags, *settings.APP_MODULES]
    print(f'executing tests from command line with: {command}')

    from django.core.management import execute_from_command_line
    assert execute_from_command_line != None
    execute_from_command_line(command)


if __name__ == '__main__':
    test()

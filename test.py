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

    test_modules = []
    flags = sys.argv[1:]

    if "test" in flags:
        flags.remove("test")

    if "--all" in flags:
        test_modules += settings.APP_MODULES
        flags.remove("--all")
    elif "--with" in flags:
        test_modules += flags[flags.index("--with") + 1:]
        flags = flags[0:flags.index("--with")]
    else:
        test_modules += settings.APP_MODULES

    command = ["./manage.py", "test", *flags, *test_modules]
    print(f'executing tests from command line with: {command}')

    from django.core.management import execute_from_command_line
    assert execute_from_command_line != None
    execute_from_command_line(command)


if __name__ == '__main__':
    test()

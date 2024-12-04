#!/usr/bin/env python

"""
Shortcut for running application tests...
automatically tests all registered application modules
takes arguments, ./test.py --help for more details
"""


import os
import sys

from django.conf import settings
from django.core.management import execute_from_command_line


def test():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.app.test')

    execute_from_command_line([
        './manage.py', 'test',
        *sys.argv[1:],
        *settings.APP_MODULES
    ])


if __name__ == '__main__':
    test()

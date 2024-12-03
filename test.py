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
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line([sys.argv[0], "test", *sys.argv[1:], *settings.APP_MODULES])


if __name__ == '__main__':
    test()

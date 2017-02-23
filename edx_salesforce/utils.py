"""Utilities used by the edx_salesforce Django app."""

from __future__ import absolute_import, unicode_literals


def parse_user_full_name(full_name):
    """
    Parses user full name into first and last name strings.
    """
    # Remove leading/trailing whitespace
    # Condense intermediate whitespace
    full_name = ' '.join(full_name.strip().split())
    try:
        # Attempt to identity last name as right-most contiguous substring of non-space characters
        first_name, last_name = full_name.rsplit(' ', 1)
    except ValueError:
        first_name = None
        last_name = full_name
    return first_name, last_name

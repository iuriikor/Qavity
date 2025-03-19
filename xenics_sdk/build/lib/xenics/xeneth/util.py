"""
util.py

Utility functions and classes.
"""

import logging

from xenics.xeneth.errors import XenethAPIException

_log = logging.getLogger("xenics.xeneth")
_log.addHandler(logging.NullHandler())
_log.propagate = False

def handle_c_call(func):
    """
    Function to handle C API calls which return an ErrorCode.
    If the function returns a non-zero value, a XenethAPIException is raised containing the returned error code.
    
    :param func: C API function
    """
    result = func()

    if result!= 0:
        raise XenethAPIException(result)

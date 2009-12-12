#!/usr/bin/env python
#
#  mcxPersistentExceptions.py
#  mcxPyBot
#
#  Created by Toni Uebernickel on 11/17/08.
#  Copyright (c) 2008 Whitestarprogramming GbR. All rights reserved.
#

"""mcxPersistentExceptions -- Exceptions for mcxPersistent module.

@author: Toni Uebernickel
@organization: Whitestarprogramming GbR
@copyright: 2008-2009 Whitestarprogramming GbR. All rights reserved.
@contact: tuebernickel@whitestarprogramming.de
"""

class mcxPersistentException(Exception):
    """Common base class for all mcxPersistent exceptions."""
    def __init__(self, value):
        self.parameter = value
        """The error message of the exception."""

    def __str__(self):
        return repr(self.parameter)

class ConnectionException(mcxPersistentException):
    """Exception for connection problems on mcxPersistent."""
    pass

class InvalidUserException(mcxPersistentException):
    """Exception for invalid user requests."""
    pass

class NoDatabaseException(mcxPersistentException):
    """Exception for requests on a mcxPersistent that's not reachable."""
    pass
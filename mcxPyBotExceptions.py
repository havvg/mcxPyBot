#!/usr/bin/env python
#
#  mcxPyBotExceptions.py
#  mcxPyBot
#
#  Created by Toni Uebernickel on 11/21/08.
#  Copyright (c) 2008 Whitestarprogramming GbR. All rights reserved.
#

"""mcxPyBotExceptions -- Exceptions for mcxPyBot module.

@author: Toni Uebernickel
@organization: Whitestarprogramming GbR
@copyright: 2008-2009 Whitestarprogramming GbR. All rights reserved.
@contact: tuebernickel@whitestarprogramming.de
"""

class mcxPyBotException(Exception):
    """Common base class for all mcxPyBot exceptions."""
    def __init__(self, value):
        self.parameter = value
        """The error message of the exception."""

    def __str__(self):
        return repr(self.parameter)

class ConfigurationException(mcxPyBotException):
    """Exception for configuration errors detected on runtime of mcxPyBot."""
    pass

class InvalidArgumentException(mcxPyBotException):
    """Exception for invalid arguments given to methods."""
    pass
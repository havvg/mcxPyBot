#!/usr/bin/env python
#
#  mcxPyBotThreads.py
#  mcxPyBot
#
#  Created by Toni Uebernickel on 12/22/08.
#  Copyright (c) 2008 Whitestarprogramming GbR. All rights reserved.
#

"""mcxPyBotThreadsConstants -- Constants for mcxPyBotThreads module.

@author: Toni Uebernickel
@organization: Whitestarprogramming GbR
@copyright: 2008-2009 Whitestarprogramming GbR. All rights reserved.
@contact: tuebernickel@whitestarprogramming.de

@var CONFIG_CHECKUPDATE_INTERVAL: Amount of seconds the update check will wait between checks.

@var UPDATE_GROUP_UPDATEMESSAGE: Group ID of updateMessage
@var UPDATE_MESSAGE_UPDATEMESSAGE: Message sent to the channel if a new updateMessage is available.
"""

# configuration
CONFIG_CHECKUPDATE_INTERVAL = 15

# group configuration for all update events
UPDATE_GROUP_UPDATEMESSAGE = 1

# messages on updates
UPDATE_MESSAGE_UPDATEMESSAGE = "Ein neues Update wurde bereitgestellt."
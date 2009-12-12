#!/usr/bin/env python
#
#  mcxPyBotConnectionPoolerConstants.py
#  mcxPyBot
#
#  Created by Toni Uebernickel on 12/29/08.
#  Copyright (c) 2008 Whitestarprogramming GbR. All rights reserved.
#

"""mcxPyBotConnectionPoolerConstants -- Constants for mcxPyBotConnectionPooler module.

@author: Toni Uebernickel
@organization: Whitestarprogramming GbR
@copyright: 2008-2009 Whitestarprogramming GbR. All rights reserved.
@contact: tuebernickel@whitestarprogramming.de

@var DCC_CONNECTION_QUEUED: Message sent to user, the DCCConnection was appended to the poolers queue.
@var AMOUNT_OF_THREADS: Amount of threads the connection pooler will create.
"""

DCC_CONNECTION_QUEUED = "Der Verbindungsaufbau wurde gestartet."

AMOUNT_OF_THREADS = 3
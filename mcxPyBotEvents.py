#!/usr/bin/env python
#
#  mcxPyBotEvents.py
#  mcxPyBot
#
#  Created by Toni Uebernickel on 12/12/08.
#  Copyright (c) 2008 Whitestarprogramming GbR. All rights reserved.
#

"""mcxPyBotEvents -- Events used by mcxPyBot and mcxPyBotThreads for inter-process communication.

@author: Toni Uebernickel
@organization: Whitestarprogramming GbR
@copyright: 2008-2009 Whitestarprogramming GbR. All rights reserved.
@contact: tuebernickel@whitestarprogramming.de

@var EVENT_MCX_DATABASE_LOST: Event that will be fired when database connection from mcxPyBot to mcxDatabase will be lost.
@var EVENT_MCX_DATABASE_RECOVERED: Event that will be fired when the database connection from mcxPyBot to mcxDatabase will be recovered after any lose.
@var EVENT_MCX_UPDATES_AVAILABLE: Event that will be fired when any update is available for mcxPyBot to deliver.
"""

from threading import Event

EVENT_MCX_DATABASE_LOST = Event();
EVENT_MCX_DATABASE_RECOVERED = Event();
EVENT_MCX_UPDATES_AVAILABLE = Event();
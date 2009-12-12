#!/usr/bin/env python
#
#  mcxPyBotConnectionPooler.py
#  mcxPyBot
#
#  Created by Toni Uebernickel on 12/29/08.
#  Copyright (c) 2008 Whitestarprogramming GbR. All rights reserved.
#

"""mcxPyBotConnectionPooler -- Connection pooling module of mcxPyBot.

This module pools DCCConnection of mcxPyBot.

@author: Toni Uebernickel
@organization: Whitestarprogramming GbR
@copyright: 2008-2009 Whitestarprogramming GbR. All rights reserved.
@contact: tuebernickel@whitestarprogramming.de

@var DCCQueue: Queue.queue with tuple of (address, port) each entry.
"""

# base libs
from Queue import *
from threading import Thread

# mcxPyBot imports
from mcxPyBotConnectionPoolerConstants import CONFIG_AMOUNT_OF_THREADS

DCCQueue = Queue.queue

class mcxPyBotConnectionThread(Thread):
    """
        A thread that handles queued DCCConnection.
    """

    def run(self):
        pass

class mcxPyBotConnectionPooler():
    """
        A class pooling DCCConnection that are requested within mcxPyBot.
    """

    def __init__(self):
        self.threadPool = []
        """Pool (list) of threads that will be created and used by the ConnectionPooler"""

        # setup threads
        i = 0
        while i < AMOUNT_OF_THREADS:
            i = i + 1

            # start thread
            connectionThread = mcxPyBotConnectionThread()
            connectionThread.setDaemon(True)
            connectionThread.start()

            self.threadPool.append(connectionThread)
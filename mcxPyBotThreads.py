#!/usr/bin/env python
#
#  mcxPyBotThreads.py
#  mcxPyBot
#
#  Created by Toni Uebernickel on 12/18/08.
#  Copyright (c) 2008 Whitestarprogramming GbR. All rights reserved.
#

"""mcxPyBotThreads -- Multithreading module of mcxPyBot.

@author: Toni Uebernickel
@organization: Whitestarprogramming GbR
@copyright: 2008-2009 Whitestarprogramming GbR. All rights reserved.
@contact: tuebernickel@whitestarprogramming.de
"""

# needed libs
from threading import Thread
from datetime import datetime
from time import sleep
import socket

# mcxPyBot imports
from mcxPyBotThreadsConstants import *
from mcxPersistentConstants import CONFIG_UPDATE_MESSAGE_TYPE
from mcxPersistentExceptions import ConnectionException
from mcxPersistent import mcxPersistent
from mcxPyBotExceptions import InvalidArgumentException
from mcxPyBotConstants import INVALID_BOT_OBJECT, DATABASE_SERVER_NOT_AVAILABLE, DATABASE_CONNECTION_INTERRUPTED, DATE_FORMAT_STRING
from mcxPyBotEvents import EVENT_MCX_DATABASE_LOST, EVENT_MCX_DATABASE_RECOVERED, EVENT_MCX_UPDATES_AVAILABLE

class mcxPyBotThread(Thread):
    """
        A simple thread starting the mcxPyBot.

        @todo 0.7b: add isinstance check of mcxPyBot object (isn't working in 0.6b)
    """
    def __init__(self, mcxpybot):
        """
            @type mcxpybot: mcxPyBot
            @param mcxpybot: an object of the mcxPyBot class that will be started

            @raise InvalidArgumentException: If the given object is no instance of the mcxPyBot class (INVALID_BOT_OBJECT).
        """
        #if not isinstance(mcxpybot, mcxPyBot):
        #    raise InvalidArgumentException(INVALID_BOT_OBJECT)
        #else:
        self.mcxPyBot = mcxpybot
        """The reference to the mcxPyBot object, that's running."""
        Thread.__init__(self)

    def run(self):
        try:
            print 'mcxPyBot starting ..'
            self.mcxPyBot.start()

        except Exception, (error):
            # clear last line of terminal or other output
            print error
            # shutdown the bot correctly
            print 'mcxPyBot initiates self destruct sequence ..'
            self.mcxPyBot.die()

class mcxDatabaseThread(Thread):
    """
        Base thread class for requests on the mcxPersistent

        @summary: This thread only initiates database connection and does nothing more.
    """

    def __init__(self, dbhost, dbuser, dbpass, dbname):
        # get mcxPersistent instance
        self.persistent = mcxPersistent(dbhost, dbuser, dbpass, dbname)
        """The reference to the mcxPersistent object."""

        # connect to database
        self.persistent.connect()

        # initialise thread
        Thread.__init__(self)

    def run(self):
        """This run method is empty."""
        pass


class mcxRecoverDBThread(mcxDatabaseThread):
    """Thread for recovering database connection."""

    def run(self):
        """
            @summary: This thread is waiting for EVENT_MCX_DATABASE_LOST and if fired, retrying to connect to the databse.
                If connection could be established, EVENT_MCX_DATABASE_RECOVERED will be fired.

            @note: EVENT_MCX_DATABASE_LOST xor EVENT_MCX_DATABASE_RECOVERED
        """

        print "%s waiting for database lose .." % self.getName()

        # wait for the database lost event
        EVENT_MCX_DATABASE_LOST.wait()

        print "%s executing recovery .." % self.getName()

        if self.persistent.connected():
            self.persistent.disconnect()

        # event was fired
        # make sure everyone knows the database has not been recovered yet
        EVENT_MCX_DATABASE_RECOVERED.clear()

        # loop until database is available
        while not EVENT_MCX_DATABASE_RECOVERED.isSet():
            try:
                # connect
                self.persistent.connect()
                # ping the persistent
                if self.persistent.ping():
                    # on pong database is available

                    # database is not lost anymore
                    EVENT_MCX_DATABASE_LOST.clear()

                    # database connection finally re-established
                    # fire event, database has been recovered
                    EVENT_MCX_DATABASE_RECOVERED.set()

                    print "%s recovered database connection .." % self.getName()

                self.persistent.disconnect()
            except:
                # try until working
                pass

        # at the end.. "restart" thread
        self.run()

class mcxCheckUpdatesThread(mcxDatabaseThread):
    """
        A thread checking for updates and firing event if update is available.

        @todo 0.7b: add reflection to __check() method
    """

    def __init__(self, dbhost, dbuser, dbpass, dbname):
        # reset event
        if EVENT_MCX_UPDATES_AVAILABLE.isSet():
            EVENT_MCX_UPDATES_AVAILABLE.clear()

        self.__cursor = None
        """The cursor of MySQLdb library retrieved from the mcxPersistent object."""

        self.__updates = {}
        """All updates, that are available since last time. Defaults to an empty dict."""

        self.__getUpdateMethods()

        # initiate base class
        mcxDatabaseThread.__init__(self, dbhost, dbuser, dbpass, dbname)

    def run(self):
        """
            @requires: self.isDaemon() == True

            @summary: This thread serves forever.
                As long as EVENT_MCX_UPDATES_AVAILABLE is not set this thread will look every CONFIG_CHECKUPDATE_INTERVAL seconds for new updates until found.

                If updates were found, it will fire EVENT_MCX_UPDATES_AVAILABLE and wait until this event becomes cleared.
        """

        # serve forever
        while self.isDaemon():
            # and event flag not cleared by now
            if not EVENT_MCX_UPDATES_AVAILABLE.isSet():
                # ensure we do not operate on an invalid object
                self.__cursor = None
                self.__clearUpdates()

                try:
                    # make sure connection is established
                    self.persistent.connect()

                    # check for updates only, if connection is established
                    if self.persistent.connected():
                        self.__cursor = self.persistent.getCursor()
                        # check for updates
                        self.__checkForUpdates()
                        # disconnect properly
                        self.persistent.disconnect()
                    else:
                        raise ConnectionException(DATABASE_SERVER_NOT_AVAILABLE)

                # no database available
                # let's handle the recover thread and wait for it
                except ConnectionException, (error):
                    print "%s fired EVENT_MCX_DATABASE_LOST caused by: %s" % (self.getName(), error)
                    # handle events
                    EVENT_MCX_DATABASE_RECOVERED.clear()
                    EVENT_MCX_DATABASE_LOST.set()
                    EVENT_MCX_DATABASE_RECOVERED.wait()

                # repeat this in a given interval and sleep in the meantime :)
                sleep(CONFIG_CHECKUPDATE_INTERVAL)

    def getUpdates(self):
        """
            Returns all available updates.

            @rtype: dict
            @return: All available updates that have been added until last __clearUpdates().
        """
        return self.__updates

    def __clearUpdates(self):
        """Clear all found updates."""
        self.__updates = {}

    def __addUpdate(self, group, updateMsg):
        """
            Add a new update to the current updates.

            @type group: string
            @param group: The group (key of dict) were the update message is held.

            @type updateMsg: string
            @param updateMsg: The actual update message that will be added to the given group.
        """
        # convert to string
        group = str(group)

        # make sure the group exists before adding updateMsg to this group
        if not hasattr(self.__updates, group):
            self.__updates[group] = []

        # add update to group
        self.__updates[group].append(updateMsg)

    def __getUpdateMethods(self):
        """
            Get a list of all update methods.

            @summary: Fills up internal list for all methods marked as update methods using @update as doc field.
                '@update: True' will mark the method as an update method.
        """
        # create methodslist
        self.__updateMethods = []

        # traverse over all methods of instance
        for method in dir(self):
            # be sure, it's a method, no attribute
            # and it's a callable method
            if callable(getattr(self, method)):
                # if method is marked as update function
                if str(getattr(self, method).__doc__).find('@update: True') > -1:
                    self.__updateMethods.append(method)

    def __checkForUpdates(self):
        """The base method that's actually checking for new updates by running all marked methods."""

        if len(self.__updateMethods):
            updatesAvailable = False
            for method in self.__updateMethods:
                # get new cursor
                self.__cursor = self.persistent.getCursor()

                # execute check update method
                updatesAvailable = updatesAvailable or getattr(self, method)()

                # close and reset cursor
                self.__cursor.close()
                self.__cursor = None

            if updatesAvailable:
                # needs to be cleared by another thread
                EVENT_MCX_UPDATES_AVAILABLE.set()

    def __checkUpdateMessage(self):
        """
            Check for a new update message (system message 'Update').

            @update: True
        """

        checkForMessageSQL = "\
                    SELECT MAX(mdate) \
                    FROM message_system \
                    WHERE mtype = %s"

        self.__cursor.execute(checkForMessageSQL, CONFIG_UPDATE_MESSAGE_TYPE)
        fetchedRow = self.__cursor.fetchone()

        if len(fetchedRow) == 1:
            # no message time saved
            if not hasattr(self, '_mcxCheckUpdatesThread__updateMessageTime'):
                # save it
                self.__updateMessageTime = fetchedRow[0]
                # it's the first run, so this is no new update
                return False
            # actual new update given
            else:
                # get a timedelta object between last saved updatemsg and new one
                dateDiff = fetchedRow[0] - self.__updateMessageTime
                # if delta greater than 0
                # mark update available
                if dateDiff.seconds > 0:
                    self.__updateMessageTime = fetchedRow[0]
                    self.__addUpdate(UPDATE_GROUP_UPDATEMESSAGE, UPDATE_MESSAGE_UPDATEMESSAGE)
                    return True
                # otherwise no update is given
                else:
                    return False
        else:
            return False

class mcxMessageBridgeThread(Thread):
    """
        A thread bridging messages received via socket connection to the IRC.
        
        @todo 0.7b: authentication and authorization system
    """
    def __init__(self, callBack):
        self.__setupSocket()
        self.__callback = callBack
        Thread.__init__(self)

    def __setupSocket(self):
        self.__host = ''
        self.__port = 1338
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.bind((self.__host, self.__port))
        self.__socket.listen(1)
        
    def getSocket(self):
        return self.__socket

    def run(self):
        while self.isDaemon():
            sock, addr = self.getSocket().accept()
            socketFile = sock.makefile('rw', 0)

            self.__callback(socketFile.readline().strip())

            socketFile.close()
            sock.close()
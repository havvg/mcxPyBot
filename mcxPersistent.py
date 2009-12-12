#!/usr/bin/env python
#
#  mcxPersistent.py
#  mcxPyBot
#
#  Created by Toni Uebernickel on 11/17/08.
#  Copyright (c) 2008 Whitestarprogramming GbR. All rights reserved.
#

"""mcxPersistent -- Database operation module of mcxPyBot.

@author: Toni Uebernickel
@organization: Whitestarprogramming GbR
@copyright: 2008-2009 Whitestarprogramming GbR. All rights reserved.
@contact: tuebernickel@whitestarprogramming.de
"""

# needed libs
import MySQLdb

# mcxPyBot imports
from mcxPersistentConstants import DATABASE_HOST, DATABASE_USER, DATABASE_PASS, DATABASE_NAME
from mcxPersistentExceptions import NoDatabaseException, ConnectionException

class mcxDatabase:
    """
        A database request wrapper for Megacomplex
        Wraps certain commands into SQL Queries, that are sent to a database (mcxPersistent).
    """
    def __init__(self):
        self.__persistent = mcxPersistent(DATABASE_HOST, DATABASE_USER, DATABASE_PASS, DATABASE_NAME)
        """The reference to the mcxPersistent object."""

    def connected(self):
        """
            Returns connection state of mcxPersistent.

            @rtype: bool
            @return: MySQLdb.connected() - Is the current connection established (True) or not (False)?
        """
        return self.__persistent.connected()

    def __preQuery(self):
        """An internal method retrieving new cursor from MySQLdb after connecting to the database."""
        try:
            self.__persistent.connect()
            self.__cursor = self.__persistent.getCursor()
        except Exception, (error):
            raise NoDatabaseException(str(error))

    def __postQuery(self):
        """Disconnect from database server."""
        try:
            self.__cursor.close()
            self.__persistent.disconnect()
        except Exception, (error):
            raise NoDatabaseException(str(error))

    def getMySQLVersion(self):
        """
            returns the complete MySQL Server version string

            @rtype: string
            @return: version of mysql server or empty string, if not connected
        """
        self.__preQuery()

        self.__cursor.execute("SELECT VERSION();")
        MySQLVersion = self.__cursor.fetchone()[0]

        self.__postQuery()

        return MySQLVersion

    def pingDatabase(self):
        """
            pings the mcxPersistent

            @rtype: bool
            @return: Ping result (True = Pong)
        """
        self.__preQuery()

        ping = self.__persistent.connected()

        self.__postQuery()

        return ping

    def getUserIdByBotKey(self, botkey):
        """
            get the user id for a given botkey

            @type botkey: string
            @param botkey: an authentification key for the bot

            @rtype: int
            @return: userid for the given botkey
        """
        getUserId = "\
            SELECT IFNULL(uid, 0) \
            FROM settings_users \
            WHERE (sid = %s) \
            AND (val = %s)"

        self.__preQuery()
        if self.__cursor.execute(getUserId, (CONFIG_USER_SETTING_ID_BOTKEY, botkey)):
            UserId = int(self.__cursor.fetchone()[0])
            self.__postQuery()
        else:
            UserId = 0

        return UserId

    def getLatestMessage(self, UserId):
        """
            get the latest message sent to an user

            @type UserId: int
            @param UserId: id of an user

            @rtype: dict
            @return: dict of message {"from": nick of user, "subject": subject of message, "body": content of message, "created": date of creation}
        """
        try:
            getMessage = "\
                SELECT \
                    (SELECT name FROM base WHERE id = m.sender) AS sender, \
                    short_text, \
                    long_text, \
                    mdate \
                FROM message_usertouser AS m \
                WHERE recipient = %s \
                ORDER BY mdate DESC \
                LIMIT 1"

            self.__preQuery()
            if self.__cursor.execute(getMessage, int(UserId)):
                fetchedRow = self.__cursor.fetchone()
                if len(fetchedRow) == 4:
                    MessageDict = {"from": fetchedRow[0], "subject": fetchedRow[1], "body": fetchedRow[2], "created": fetchedRow[3]}
                # no message sent, yet
                else:
                    MessageDict = {}
                self.__postQuery()
            # query failed
            else:
                MessageDict = {}
        except NoDatabaseException:
            MessageDict = {}

        return MessageDict

class mcxPersistent:
    """
        Persistent class for retrieving data from MegaCompleX.

        @note: using MySQLdb
    """
    def __init__(self, dbhost, dbuser, dbpass, dbname):
        """
            constructor connects to MySQL database

            @type dbhost: string
            @param dbhost: any hostname, ip address or ip address with port

            @type dbuser: string
            @param dbuser: database user to login

            @type dbpass: string
            @param dbpass: the password for this dbuser

            @type dbname: string
            @param dbname: name of the database to connect to

            @raise ConnectionException: If no database connection could be established
        """
        # save connection information into dict
        self.__db = {"dbhost": dbhost,
                     "dbuser": dbuser,
                     "dbpass": dbpass,
                     "dbname": dbname}
        """Dict saving all database information."""

        self.__connected = False
        """Flag if connection status."""

        try:
            self.connect()
        except ConnectionException, (e):
            self.__connected = False

    def __del__(self):
        """
            destructor disconnects all open connections before deleting object
        """
        if self.__connected:
            self.disconnect()

    def ping(self):
        """
            Ping the database.

            @rtype: bool
        """
        return self.__connected

    def connected(self):
        """
            Is client connected to the database server?

            @rtype: bool
        """
        return self.__connected

    def getCursor(self):
        """
            Retrieve the MySQLdb cursor object.

            @rtype: MySQLDb.cursor
        """
        return self.__connection.cursor()

    def connect(self):
        """Connect to the database server."""
        if not self.__connected:
            try:
                self.__connection = MySQLdb.connect(self.__db['dbhost'], self.__db['dbuser'], self.__db['dbpass'], self.__db['dbname'])
                self.__connected = True
            except Exception, (error):
                self.__connected = False
                raise ConnectionException('Could not connect to database.')

    def disconnect(self):
        """Disconnect from the database server."""
        if self.__connected:
            self.getCursor().close()
            self.__connection.close
            self.__connected = False
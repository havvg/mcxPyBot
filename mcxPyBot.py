#!/usr/bin/env python
#
#  mcxPyBot.py
#  mcxPyBot
#
#  Created by Toni Uebernickel on 11/17/08.
#  Copyright (c) 2008 Whitestarprogramming GbR. All rights reserved.
#

"""mcxPyBot -- Megacomplex Python Bot.

The base class mcxPyBot and the __main__ programm.

@author: Toni Uebernickel
@organization: Whitestarprogramming GbR
@copyright: 2008-2009 Whitestarprogramming GbR. All rights reserved.
@contact: tuebernickel@whitestarprogramming.de
"""

# irc libs
from datetime import datetime
from random import randint
from threading import Thread
from time import time

from ircbot import SingleServerIRCBot
from irclib import DCCConnection
from irclib import DCCConnectionError
from irclib import ServerConnection
from irclib import ip_numstr_to_quad
from irclib import irc_lower
from irclib import is_channel
from irclib import nm_to_n
from mcxPersistent import *
from mcxPersistentConstants import DATABASE_HOST
from mcxPersistentConstants import DATABASE_NAME
from mcxPersistentConstants import DATABASE_PASS
from mcxPersistentConstants import DATABASE_USER
from mcxPersistentExceptions import *
#from mcxPyBotConnectionPooler import DCCQueue
#from mcxPyBotConnectionPooler import mcxPyBotConnectionPooler
#from mcxPyBotConnectionPoolerConstants import *
from mcxPyBotConstants import *
from mcxPyBotEvents import *
from mcxPyBotExceptions import *
from mcxPyBotThreads import mcxCheckUpdatesThread
from mcxPyBotThreads import mcxPyBotThread
from mcxPyBotThreads import mcxRecoverDBThread
from mcxPyBotThreads import mcxMessageBridgeThread

class mcxPyBot(SingleServerIRCBot):
    """
        The Megacomplex Python IRC Bot class.

        @todo 0.9b: add admin command type
        @version: 0.6b
    """

    def __init__(self, channel, nickname, password, server, port = 6667, dbcon = False):
        """
            mcxPyBot constructor initialises mcxDatabase connection and adds command handlers.

            @type channel: string
            @param channel: name of the IRC channel to join

            @type nickname: string
            @param nickname: the nickname the bot use

            @type password: string
            @param password: the password for the bots nickname

            @type server: string
            @param server: any type of IRC server address

            @type port: number
            @param port: the port to connect on the IRC server

            @type dbcon: mcxDatabase
            @param dbcon: enable mcxDatabase features
        """
        # IRC connection
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)

        # register event handler for all events
        self.ircobj.add_global_handler('all_events', getattr(self, 'on_event'), -10)

        self.channel = channel
        """The channel in which the bot will serve."""

        self.__password = password
        """The password used to identify with nick services."""

        self.__IpToUser = {}
        """A dict which stores IP (dcc) to user (mcx.user.id) relations."""

        self.__quitmsgs = []
        """A list of available quit messages used by the bot when quitting from a server."""

        self.__initQuitMsgPool()

        self.__commandHandlers = {}
        """Dict saving all command handlers."""

        # mcxDatbase
        self.__database = dbcon
        """A reference to a mcxDatabase object."""

        if isinstance(self.__database, mcxDatabase):
            self.__databaseAvailable = self.__database.connected()
            """Flag whether mcxDatabase is reachable."""

            # if database connection could be established
            if self.__databaseAvailable:
                EVENT_MCX_DATABASE_LOST.clear()
                EVENT_MCX_DATABASE_RECOVERED.set()
        else:
            self.__databaseAvailable = False

        # register all available command types
        self.__setupCommandHandlerTypes()

        # add new command handlers here
        # query commands
        self.__addCommandHandler('die', 'query')

        # channel commands
        self.__addCommandHandler('greet', 'channel')
        self.__addCommandHandler('pingDataBase', 'channel', True)
        self.__addCommandHandler('getMySQLVersion', 'channel', True)
        self.__addCommandHandler('getTestUserByBotKey', 'channel', True)

        # user commands
        self.__addCommandHandler('auth', 'not_authed_dcc', True)

        # registered user commands
        self.__addCommandHandler('getLatestMessage', 'authed_dcc', True)

        # admin commands
        # not implemented yet

    def __initQuitMsgPool(self):
        """
            initialize some quit message and save them into a list by filling self.__quitmsgs
        """
        self.__quitmsgs.append("Infektion festgestellt... leite Quarantaenemassnahmen ein... trenne aktive Verbindung")
        

    def getRandomQuitMsg(self):
        """
            get any random quit message that was initialized by __initQuitMsgPool()

            @rtype: string
            @return: quit message
        """
        return self.__quitmsgs[randint(0, len(self.__quitmsgs)-1)]

    def get_version(self):
        """
            get the version string of this class

            @rtype: string
            @return: version string
        """
        return "mcxPyBot.py by Toni Uebernickel <tuebernickel@whitestarprogramming.de> using ircbot based on python-irclib"

    def getFormattedDate(self, dt):
        """
            returns a formatted date string

            @summary: returns either the formatted datestring defined by DATE_FORMAT_STRING or it defaults to '%Y-%m-%d %H:%M:%S'.

            @type dt: datetime
            @param dt: datetime object to format

            @rtype: string
            @return: formatted date string
        """
        if DATE_FORMAT_STRING == '':
            return time.strftime('%Y-%m-%d %H:%M:%S', dt.timetuple())
        else:
            return time.strftime(DATE_FORMAT_STRING, dt.timetuple())

    #{ registered commands

    def cmd_channel_greet(self, c, e):
        """
            simple example command greeting the executing user

            @type c: ServerConnection
            @param c: connection object to the server

            @type e: Event
            @param e: event object that was fired
        """
        c.privmsg(e.target(), 'Greetings %s!' % nm_to_n(e.source()))

    def cmd_channel_getMySQLVersion(self, c, e):
        """
            simple example command using mcxDatabase

            @type c: ServerConnection
            @param c: connection object to the server

            @type e: Event
            @param e: event object that was fired
        """
        c.privmsg(e.target(), 'MySQL Server Version: %s' % self.__database.getMySQLVersion())

    def cmd_channel_pingDataBase(self, c, e):
        """
            ping the mcxDatabase

            @type c: ServerConnection
            @param c: connection object to the server

            @type e: Event
            @param e: event object that was fired
        """
        c.privmsg(e.target(), 'Ping: %s' % self.__database.pingDatabase())

    def cmd_channel_getTestUserByBotKey(self, c, e):
        """For testing purpose only, will be erased in future versions."""
        BotKey = self.getParameterListByEvent(e)[0]
        UserId = int(self.__database.getUserIdByBotKey(BotKey))
        if UserId:
            c.privmsg(e.target(), 'UserId for Botkey: %s' % user)
        else:
            c.privmsg(e.target(), 'Not Found: User')

    def cmd_query_die(self, c, e):
        """
            command to let the bot quit and end the program

            @type c: ServerConnection
            @param c: connection object to the server

            @type e: Event
            @param e: event object that was fired
        """
        self.die(self.getRandomQuitMsg())

    def cmd_not_authed_dcc_auth(self, c, e):
        """
            auth command, a user may authenticate itself by sending a authentification key

            @type c: DCCConnection
            @param c: connection object to the server

            @type e: Event
            @param e: event object that was fired
        """
        UserId = self.__authUser(c, e)

        if int(UserId) > 0:
            self.__IpToUser[self.getIpStringByDCCConnection(c)]['auth'] = 'authed_dcc'
            c.privmsg(AUTH_USER_SUCCESS_BY_BOTKEY)
        else:
            c.privmsg(AUTH_USER_FAILED)

    def cmd_authed_dcc_getLatestMessage(self, c, e):
        """
            get the lastest message for the user

            @type c: DCCConnection
            @param c: connection object to the server

            @type e: Event
            @param e: event object that was fired
        """
        MessageDict = self.__database.getLatestMessage(self.__getUserIdByDCCConnection(c))
        if MessageDict.has_key('from'):
            created = self.getFormattedDate(MessageDict['created'])
            c.privmsg(LATEST_MESSAGE_INTRO)
            c.privmsg(LATEST_MESSAGE_FROM % (MessageDict['from'], created))
            c.privmsg(LATEST_MESSAGE_SUBJECT % MessageDict['subject'])
            c.privmsg(LATEST_MESSAGE_BODY % MessageDict['body'])
        else:
            c.privmsg(NO_LATEST_MESSAGE)

    #} end registered commands

    #{ event handlers

    def on_nicknameinuse(self, c, e):
        """
            commands executed after connected to the server
            triggered if the chosen nickname on construction is already in use

            @type c: ServerConnection
            @param c: connection object to the server

            @type e: Event
            @param e: event object that was fired
        """
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        """
            commands executed after connected to the server
            triggered immediately after connection has been established

            @type c: ServerConnection
            @param c: connection object to the server

            @type e: Event
            @param e: event object that was fired
        """
        c.privmsg('NICKSERV', 'GHOST %s %s' % (self._nickname, self.__password))
        c.nick(self._nickname)
        c.privmsg('NICKSERV', 'IDENTIFY %s' % self.__password)
        c.join(self.channel)

    def on_privmsg(self, c, e):
        """
            commands executed when the bot received a private message
            forwards the command and the event to self.do_command()

            @type c: ServerConnection
            @param c: connection object to the server

            @type e: Event
            @param e: event object that was fired
        """
        self.do_command(e.arguments()[0], c, e)

    def on_pubmsg(self, c, e):
        """
            commands executed when the bot received a public message on a channel
            extracts command and forward it and the event to self.do_command()
            if no command prefix (bot not addressed) is find, nothing happens

            @type c: ServerConnection
            @param c: connection object to the server

            @type e: Event
            @param e: event object that was fired
        """
        args = e.arguments()[0].split(",", 1)
        sender = args[0]

        if len(args) > 1 and irc_lower(sender) == irc_lower(self.connection.get_nickname()):
            self.do_command(self.getCommandByEvent(e), c, e)

    def on_dccmsg(self, c, e):
        """
            commands executed when the bot received a dcc message
            currently does nothing

            @type c: DCCConnection
            @param c: connection object to the server

            @type e: Event
            @param e: event object that was fired
        """

        args = e.arguments()[0].split(" ", 1)
        if len(args) > 0:
            self.do_command(args[0], c, e)

    def on_dccchat(self, c, e):
        """
            commands executed when the bot received a request for a new dcc chat
            currently does nothing

            @type c: ServerConnection
            @param c: connection object to the server

            @type e: Event
            @param e: event object that was fired
        """

        self.__privMsg(c, e, FEATURE_DISABLED)
        return

        # check parameters
        if len(e.arguments()) != 2:
            return

        # retrieve parameters
        args = e.arguments()[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return

            DCCQueue.append((address, port))
            self.__privMsg(c, e, DCC_CONNECTION_QUEUED)

            #try:
            #    con = self.dcc_connect(address, port)
            #    self.__IpToUser[self.getIpStringByDCCConnection(con)] = {"auth": NOT_AUTHED, "userid": 0}
            #except DCCConnectionError, error:
            #    print 'DCC Connection failed: %s:%s' % (address, port)
            #    print error

    def dcc_connect(address, port):
        try:
            con = SimpleIRCClient.dcc_connect(self, address, port)
            self.__IpToUser[self.getIpStringByDCCConnection(con)] = {"auth": NOT_AUTHED, "userid": 0}
            return con

        except DCCConnectionError, error:
            print 'DCC Connection failed: %s:%s' % (address, port)
            print error

    def on_event(self, c, e):
        """
            method that's executed on every event

            @type c: ServerConnection
            @param c: connection object to the server

            @type e: Event
            @param e: event object that was fired
        """

        # any updates available?
        if EVENT_MCX_UPDATES_AVAILABLE.isSet():
            # gather all updates
            availableUpdates = mcxUpdateThread.getUpdates()
            # for each update group
            for updateGroupId, updateMessageList in availableUpdates.iteritems():
                # and each message within each group
                for updateMessage in updateMessageList:
                    # send the message
                    self.connection.privmsg(self.channel, updateMessage)

            # after all reset event
            EVENT_MCX_UPDATES_AVAILABLE.clear()

    #} end event handlers

    #{ auth functions

    def __authUser(self, c, e):
        """
            auth a user to a DCCConnection

            @type c: DCCConnection
            @param c: DCCConnection on which the auth is processed

            @type e: Event
            @param e: event object that was fired

            @rtype: int
            @return: userid that has been authed, zero on failure
        """
        try:
            UserId = self.__database.getUserIdByBotKey(self.getParameterListByEvent(e)[0]);
            self.__IpToUser[self.getIpStringByDCCConnection(c)]['userid'] = int(UserId)
            return UserId
        except IndexError:
            return 0;

    def __getUserIdByDCCConnection(self, c):
        """
            returns the userid of the connected user on a DCCConnection

            @type c: DCCConnection
            @param c: the dcc connection on which the user id will be retrieved

            @rtype: int
            @return: user id or NOT_AUTHED constant
        """
        try:
            UserId = self.__IpToUser[self.getIpStringByDCCConnection(c)]['userid']
            if UserId > 0:
                return UserId
            else:
                return NOT_AUTHED
        except KeyError:
            return NOT_AUTHED

    #} end auth functions

    #{ command handling functions

    def getParameterListByEvent(self, e):
        """
            @type e: Event
            @param e: event object to retrieve command from

            @rtype: list
            @return: list of parameters that was sent on this event
        """
        # on ServerConnection
        try:
            return e.arguments()[0].split(",", 1)[1].strip().split(" ", 1)[1].strip().split(" ")
        except IndexError:
            # on DCCConnection
            try:
                return e.arguments()[0].split(" ", 1)[1].strip().split(" ")
            except IndexError:
                return []

    def getCommandByEvent(self, e):
        """
            @type e: Event
            @param e: event object to retrieve command from

            @rtype: string
            @return: command that was sent on this event
        """
        try:
            return e.arguments()[0].split(",", 1)[1].strip().split(" ", 1)[0].strip()
        except IndexError, (e):
            return ""

    def getIpStringByDCCConnection(self, c):
        """
            @type c: DCCConnection
            @param c: the dcc connection from which the ip:port string will be extracted

            @rtype: string
            @return: a formatted string like "127.0.0.1:67123" of IP:Port
        """
        return str(c.peeraddress)

    def do_command(self, command, c, e):
        """
            execute the command given by an event

            @type command: string
            @param command: name of the command to execute

            @type c: Connection
            @param c: either DCCConnection or ServerConnection

            @type e: Event
            @param e: event object that was fired
        """
        # get command type
        cmdtype = self.__resolveCommandType(command, e)

        # ensure the cmd is valid
        if self.__commandExists(command, cmdtype):
            try:
                # only if command is registered
                if self.__commandHandlers[cmdtype].has_key(command):
                    # check for recovered db
                    if EVENT_MCX_DATABASE_RECOVERED.isSet():
                        self.__databaseAvailable = True

                    # if database required but not available
                    if self.__commandHandlers[cmdtype][command]['db'] == True and not self.__databaseAvailable:
                        # tell the user
                        self.__privMsg(c, e, DATABASE_SERVER_NOT_AVAILABLE)
                    # otherwise execute command
                    else:
                        self.__commandHandlers[cmdtype][command]['func'](c, e)
                # command not registered, tell the user
                else:
                    self.__privMsg(c, e, (COMMAND_NOT_FOUND % command))
            # database was set, but is not available anymore
            except NoDatabaseException, (error):
                self.__databaseAvailable = False
                self.__privMsg(c, e, DATABASE_CONNECTION_INTERRUPTED)
                # fire event
                if not EVENT_MCX_DATABASE_LOST.isSet():
                    EVENT_MCX_DATABASE_LOST.set()
        # command does not exist
        else:
            self.__privMsg(c, e, (COMMAND_NOT_FOUND % command))

    def __privMsg(self, c, e, message):
        """
            privmsg message on connection c

            @type c: Connection
            @param c: either DCCConnection or ServerConnection

            @type e: Event
            @param e: event object that was fired

            @type message: string
            @param e: message that will be sent on the connection

            @raise InvalidArgumentException: If the given object (c) is neither an instance of DCCConnection nor ServerConnection class (INVALID_CONNECTION).
        """
        if isinstance(c, DCCConnection):
            c.privmsg(message)

        if isinstance(c, ServerConnection):
            # if message was sent to a channel, answer in channel
            if is_channel(e.target()):
                c.privmsg(e.target(), message)
            # otherwise it was sent via privmsg to nick (bot)
            else:
                c.privmsg(nm_to_n(e.source()), message)

        if not isinstance(c, DCCConnection) and not isinstance(c, ServerConnection):
            raise InvalidArgumentException(INVALID_CONNECTION)

    def __commandExists(self, command, cmdtype):
        """
            checks whether a given command is registered on the given type

            @type command: string
            @param command: name of the command to execute

            @type cmdtype: string
            @param cmdtype: type of the command to execute

            @rtype: bool
            @return: state whether the command is available on the given type
        """
        try:
            # method exists
            if hasattr(self, self.__getFullCommandName(command, cmdtype)):
                # command handler type exists
                if self.__commandHandlerTypeExists(cmdtype):
                    return True
                else:
                    return False
            else:
                return False
        # any key does not exist
        except KeyError:
            return False

    def __resolveCommandType(self, command, e):
        """
            resolves the command type by an event and a command

            @type command: string
            @param command: name of the command to execute

            @type e: Event
            @param e: event object that was fired

            @rtype: string
            @return: actual name of the command type
        """
        # check for existing DCC Connection
        try:
            if self.__IpToUser[e.source()]['auth'] == NOT_AUTHED:
                return 'not_authed_dcc'
            else:
                return 'authed_dcc'
        # DCC Connection does not exist
        except KeyError:

            if not is_channel(e.target()):
                return 'query'
            else:
                # defaults to channel
                return 'channel'

    def __resolveCommandFunction(self, command, e):
        """
            resolve the function to call by an event and a command

            @type command: string
            @param command: name of the command to execute

            @type e: Event
            @param e: event object that was fired

            @rtype: string
            @return: actual name of the function to call
        """
        return self.__getFullCommandName(command, self.__resolveCommandType(command, e))

    def __getFullCommandName(self, command, type):
        """
            returns the method name of this object for the given command and command type

            @type command: string
            @param command: name of the command to execute

            @type type: string
            @param type: type of the command to execute

            @rtype: string
            @return: complete name of the command (function to call on this object)
        """
        return 'cmd_%s_%s' % (type, command)

    def __addCommandHandler(self, command, type = 'channel', requiresdb = False):
        """
            adds a new command handler to the system

            @type command: string
            @param command: name of the command to execute

            @type type: string
            @param type: type of the command to execute

            @type requiresdb: bool
            @param requiresdb: flag if the command requires a connection to mcxPersistent

            @rtype: bool
            @return: state whether the command handler was added

            @raise ConfigurationException:
                If command requires database, but no database is given (CONFIG_DATABASE_NOT_AVAILABLE).
                If method for command is not found (CONFIG_COMMAND_EXEC_NOT_FOUND).
                If command type is not registered (CONFIG_COMMAND_TYPE_NOT_FOUND).
        """
        try:
            # ensure we are dealing with booleans
            if not requiresdb:
                requiresdb = False
            else:
                requiresdb = True

            # add the handler
            # check for existing command type
            if self.__commandHandlerTypeExists(type):
                cmdExec = self.__getFullCommandName(command, type)

                # if database required but no database available raise exception
                if requiresdb and not self.__databaseAvailable:
                    raise ConfigurationException(CONFIG_DATABASE_NOT_AVAILABLE % cmdExec)

                # add handler only if the correct method exists
                if self.__commandExists(command, type):
                    cmdHandler = {'func': getattr(self, cmdExec),
                        'db': requiresdb}
                    self.__commandHandlers[type][command] = cmdHandler
                else:
                    raise ConfigurationException(CONFIG_COMMAND_EXEC_NOT_FOUND % cmdExec)
            else:
                raise ConfigurationException(CONFIG_COMMAND_TYPE_NOT_FOUND % type)

        except ConfigurationException, (e):
            print 'Configuration failed: ',
            print 'Could not add the command handler for %s: ' % command
            print e.parameter

    def __setupCommandHandlerTypes(self):
        """
            function that registered all handled command types
        """
        # dict saving all command handler types
        self.__commandHandlers = {'channel': {}, 'query': {}, 'not_authed_dcc': {}, 'authed_dcc': {}}

    def __commandHandlerTypeExists(self, type):
        """
            checks whether the given command type exists

            @rtype: bool
            @return: state whether command type is available
        """
        return self.__commandHandlers.has_key(type)

    #} end command handling functions
    
    #{ message bridging handling 
    
    def messageBridgeInput(self, input):
        self.connection.privmsg(self.channel, input)

    #} end message bridging handling functions

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 5:
        print "Usage: mcxPyBot.py <server[:port]> <channel> <nickname> <password> [usedatabase=on|off]"
        sys.exit(1)
    elif len(sys.argv) > 6:
        print "Usage: mcxPyBot.py <server[:port]> <channel> <nickname> <password> [usedatabase=on|off]"
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    # if any port is given by user
    if len(s) == 2:
        try:
            # check whether it's an int
            port = int(s[1])
        except ValueError:
            # if no int given, exit and display error
            print "Error: Erroneous port."
            sys.exit(1)
    else:
        # no port given by user, so use default IRC port
        port = 6667

    channel = sys.argv[2]
    nickname = sys.argv[3]
    password = sys.argv[4]

    # mcxDatabase
    if len(sys.argv) == 6:
        if (sys.argv[5] == "on"):
            # create database object
            mcxDB = mcxDatabase()
        else:
            mcxDB = False
    else:
        mcxDB = False

    try:
        # create mcxPyBot
        bot = mcxPyBot(channel, nickname, password, server, port, mcxDB)

        # start mcxPyBot
        mcxBotThread = mcxPyBotThread(bot)
        mcxBotThread.setName(THREAD_NAME_MCXPYBOT)
        mcxBotThread.start()
        if mcxBotThread.isAlive:
            print "%s running .." % THREAD_NAME_MCXPYBOT

        # create thread for recoverage on lost db
        mcxRecoverThread = mcxRecoverDBThread(DATABASE_HOST, DATABASE_USER, DATABASE_PASS, DATABASE_NAME)
        mcxRecoverThread.setName(THREAD_NAME_RECOVERDB)
        mcxRecoverThread.setDaemon(True)
        mcxRecoverThread.start()
        if mcxRecoverThread.isAlive:
            print "%s running .." % THREAD_NAME_RECOVERDB

        # create thread checking for updates on database
        mcxUpdateThread = mcxCheckUpdatesThread(DATABASE_HOST, DATABASE_USER, DATABASE_PASS, DATABASE_NAME)
        mcxUpdateThread.setName(THREAD_NAME_UPDATECHECK)
        mcxUpdateThread.setDaemon(True)
        mcxUpdateThread.start()
        if mcxUpdateThread.isAlive:
            print "%s running .." % THREAD_NAME_UPDATECHECK
            
        # create thread for message bridging from megacomplex web application
        mcxMessageThread = mcxMessageBridgeThread(bot.messageBridgeInput)
        mcxMessageThread.setName(THREAD_NAME_MESSAGEBRIDGE)
        mcxMessageThread.setDaemon(True)
        mcxMessageThread.start()
        if mcxMessageThread.isAlive:
            print "%s running .." % THREAD_NAME_MESSAGEBRIDGE

        # create thread for connection pooling
        #mcxConnectionPool = mcxPyBotConnectionPooler()
        #mcxConnectionPool.setName(THREAD_NAME_CONNECTIONPOOL)
        #mcxConnectionPool.setDaemon(True)
        #mcxConnectionPool.start()
        #if mcxConnectionPool.isAlive:
        #    print "%s running .." % THREAD_NAME_CONNECTIONPOOL

        # wait for threads to terminate
        mcxBotThread.join()

    except InvalidArgumentException, (error):
        # clear last line of terminal or other output
        print error
        print 'mcxPyBot could not be initiated, shutting down ..'
        mcxBotThread.join()

    except KeyboardInterrupt, (error):
        # clear last line of terminal or other output
        print error
        # shutdown the bot correctly
        print 'mcxPyBot initiates self destruct sequence ..'
        try:
            bot.die()
            mcxBotThread.join()
        except:
            print 'mcxPyBot could not self destruct'

    except Exception, (error):
            # clear terminal output
            print error
            try:
                bot.die()
                mcxBotThread.join()
            except Exception, (error):
                print error
                print 'mcxPyBot did not shut down correctly'

    print "mcxPyBot shut down"
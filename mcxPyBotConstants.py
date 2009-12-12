#!/usr/bin/env python
#
#  mcxPersistentExceptions.py
#  mcxPyBot
#
#  Created by Toni Uebernickel on 11/27/08.
#  Copyright (c) 2008 Whitestarprogramming GbR. All rights reserved.
#

"""mcxPyBotConstants -- Constants for mcxPyBot module.

@author: Toni Uebernickel
@organization: Whitestarprogramming GbR
@copyright: 2008-2009 Whitestarprogramming GbR. All rights reserved.
@contact: tuebernickel@whitestarprogramming.de

@var DATE_FORMAT_STRING: A date format string for the datetime module that will be used when sending datetime information to the user.

@var CONFIG_DATABASE_NOT_AVAILABLE: Error message displayed when database is not available while configuration of mcxPyBot is running.
@var CONFIG_COMMAND_EXEC_NOT_FOUND: Error message displayed when the required method for a configurated command is not found.
@var CONFIG_COMMAND_TYPE_NOT_FOUND: Error message displayed when the given command type for a configurated command is not found.

@var THREAD_NAME_MCXPYBOT: The name for the main mcxPyBot thread.
@var THREAD_NAME_RECOVERDB: The name for the thread recovering mcxPersistent connection.
@var THREAD_NAME_UPDATECHECK: The name for the thread which is checking for new available update.
@var THREAD_NAME_CONNECTIONPOOL: The name for the thread which is pooling DCC connections.
@var THREAD_NAME_MESSAGEBRIDGE: The name for the thread bridging messages..

@var INVALID_CONNECTION: Exception message for invalid connection on connection parameters.
@var INVALID_BOT_OBJECT: Exception message for invalid mcxPyBot object reference.

@var NOT_AUTHED: State for unauthentificated users.

@var COMMAND_NOT_FOUND: Message sent to user, when a requested command is not found.
@var FEATURE_DISABLED: Message sent to user, when a requested feature is disabled.

@var AUTH_USER_FAILED: Message sent to user, when authentification failed.
@var AUTH_USER_SUCCESS_BY_BOTKEY: Message sent to user, when authentification with a botkey was successful.

@var DATABASE_CONNECTION_INTERRUPTED: Message sent to user, when the database connection is interrupted (first command).
@var DATABASE_SERVER_NOT_AVAILABLE: Message sent to user, when the database connection is still not available (further commands).

@var NO_LATEST_MESSAGE: Message sent to user, when the user does not have any new message.
@var LATEST_MESSAGE_INTRO: Header sent to user before sending latest message.
@var LATEST_MESSAGE_FROM: Message sent to user with sender name and date the message was sent.
@var LATEST_MESSAGE_SUBJECT: Message sent to user containing the subject of the message.
@var LATEST_MESSAGE_BODY: Message sent to user containing the content of the latest message.
"""

# configuration
DATE_FORMAT_STRING = '%H:%M:%S %d.%m.%Y'

# failed configuration messages
CONFIG_DATABASE_NOT_AVAILABLE = 'Database not available for command %s'
CONFIG_COMMAND_EXEC_NOT_FOUND = 'Command executor not found: %s'
CONFIG_COMMAND_TYPE_NOT_FOUND = 'Command type not found: %s'

# threads
THREAD_NAME_MCXPYBOT = "mcxPyBot Thread"
THREAD_NAME_RECOVERDB = "mcxPyBot recover DB Thread"
THREAD_NAME_UPDATECHECK = "mcxPyBot Update Thread"
THREAD_NAME_CONNECTIONPOOL = "mcxPyBot ConnectionPooler"
THREAD_NAME_MESSAGEBRIDGE = "mcxPyBot MessageBridge"

# exceptions
INVALID_CONNECTION = 'The given connection object is invalid.'
INVALID_BOT_OBJECT = 'The given object is no mcxPyBot object.'

NOT_AUTHED = 'The user was not found.'

# messages sent to the user (via IRC)
# commands
COMMAND_NOT_FOUND = 'Befehl nicht gefunden: %s'
FEATURE_DISABLED = 'Dieser Teil ist derzeit deaktiviert.'

# authentification
AUTH_USER_FAILED = 'Die Authentifizierung ist fehlgeschlagen!'
AUTH_USER_SUCCESS_BY_BOTKEY = 'Du hast dich erfolgreich authentifiziert.'

# database
DATABASE_CONNECTION_INTERRUPTED = 'Die Datenbankverbindung wurde unterbrochen.'
DATABASE_SERVER_NOT_AVAILABLE = 'Der Datenbankserver ist derzeit nicht erreichbar.'

# responses
NO_LATEST_MESSAGE = 'Du hast keine Nachricht im Posteingang.'
LATEST_MESSAGE_INTRO = 'Deine neueste Nachricht:'
LATEST_MESSAGE_FROM = "Nachricht gesendet von %s (%s)"
LATEST_MESSAGE_SUBJECT = "Betreff: %s"
LATEST_MESSAGE_BODY = "Inhalt: %s"
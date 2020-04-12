#!/usr/bin/python3
"""
This software has been developed by github user fndh (http://github.com/fndh)

You are free to use, modify and redistribute this software as you please, as
long as you follow the conditions listed in the LICENSE file of the github
repository indicated. I want to thank you for reading this small paragraph,
and please consider sending me a message if you are using this software! It
will surely make my day.
"""
import logging
import os
import time

import requests
from telegram import Update
from telegram.ext import (MessageHandler, Filters, Updater, CommandHandler,
                          CallbackQueryHandler, CallbackContext)

import BotBlocker
import BotCallbackHandler
import BotLogger
import BotMessageSender
import SQLiteWrapper

# ---READ CONFIG---

with open('config.txt', 'r') as f:
    tg_token = f.readline().strip()
    tg_id = f.readline().strip()

# ---LOGGING---

logging_enabled = True
logger = BotLogger.Logger(logging_enabled)
logger.log("Logging enabled")

# ---DATABASE---

db_name = 'DB_AnonymousForwardBot.db'
sql = SQLiteWrapper.SQLiteWrapper(db_name)
sql.execute_and_commit(
    "CREATE TABLE IF NOT EXISTS forwarded_msg_ids (message_id, user_id);")

# ---BLOCKED USERS MANAGEMENT---

blocker = BotBlocker.Blocker(sql)

# ---MESSAGE UTILITIES---

messenger = BotMessageSender.MessageSender(logger)
callback_handler = BotCallbackHandler.CallbackHandler(messenger, sql)


# ---AUX FUNCTIONS---

def get_root_message(message):
    """Gets the message at the root of a reply chain.

    Forwarded messages lose their replies."""
    root_message = message
    while root_message.reply_to_message is not None:
        root_message = root_message.reply_to_message
    return root_message


def get_forwarded_userid(message):
    """Fetches the user ID of a recieved message."""
    # Check that the message is a forward from a user
    forwarded_user = message.forward_from
    if forwarded_user is None:
        return None

    # Check if the message was forwarded by the user to the bot
    sql_select = sql.select_and_fetch(
        "SELECT user_id FROM forwarded_msg_ids WHERE message_id=?;",
        (message.message_id,))

    if sql_select:
        # First element
        return sql_select[0][0]
    else:
        return forwarded_user.id


# ---BASIC COMMANDS---

def start(update: Update, context: CallbackContext):
    """ User started the bot. Greet with message.
    /start
    """
    messenger.send_typing(context.bot, update.message.chat_id)
    welcome_msg = "Hello!\nPlease leave your message here and I will answer " \
                  "ASAP."
    messenger.send_text(
        context.bot, update.message.chat_id, welcome_msg,
        reply=update.message.message_id)


def start_owner(update: Update, context: CallbackContext):
    """ Owner started the bot. Greet with message.
    /start
    """
    messenger.send_typing(context.bot, update.message.chat_id)
    welcome_msg = "Hello! Bot is running. It will forward all messages to you."
    messenger.send_text(
        context.bot, update.message.chat_id, welcome_msg,
        reply=update.message.message_id)


def help(update: Update, context: CallbackContext):
    """ Send help.
    /help
    """
    messenger.send_typing(context.bot, update.message.chat_id)
    help_text = "Hi!\n\n"
    help_text += "This bot forwards your messages to its owner"
    help_text += " while keeping the owner anonymous. If you're interested"
    help_text += " in the source code, visit:\n\n\t"
    help_text += "https://github.com/fndh/Anonymous-Telegram-Bot"
    messenger.send_text(context.bot, update.message.chat_id, help_text)


# ---LOGGING COMMANDS---

def clear_logs(update: Update, context: CallbackContext):
    """ Delete log file if prompted from owner id.
    /clearlogs
    """
    logger.clear(context.bot)


def get_logs(update: Update, context: CallbackContext):
    """ Get the last N lines from the log file, defaults to 50.
    /getlogs [N]
    """
    messenger.send_typing(context.bot, update.message.chat_id)
    try:
        if len(context.args) and int(context.args[0]) > 0:
            lines = int(context.args[0])
            msg = logger.get(lines)
        else:
            msg = logger.get(50)
        messenger.send_text(context.bot, update.message.chat_id, msg)
    except Exception as e:
        logger.log(f"getlogs - {e}")
        messenger.send_text(
            context.bot, update.message.chat_id,
            f"Error while getting logs {e}")


# ---BLOCKING COMMANDS---

def block_user(update: Update, context: CallbackContext):
    """ Ignore all messages sent by a user.
    /block (While replying to a message)
    """
    user_id = get_forwarded_userid(update.message.reply_to_message)
    if user_id is not None:
        blocker.block_user(user_id)
        messenger.send_text(context.bot, tg_id, f"Blocked user {user_id}")


def unblock_user(update: Update, context: CallbackContext):
    """ Recieve messages from a blocked user again.
    /unblock (While replying to a message)
    """
    user_id = get_forwarded_userid(update.message.reply_to_message)
    if user_id is not None:
        blocker.unblock_user(user_id)
        messenger.send_text(context.bot, tg_id, f"Unblocked user {user_id}")


def list_blocked_users(update: Update, context: CallbackContext):
    """ Get the list of blocked user IDs.
    /listblockedusers
    """
    users = blocker.get_blocked_users()
    msg = "Blocked ids:\n\n"
    msg += '\n'.join(users) if users else 'No blocked IDs'
    messenger.send_text(context.bot, tg_id, msg)


# ---MESSAGE HANDLING---

def new_message(update: Update, context: CallbackContext):
    """ User talking to the bot """
    logger.log("New message")
    sent_msg = messenger.forward_message(update.message, tg_id)
    logger.log(f"\tForwarded to owner, msg id {sent_msg.message_id}")

    user = update.message.from_user
    forwarded_user = update.message.forward_from
    # The user forwarded a message to the bot
    if forwarded_user is not None:
        logger.log("\tOriginal message was forwarded from somebody")
        log_msg = f"\t\tStoring message id {sent_msg.message_id}"
        log_msg += f" with user id {user.id}"
        logger.log(log_msg)

        # Store relation between message id and user id
        sql.execute_and_commit(
            "INSERT INTO forwarded_msg_ids (message_id, user_id) VALUES (?, ?);",
            (sent_msg.message_id, user.id))

        # Notify owner that last message was a forward
        messenger.send_text(
            context.bot, tg_id,
            f"Message forwarded by user @{user.username}",
            reply=sent_msg.message_id)


def owner_message(update: Update, context: CallbackContext):
    """ Owner talking to the bot

    Only works if the owner is replying to a user message."""
    # Get user message the owner is replying to (accepts reply chains).
    message = get_root_message(update.message)
    # Get user id
    user_id = get_forwarded_userid(message)

    log_msg = f"\tReplying to user id {user_id}, msg id {message.message_id}"
    logger.log(log_msg)
    if user_id is not None:
        # Copy the reply text and send to the user
        messenger.send_text(context.bot, user_id, update.message.text)
    else:
        messenger.send_text(context.bot, tg_id, "user_id is None")


# ---START BOT---

logger.log('-' * 10 + time.strftime(" %H:%M:%S ") + '-' * 10)

try:
    ip = requests.get("https://api.ipify.org?format=json").json()['ip']
except:
    ip = "127.0.0.1"
logger.log(f'Starting bot at {ip}')

# -----------------------------------
#    Start system logging
# -----------------------------------

logger.log('Setting up logging')
logging.basicConfig(
    filename=os.path.dirname(os.path.abspath(__file__)) + 'log.out',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR)

# -----------------------------------
#    Create bot instance
# -----------------------------------
logger.log('Retrieving dispatcher')
updater = Updater(token=tg_token, use_context=True)
dispatcher = updater.dispatcher

# -----------------------------------
#    Add handlers to bot
# -----------------------------------
logger.log('Adding handlers')
owner_filter = Filters.chat(chat_id=int(tg_id))
# Public commands
dispatcher.add_handler(CommandHandler(
    'start',
    start,
    filters=~owner_filter))
dispatcher.add_handler(CommandHandler(
    'help',
    help,
    filters=~owner_filter))

# Owner commands
dispatcher.add_handler(CommandHandler(
    'start',
    start_owner,
    filters=owner_filter))
dispatcher.add_handler(CommandHandler(
    'help',
    callback_handler.send_initial_message,
    filters=owner_filter))

dispatcher.add_handler(CallbackQueryHandler(
    callback_handler.handle_callback))

dispatcher.add_handler(CommandHandler(
    'getlogs',
    get_logs,
    filters=owner_filter))
dispatcher.add_handler(CommandHandler(
    'clearlogs',
    clear_logs,
    filters=owner_filter))
dispatcher.add_handler(CommandHandler(
    'block',
    block_user,
    filters=owner_filter & Filters.reply))
dispatcher.add_handler(CommandHandler(
    'unblock',
    unblock_user,
    filters=owner_filter & Filters.reply))
dispatcher.add_handler(CommandHandler(
    'listblockedusers',
    list_blocked_users,
    filters=owner_filter))

# Public messages
msg_filter = ~Filters.command & ~Filters.status_update

dispatcher.add_handler(MessageHandler(
    msg_filter & ~owner_filter,
    new_message))

# Owner messages
dispatcher.add_handler(MessageHandler(
    msg_filter & owner_filter & Filters.reply,
    owner_message))

# -----------------------------------
#    Start polling
# -----------------------------------
logger.log('Starting to poll')
updater.start_polling(poll_interval=1.0)

# -----------------------------------
#    Go idle
# -----------------------------------
logger.log('Start successful. Going idle now')
logger.log('-' * 20)
updater.idle()

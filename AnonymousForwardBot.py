#!/usr/bin/python2
'''
This software has been developed by github user fndh (http://github.com/fndh)

You are free to use, modify and redistribute this software as you please, as
long as you follow the conditions listed in the LICENSE file of the github 
repository indicated. I want to thank you for reading this small paragraph,
and please consider sending me a message if you are using this software! It
will surely make my day.
'''
import logging
import time
from telegram import ParseMode, Message, Chat, Bot, TelegramError, ChatAction
from telegram.ext import (MessageHandler, Filters, Updater, CommandHandler,
    CallbackQueryHandler)

import SQLiteWrapper
import BotLogger
import BotBlocker
import BotMessager
import BotCallbackHandler

#---READ CONFIG---

my_token = ''
my_path = ''
my_id = ''
with open('config.txt', 'r') as f:
    my_token = f.readline().rstrip('\n').rstrip('\r')
    my_path  = f.readline().rstrip('\n').rstrip('\r')
    my_id    = f.readline().rstrip('\n').rstrip('\r')

#---LOGGING---

logging_enabled = True
logger = BotLogger.Logger(my_path, logging_enabled)
logger.log("Logging enabled")

#---DATABASE---

db_name = 'DB_AnonymousForwardBot.db'
sql = SQLiteWrapper.SQLiteWrapper(db_name)
sql.execute_and_commit(
    "CREATE TABLE IF NOT EXISTS forwarded_msg_ids (message_id, user_id);")
    
#---BLOCKED USERS MANAGEMENT---

blocker = BotBlocker.Blocker(sql)

#---MESSAGE UTILITIES---

messager = BotMessager.Messager(logger)
callback_handler = BotCallbackHandler.CallbackHandler(messager, sql)


#---AUX FUNCTIONS---

def get_root_message(message):
    '''
    Gets the message at the root of a reply chain. Forwarded
    messages lose their replies.
    '''
    root_message = message
    while root_message.reply_to_message is not None:
        root_message = root_message.reply_to_message
    return root_message


def get_forwarded_userid(message):
    '''
    Fetches the user ID of a recieved message. 
    '''
    #Check that the message is a forward from a user
    forwarded_user = message.forward_from
    if forwarded_user is None:
        return None
    
    #Check if the message was forwarded by the user to the bot
    sql_select = sql.select_and_fetch(
        "SELECT user_id FROM forwarded_msg_ids WHERE message_id=?;",
        (message.message_id,))
        
    user_id = ''
    if sql_select:
        #First element
        user_id = sql_select[0][0]
    else:
        user_id = forwarded_user.id
    return user_id

#---BASIC COMMANDS---

def start(bot, update):
    '''
    User started the bot. Greet with message
    /start
    '''
    messager.send_typing(bot, update.message.chat_id)
    welcome_msg = "Hello!"
    messager.send_text(
        bot, update.message.chat_id, welcome_msg,
        reply=update.message.message_id)


def help(bot, update, args):
    '''
    Send help
    /help
    '''
    messager.send_typing(bot, update.message.chat_id)
    help_text = "Hi!\n\n"
    help_text += "This bot forwards your messages to its owner "
    help_text += " while keeping him anonymous. If you're interested"
    help_text += " in the source code, visit:\n\n\t"
    help_text += "https://github.com/fndh/Anonymous-Telegram-Bot"
    messager.send_text(bot, update.message.chat_id, help_text)


#---LOGGING COMMANDS---

def clear_logs(bot, update):
    '''
    Delete log file if prompted from owner id
    /clearlogs
    '''
    logger.clear()


def get_logs(bot, update, args):
    '''
    Get the last N lines from the log file, defaults to 50
    /getlogs [N]
    '''
    messager.send_typing(bot, update.message.chat_id)
    try:
        msg = ''
        if len(args) and int(args[0]) > 0:
            lines = int(args[0])
            msg = logger.get(lines)
        else:
            msg = logger.get(50)
        messager.send_text(bot, update.message.chat_id, msg)
    except Exception as e:
        logger.log('getlogs - {}'.format(e))
        messager.send_text(
            bot, update.message.chat_id,
            "Error while getting logs {}".format(e))


#---BLOCKING COMMANDS---

def block_user(bot, update):
    '''
    Ignore all messages sent by a user
    '''
    user_id = get_forwarded_userid(update.message.reply_to_message)
    if user_id is not None:
        blocker.block_user(user_id)
        messager.send_text(bot, my_id, "Blocked user {}".format(user_id))
    


def unblock_user(bot, update):
    '''
    Recieve messages from the user again
    '''
    user_id = get_forwarded_userid(update.message.reply_to_message)
    if user_id is not None:
        blocker.unblock_user(user_id)
        messager.send_text(bot, my_id, "Unblocked user {}".format(user_id))


def list_blocked_users(bot, update):
    users = blocker.get_blocked_users()
    msg = "Blocked ids:\n\n"
    msg += '\n'.join(users) if users else 'No blocked IDs'
    messager.send_text(bot, my_id, msg)

#---MESSAGE HANDLING---

def new_message(bot, update):
    '''
    User talking to the bot
    '''
    logger.log("New message")
    sent_msg = messager.forward_message(update.message, my_id)
    logger.log("\tForwarded to owner, msg id {}".format(sent_msg.message_id))
    
    user = update.message.from_user
    forwarded_user = update.message.forward_from
    #The user forwarded a message to the bot
    if forwarded_user is not None:
        logger.log("\tOriginal message was forwarded from somebody")
        log_msg = "\t\tStoring message id {}".format(sent_msg.message_id)
        log_msg += " with user id {}".format(user.id)
        logger.log(log_msg)
        
        #Store relation between message id and user id
        sql.execute_and_commit(
            "INSERT INTO forwarded_msg_ids (message_id, user_id) VALUES (?, ?);",
            (sent_msg.message_id, user.id))
        
        #Notify owner that last message was a forward
        messager.send_text(
            bot, my_id,
            "Message forwarded by user @{}".format(user.username),
            reply=sent_msg.message_id)


def owner_message(bot, update):
    '''
    Owner talking to the bot
    '''
    #Get user message the owner is replying to (accepts reply chains).
    message = get_root_message(update.message)
    #Get user id
    user_id = get_forwarded_userid(message)
    
    log_msg = "\tReplying to user id {}".format(user_id)
    log_msg += ", "
    log_msg += "msg id {}".format(message.message_id)
    logger.log(log_msg)
    if user_id is not None:
        #Copy the reply text and send to the user
        messager.send_text(bot, user_id, update.message.text)
    else:
        messager.send_text(bot, my_id, "user_id is None")
    

#---START BOT---

logger.log('-'*10 + time.strftime(" %H:%M:%S ") + '-'*10)
logger.log('Starting bot...')

#-----------------------------------
#    Start system logging
#-----------------------------------

logger.log('Setting up logging')
logging.basicConfig(
    filename=my_path + 'log.out',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR)


#-----------------------------------
#    Create bot instance
#-----------------------------------
logger.log('Retrieving dispatcher')
updater = Updater(token=my_token)
dispatcher = updater.dispatcher

#-----------------------------------
#    Add handlers to bot
#-----------------------------------
logger.log('Adding handlers')
owner_filter = Filters.chat(chat_id=int(my_id))
#Public commands
dispatcher.add_handler(CommandHandler(
    'start',
    start))
dispatcher.add_handler(CommandHandler(
    'help',
    help,
    filters=~owner_filter,
    pass_args = True))

#Owner commands
dispatcher.add_handler(CommandHandler(
    'help',
    callback_handler.send_initial_message,
    filters=owner_filter))
    
dispatcher.add_handler(CallbackQueryHandler(
    callback_handler.handle_callback))
    
dispatcher.add_handler(CommandHandler(
    'getlogs',
    get_logs,
    filters=owner_filter,
    pass_args=True))
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

#Public messages
msg_filter = ~Filters.command & ~Filters.status_update

dispatcher.add_handler(MessageHandler(
    msg_filter & ~owner_filter,
    new_message))

#Owner messages
dispatcher.add_handler(MessageHandler(
    msg_filter & owner_filter & Filters.reply,
    owner_message))



#-----------------------------------
#    Start polling
#-----------------------------------
logger.log('Starting to poll')
updater.start_polling(poll_interval=1.0)

#-----------------------------------
#    Go idle
#-----------------------------------
logger.log('Start successful. Going idle now :)')
logger.log('-'*20)
updater.idle()

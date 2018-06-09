#!/usr/bin/python
'''
This software has been developed by github user fndh (http://github.com/fndh)

You are free to use, modify and redistribute this software as you please, as
long as you follow the conditions listed in the LICENSE file of the github 
repository indicated. I want to thank you for reading this small paragraph,
and please consider sending me a message if you are using this software! It
will surely make my day.
'''
import logging
from telegram import ParseMode, Message, Chat, Bot, TelegramError, ChatAction
from telegram.ext import MessageHandler, Filters, Updater, CommandHandler
import sqlite3

import BotLogger

#---READ CONFIG---

my_token = ''
my_path = ''
my_id = ''
with open('config.txt', 'r') as f:
    my_token = f.readline().rstrip('\n').rstrip('\r')
    my_path  = f.readline().rstrip('\n').rstrip('\r')
    my_id    = f.readline().rstrip('\n').rstrip('\r')

#---DATABASE---

db_name = 'Anon_Forward_Bot.db'

sql_connection = sqlite3.connect(db_name, check_same_thread=False)
sql_cursor = sql_connection.cursor()
sql_cursor.execute(
        "CREATE TABLE IF NOT EXISTS msgid_forwarderid (msg, forwarder);")
sql_connection.commit()


#---LOGGING---

logger = BotLogger.Logger(my_path)


#---AUX FUNCTIONS---

def get_kwargs(kw_dict, key, default):
    '''
    Using kwargs.get(key, default) was giving some problems on invalid keys
    '''
    if key in kw_dict:
        return kw_dict[key]
    else:
        return default


def send(bot, user, message, tried=0, **kwargs):
    '''
    Send messages with markdown, markup or replies
    '''
    try:
        reply = get_kwargs(kwargs, 'reply', None)
        replymarkup = get_kwargs(kwargs, 'markup', None)
        markdown = get_kwargs(kwargs, 'markdown', 'HTML')

        bot.sendMessage(
            str(user),
            message,
            reply_to_message_id=reply,
            reply_markup=replymarkup,
            parse_mode=markdown)
    except TelegramError as e: 
        logger.log("TelegramError when sending message to {}:".format(user)
        logger.log("{} - Try {}".format(e.message, tried))
        if e.message == 'Timed out' and tried < 3:
            send(
                bot, user, message, tried=tried+1,
                reply=reply, markup=replymarkup, markdown=markdown)
    except RuntimeError as e:
        logger.log("RuntimeError when sending message")
        logger.log(e.message)
    except Exception as e:
        logger.log("Unhandled error when sending message")
        logger.log(e.message)


#---BASIC COMMANDS---

def start(bot, update):
    '''
    User started the bot. Greet with message
    /start
    '''
    bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
    welcome_msg = "Hello!"
    send(
        bot, update.message.chat_id, welcome_msg,
        reply=update.message.message_id)


def help(bot, update, args):
    '''
    Send help
    /help
    '''
    bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
    help_text = "Help text"
    send(bot, update.message.chat_id, help_text)


#---LOGGING COMMANDS---

def clear_logs(bot, update):
    '''
    Delete log file if prompted from owner id
    /clearlogs
    '''
    if str(update.message.from_user.id) == my_id:
        logger.clear()


def get_logs(bot, update, args):
    '''
    Get the last N lines from the log file, defaults to 50
    /getlogs [N]
    '''
    if str(update.message.from_user.id) == my_id:
        bot.sendChatAction(update.message.chat_id, ChatAction.TYPING)
        try:
            msg = ''
            if len(args) and int(args[0]) > 0:
                lines = int(args[0])
                msg = logger.get(lines)
            else:
                msg = logger.get(50)
            send(bot, update.message.chat_id, msg)
        except Exception as e:
            logger.log('getlogs - %s' %(e.message))
            send(
                bot, update.message.chat_id,
                "Error while getting logs {}".format(e.message))


#---MESSAGE HANDLING---

def new_message(bot, update):
    '''
    Bot received a new message
    '''
    userinfo = update.message.from_user
    logger.log("New message from @{}".format(userinfo.username))
    if str(userinfo.id) == my_id:
        outgoing_message(bot, update)
    else:
        incoming_message(bot, update)
    

def outgoing_message(bot, update):
    '''
    Owner replying to a forwarded message
    '''
    logger.log("\tIs outgoing")
    replied_message = update.message.reply_to_message
    if replied_message is None:
        log("\tNot replying to anything")
        return
    
    #Cached message id? If it is, then somebody forwarded a post to the bot
    #Get the user info from the forwarder, not the forwarded
    sql_cursor.execute(
        "SELECT forwarder FROM msgid_forwarderid WHERE msg=?;",
        (replied_message.message_id,))
    sql_select = sql_cursor.fetchone()

    user_id = ''
    if sql_select is not None:
        user_id = sql_select[0]
    else:
        user_id = replied_message.forward_from.id
    
    log_msg = "\tReplying to user id {}".format(user_id)
    log_msg += ", "
    log_msg += "msg id {}".format(replied_message.message_id)
    logger.log(log_msg)
    if user_id is not None:
        send(bot, user_id, update.message.text.encode('utf-8'))
    else:
        send(bot, my_id, "user_id is None")
    

def incoming_message(bot, update):
    '''
    User talking to the bot
    '''
    logger.log("\tIs incoming")
    sent_msg = update.message.forward(my_id)
    logger.log("\tForwarded to owner, msg id {}".format(sent_msg.message_id))
    #Somebody forwarded a message to the bot
    if update.message.forward_from is not None:
        logger.log("\tOriginal message was forwarded from somebody")
        log_msg = "\t\tStoring message id {}".format(sent_msg.message_id)
        log_msg += " with user id {}".format(update.message.from_user.id)
        logger.log(log_msg)
        sql_cursor.execute(
            "INSERT INTO msgid_forwarderid (msg, forwarder) VALUES (?, ?);",
            (sent_msg.message_id, update.message.from_user.id))
        sql_connection.commit()


#---START BOT---

logger.log('-'*20)
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
dispatcher.add_handler(CommandHandler('start', start))

dispatcher.add_handler(CommandHandler('help', help, pass_args = True))

dispatcher.add_handler(CommandHandler('getlogs', get_logs, pass_args=True))
dispatcher.add_handler(CommandHandler('clearlogs', clear_logs))

msg_filters = ~Filters.command & ~Filters.status_update
dispatcher.add_handler(MessageHandler(msg_filters, new_message))

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

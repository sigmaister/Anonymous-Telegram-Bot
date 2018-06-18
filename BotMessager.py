'''
This software has been developed by github user fndh (http://github.com/fndh)

You are free to use, modify and redistribute this software as you please, as
long as you follow the conditions listed in the LICENSE file of the github 
repository indicated. I want to thank you for reading this small paragraph,
and please consider sending me a message if you are using this software! It
will surely make my day.
'''
from telegram import (ParseMode, Message, Chat, Bot, TelegramError,
    ChatAction, InlineKeyboardMarkup, InlineKeyboardButton)

class Messager():
    
    def __init__(self, logger):
        self.logger = logger


    def send_text(self, bot, user, message, tried=0, reply=None,
                  reply_markup=None, parse_mode=None):
        '''
        Send messages with markdown, markup or replies.
        Returns the sent message.
        '''
        try:
            return bot.sendMessage(
                str(user),
                message,
                reply_to_message_id=reply,
                reply_markup=reply_markup,
                parse_mode=parse_mode)
            
        except TelegramError as e: 
            self.logger.log(
                "TelegramError when sending message to {}:".format(user))
            self.logger.log(
                "\t{} - Try #{}/3".format(e.message, tried))
            if e.message == 'Timed out' and tried < 3:
                return self.send_text(
                    bot, user, message,
                    tried=tried+1,
                    reply=reply,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode)
                    
        except RuntimeError as e:
            self.logger.log("RuntimeError when sending message")
            self.logger.log(e.message)
        except Exception as e:
            self.logger.log("Unhandled error when sending message")
            self.logger.log(e.message)


    def send_typing(self, bot, chat_id):
        '''
        Send "Bot is typing..." action to chat
        '''
        bot.sendChatAction(chat_id, ChatAction.TYPING)

    
    def forward_message(self, message, user_id):
        return message.forward(user_id)


    def create_inline_keyboard(self, buttons, callbacks):
        '''
        Generate a keyboard with the options specified.
        Make sure bot handles callback methods before creating a keyboard.
        
        #TO DO: Add multi-column support
        '''
        if buttons is None or callbacks is None:
            return None
        if len(buttons) != len(callbacks):
            raise ValueError("Buttons and callbacks size doesn't match")
        
        kb_buttons = []
        
        for n in range(len(buttons)):
            text = buttons[n].encode('utf-8')
            callback = callbacks[n].encode('utf-8')
            
            kb_button = InlineKeyboardButton(
                text=text,
                callback_data=callback)
            kb_buttons.append([kb_button])
        
        keyboard = InlineKeyboardMarkup(kb_buttons)
        return keyboard
        





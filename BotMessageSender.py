"""
This software has been developed by github user fndh (http://github.com/fndh)

You are free to use, modify and redistribute this software as you please, as
long as you follow the conditions listed in the LICENSE file of the github
repository indicated. I want to thank you for reading this small paragraph,
and please consider sending me a message if you are using this software! It
will surely make my day.
"""
from telegram import (TelegramError, ChatAction, InlineKeyboardMarkup,
                      InlineKeyboardButton)


class MessageSender:
    
    def __init__(self, logger):
        self.logger = logger

    def send_text(self, bot, user, message, tried=0, reply=None,
                  reply_markup=None, parse_mode=None):
        """
        Send messages with markdown, markup or replies.
        Returns the sent message.
        """
        try:
            return bot.sendMessage(
                str(user),
                message,
                reply_to_message_id=reply,
                reply_markup=reply_markup,
                parse_mode=parse_mode)
            
        except TelegramError as e:
            # Log the errors
            self.logger.log(
                    f"TelegramError when sending message to {user}:")
            self.logger.log(f"\t{e} - Try #{tried}/3")
            if e == 'Timed out' and tried < 3:
                # Retry up to 3 times
                return self.send_text(
                    bot, user, message,
                    tried=tried+1,
                    reply=reply,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode)
                    
        except RuntimeError as e:
            self.logger.log("RuntimeError when sending message")
            self.logger.log(e)
        except Exception as e:
            self.logger.log("Unhandled error when sending message")
            self.logger.log(e)

    def send_typing(self, bot, chat_id):
        """
        Send "Bot is typing..." action to chat
        """
        bot.sendChatAction(chat_id, ChatAction.TYPING)

    def forward_message(self, message, user_id):
        return message.forward(user_id)

    def create_inline_keyboard(self, button_texts, callbacks):
        """Generate a keyboard with the options specified.

        Make sure bot handles callback methods before creating a keyboard.
        """
        if button_texts is None or callbacks is None:
            return None
        if len(button_texts) != len(callbacks):
            raise ValueError("Buttons and callbacks size doesn't match")
        
        kb_buttons = []
        
        # Iterate over information rows
        for n in range(len(button_texts)):
            # Extract display text and callback function
            button_text_row = button_texts[n]
            callback_row = callbacks[n]
            button_row = []

            # Verify size
            if len(button_text_row) != len(callback_row):
                raise ValueError("Buttons and callbacks size doesn't match")
            # Iterate over button texts
            for m in range(len(button_text_row)):
                text = button_text_row[m]
                callback = callback_row[m]
                # Create button
                kb_button = InlineKeyboardButton(
                    text=text,
                    callback_data=callback)
                # Add to button row
                button_row.append(kb_button)

            # Add row to keyboard
            kb_buttons.append(button_row)
        
        keyboard = InlineKeyboardMarkup(kb_buttons)
        return keyboard

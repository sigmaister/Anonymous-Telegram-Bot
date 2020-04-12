"""
This software has been developed by github user fndh (http://github.com/fndh)

You are free to use, modify and redistribute this software as you please, as
long as you follow the conditions listed in the LICENSE file of the github
repository indicated. I want to thank you for reading this small paragraph,
and please consider sending me a message if you are using this software! It
will surely make my day.
"""
from telegram import Update
from telegram.ext import CallbackContext


class CallbackHandler:
    
    def __init__(self, messenger, sql_wrapper):
        self.messenger = messenger
        self.sql = sql_wrapper
        # Check if callback tables exists
        matched_tables = self.sql.select_and_fetch(
            "SELECT count(*) FROM sqlite_master " + 
            "WHERE type='table' AND name IN " +
            "('callback_message', 'callback_buttons', 'callback_state');")
        if matched_tables[0][0] != 3:
            print("Creating tables")
            # At least one table doesn't exist. Create and init entries
            self.__create_tables()

    def send_initial_message(self, update: Update, context: CallbackContext):
        """Prompt the user with the main help keyboard."""
        self.messenger.send_typing(context.bot, update.message.chat_id)
        
        help_msg = self.__get_state_text('default')
        texts, callbacks = self.__get_state_markup('default')
        keyboard = self.messenger.create_inline_keyboard(texts, callbacks)
        
        self.messenger.send_text(
            context.bot, update.message.chat_id,
            help_msg, reply_markup=keyboard)

    def handle_callback(self, update: Update, context: CallbackContext):
        """Receive a callback operation and act accordingly."""
        callback_data = update.callback_query.data
        
        # Update message text
        new_message_text = self.__get_state_text(callback_data)
        update.callback_query.edit_message_text(new_message_text)
        
        # Update inline keyboard
        texts, callbacks = self.__get_state_markup(callback_data)
        new_keyboard = self.messenger.create_inline_keyboard(texts, callbacks)
        update.callback_query.edit_message_reply_markup(
            reply_markup=new_keyboard)

    def __create_tables(self):
        """Create the necessary command and callback tables in the DB.

        Only called at launch if any of the tables doesn't exist.
        """
        self.sql.execute_file("create_button_tables.sql")

    def __get_state_text(self, state):
        """Retrieve the text message to display for a certain callback state."""
        selection = self.sql.select_and_fetch(
            "SELECT message FROM callback_message WHERE state=?",
            (state,))
        return selection[0][0]

    def __get_state_markup(self, state):
        """Retrieve the buttons and callbacks for a certain callback state."""
        selection = self.sql.select_and_fetch(
            "SELECT button FROM callback_buttons WHERE state=?",
            (state,))
        # Get button texts
        button_rows = [row[0].split(",") for row in selection]
        callback_rows = []
        # Get callbacks associated to the buttons
        for button_row in button_rows:
            callback_row = []
            for button in button_row:
                selection = self.sql.select_and_fetch(
                    "SELECT next_state FROM callback_state WHERE button=?",
                    (button,))
                callback = selection[0][0]
                callback_row.append(callback)
            callback_rows.append(callback_row)
        return button_rows, callback_rows

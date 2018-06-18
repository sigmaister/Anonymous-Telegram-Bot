'''
This software has been developed by github user fndh (http://github.com/fndh)

You are free to use, modify and redistribute this software as you please, as
long as you follow the conditions listed in the LICENSE file of the github 
repository indicated. I want to thank you for reading this small paragraph,
and please consider sending me a message if you are using this software! It
will surely make my day.
'''
class CallbackHandler():
    
    def __init__(self, messager, sql_wrapper):
        self.messager = messager
        self.sql = sql_wrapper
        #Check if callback tables exists
        matched_tables = self.sql.select_and_fetch(
            "SELECT count(*) FROM sqlite_master " + 
            "WHERE type='table' AND name IN " +
            "('callback_message', 'callback_buttons', 'callback_state');")
        if matched_tables[0][0] != 3:
            print("Creating tables")
            #At least one table doesn't exist. Create and init entries
            self.__create_tables()


    def send_initial_message(self, bot, update):
        self.messager.send_typing(bot, update.message.chat_id)
        
        help_msg = self.__get_state_text('default').encode('utf-8')
        texts, callbacks = self.__get_state_markup('default')
        keyboard = self.messager.create_inline_keyboard(texts, callbacks)
        
        self.messager.send_text(
            bot, update.message.chat_id,
            help_msg, reply_markup=keyboard)
        


    def handle_callback(self, bot, update):
        callback_data = update.callback_query.data
        
        #Update message text
        new_message_text = self.__get_state_text(callback_data).encode('utf-8')
        update.callback_query.edit_message_text(new_message_text)
        
        #Update inline keyboard
        texts, callbacks = self.__get_state_markup(callback_data)
        new_keyboard = self.messager.create_inline_keyboard(texts, callbacks)
        update.callback_query.edit_message_reply_markup(
            reply_markup=new_keyboard)


    def __create_tables(self):
        #Only called on launch if any table doesn't exist
        self.sql.execute_script_and_commit("""
            DROP TABLE IF EXISTS callback_message;
            DROP TABLE IF EXISTS callback_buttons;
            DROP TABLE IF EXISTS callback_state;
            
            
            --Relation between states and message texts
            CREATE TABLE callback_message (state, message);
            
            INSERT INTO callback_message (state, message) VALUES('default', 'Hello!\n\nWhat can I help you with?');
            
            INSERT INTO callback_message (state, message) VALUES('logging', 'Hello!\n\nThere are several commands that can help verify everything is running smoothly at the server:\n\n/getlogs [N] - Gets the last N lines of logs (default 50).\n/clearlogs - Clears the log file.');
            
            INSERT INTO callback_message (state, message) VALUES('blocking', 'Hello!\n\nIf a user is sending too many messages you can block or unblock all the incoming messages with these commands. To use them, you must reply to a message from that user in particular.\n\n/block - Block incoming messages from that user\n/unblock - Remove block on that user\n/listblockedusers - Lists all the blocked user IDs (not usernames)');
            
            
            --Relation between states and their available buttons
            CREATE TABLE callback_buttons (state, button, PRIMARY KEY (state, button));
            
            INSERT INTO callback_buttons (state, button) VALUES('default', 'Logging \xF0\x9F\x93\x84');
            INSERT INTO callback_buttons (state, button) VALUES('default', 'User management \xF0\x9F\x91\xA4');
            INSERT INTO callback_buttons (state, button) VALUES('logging', 'Go back \xE2\x86\xA9');
            INSERT INTO callback_buttons (state, button) VALUES('blocking', 'Go back \xE2\x86\xA9');
            
            
            --Relation between buttons and their callback data
            CREATE TABLE callback_state (button, next_state);
            
            INSERT INTO callback_state (button, next_state) VALUES('Logging \xF0\x9F\x93\x84', 'logging');
            INSERT INTO callback_state (button, next_state) VALUES('User management \xF0\x9F\x91\xA4', 'blocking');
            INSERT INTO callback_state (button, next_state) VALUES('Go back \xE2\x86\xA9', 'default');
            """)


    def __get_state_text(self, state):
        selection = self.sql.select_and_fetch(
            "SELECT message FROM callback_message WHERE state=?",
            (state,))
        return selection[0][0]


    def __get_state_markup(self, state):
        selection = self.sql.select_and_fetch(
            "SELECT button FROM callback_buttons WHERE state=?",
            (state,))
        #Get button texts
        buttons = [row[0] for row in selection]
        callbacks = []
        #Get callbacks associated to the buttons
        for button in buttons:
            selection = self.sql.select_and_fetch(
                "SELECT next_state FROM callback_state WHERE button=?",
                (button,))
            callbacks.append(selection[0][0])
        return buttons, callbacks


















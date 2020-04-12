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
INSERT INTO callback_buttons (state, button) VALUES('default', 'Logging');
INSERT INTO callback_buttons (state, button) VALUES('default', 'User management');
INSERT INTO callback_buttons (state, button) VALUES('logging', 'Go back');
INSERT INTO callback_buttons (state, button) VALUES('blocking', 'Go back');

--Relation between buttons and their callback data
CREATE TABLE callback_state (button, next_state);
INSERT INTO callback_state (button, next_state) VALUES('Logging', 'logging');
INSERT INTO callback_state (button, next_state) VALUES('User management', 'blocking');
INSERT INTO callback_state (button, next_state) VALUES('Go back', 'default');
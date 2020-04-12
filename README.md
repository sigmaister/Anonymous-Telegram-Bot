# Anonymous Telegram Bot
This project is a Telegram bot. The bot itself acts as a secure wall between other users and yourself, making you anonymous while providing text replies to the other users. The idea behind this bot is for people who own public channels and don't want to expose their private profiles to everybody.

It has been developed using **Python v3.8** and [*Python Telegram Bot*](https://python-telegram-bot.readthedocs.io/en/stable/) v12.6.1
> Python2.7 release [here](https://github.com/fndh/Anonymous-Telegram-Bot/releases/tag/b784a13)

# How to set it up
1. Download Python v3.8
2. Run `pip install -r requirements.txt` to install the required libraries
3. You will need a bot token, which you can obtain from the [@BotFather](https://t.me/BotFather)
4. Download this project and edit the file **config.txt**
   * Add your bot token
   * Add your telegram user ID. It is a unique identifier that can be found in your profile
5. Launch AnonymousForwardBot.py
6. Start your bot by sending a /start command in Telegram

# How to use it
1. When a user messages the bot you are hosting, the bot will forward their message to you. This step works for all kind of messages, be it images, audio, stickers, text, ... you name it.
2. You can choose to ignore the message or reply to it. If you choose to reply to the forwarded message, the bot will send the text to the user at the other end of the conversation.

# Future improvements

- [x] Updated to Python v3.8
- [x] Updated to PythonTelegramBot v12.6.1
- [ ] Allow non-text replies
- [x] Implement multi-column keyboard in owner /help messages
- [ ] Update project to use the `logging` module

You can find the changelog [here](https://github.com/fndh/Anonymous-Telegram-Bot/wiki/Changelog)

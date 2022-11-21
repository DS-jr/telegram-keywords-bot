### Setup
- clone this repo
- create & activate a virtual environment named `env`
- install python3.10 (https://www.python.org/downloads/) # Python version 3.10 is necessary to run the bot 
- run `pip install -r requirements.txt`
- copy config_sample.ini to config.ini and edit it with your personal App api_id and api_hash (get here: https://my.telegram.org/auth?to=apps)
- start the bot with:
  - a) `python3.10 ./main.py` - to run the bot temporarily 
  - b) `nohup python3.10 ./main.py &` - to run the bot 24/7 on server as a background process

### (?) During the first session of running the bot with Python via Terminal:
- Pyrogram asks you to enter the phone number attached to your Telegram account (just digits including your Country Code digit(s), other symbols can be omitted)
- You’ll receive a confirmation code from Telegram
- If your Telegram account has two-step verification enabled - your password will be required 
- If you see ‘bot started’ phrase in Terminal - the bot is working 
- Three group chats (‘Keywords’, ‘Following’, ‘Mentions’) will appear in your Telegram account with `@MyLittleDummyBot` in every chat. The bot is needed to create a group (it takes 2 to make a group). You can set your name in `config.ini` with name `dummy_bot_name = MyLittleDummyBot `


### Commands
#### 1. Keywords bot
Forwards messages that contain specified keywords to 'Keywords' chat  
##### In ‘Keywords’ chat:
- `/help` - show a list of Keywords bot commands

> - /add keyword1 keyword2 ... - add new keyword(s) to global listener
> - /remove keyword1 keyword2 ... - remove keyword(s) from global listener
> - /show - show all keywords
> - /exclude_chat chat_title | chat_id | @username - exclude chat or user or channel from being monitored by Keywords bot (may work slowly, wait for bot's response)
> - /excluded_chats_list - show IDs of all excluded chats 
> - /delete_from_excluded_chats chat_id - delete a chat from your excluded chats list
> - /findid chat_title | first_name last_name | id | @username - find IDs & names of chats or users or channels (may work slowly, wait for bot's response) 
> - (??) `/forward_all_messages_from_chat` 
> chat_id - forward all messages from specific chat (selected by ID) to another chat. Use /findid command to get chats' IDs    
> - /removeall - remove all keywords from global listener (turned off currently)

#### 2. Mentions bot
Forwards to 'Mentions' chat all the messages where you were tagged (your TG account was mentioned). Replies to your messages are also counted as mentions 
#### 3. Following Bot
Forwards all messages from specified users to 'Following' chat  
##### In ‘Following’ chat:
- To follow a Telegram user: forward manually any message from this user to ‘Following’ chat
- /show - to check IDs of all Telegram users you are currently following
- /unfollow user_ID - to remove a user from the list of who you follow

### Pay attention:
- This bot is a Telegram client & an app. It is NOT a ‘usual TG bot via BotFather’, so do NOT create a new bot via BotFather 
- [Pyrogram](https://docs.pyrogram.org/) is used in the bot. It is [MTProto API](https://docs.pyrogram.org/topics/mtproto-vs-botapi) framework to interact with the main Telegram API 
- Data about your keywords & Telegram users who you follow is saved to config.ini file 

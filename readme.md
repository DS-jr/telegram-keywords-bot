## wip

### Setup
- clone this repo
- create & activate a virtual environment named `env`
- install python3.10 (https://www.python.org/downloads/) # Python version 3.10 is necessary to run the bot 
- run `pip install -r requirements.txt`
- copy config_sample.ini to config.ini and edit it with your personal App api_id and api_hash (get here: https://my.telegram.org/auth?to=apps)
- start the bot with:
  - a) `python3.10 ./main.py` - to run the bot temporarily 
  - b) `nohup python3.10 ./main.py &` - to run the bot 24/7 on server as a background process

### During the first session of running the bot with Python via Terminal:
- Pyrogram asks you to enter the phone number attached to your Telegram account (just digits including your Country Code digit(s), other symbols can be omitted)
- You’ll receive a confirmation code from Telegram
- If your Telegram account has two-step verification enabled - your password will be required 
- If you see ‘bot started’ phrase in Terminal - the bot is working 
- Three group chats (‘Keywords’, ‘Following’, ‘Mentions’) will appear in your Telegram account with @MyLittleDummyBot in every chat  

### Commands
- /help - shows a list of commands to use
#### I. Keywords bot
Forwards messages that contain specified keywords to 'Keywords' chat  
##### In ‘Keywords’ chat:
- /add keyword1 keyword2 ... - add new keyword(s) to global listener
- /remove keyword1 keyword2 ... - remove keyword(s) from global listener
- /exclude chat_name | chat_id | @username - exclude a chat from being monitored by Keywords feature  
- /show - show all keywords
- /findid @username | first_name last_name | chat_title - find Telegram IDs of individuals or chats or channels (may work slowly)  
- /removeall - remove all keywords from global listener (turned off currently)


#### II. Mentions bot
Forwards to 'Mentions' chat all the messages where you were tagged (your TG account was mentioned). Replies to your messages are also counted as mentions 

#### III. Following Bot
Forwards all messages from specified users to 'Following' chat  
##### In ‘Following’ chat:
- To follow a Telegram user: forward manually any message from this user to ‘Following’ chat
- /show - to check IDs of all Telegram users you are currently following
- /unfollow user_ID - to remove a user from the list of who you follow

### Pay attention:
- This bot is a Telegram client & an app. It is NOT a ‘usual TG bot via BotFather’, so do NOT create a new bot via BotFather 
- [Pyrogram](https://docs.pyrogram.org/) is used in the bot. It is [MTProto API](https://docs.pyrogram.org/topics/mtproto-vs-botapi) framework to interact with the main Telegram API 
- Info about your keywords & Telegram users who you follow is saved to config.ini file 

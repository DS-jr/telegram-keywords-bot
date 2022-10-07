## wip

### setup
- clone this repo
- create & activate a virtual environment named `env`
- install python3.10 (https://www.python.org/downloads/) # Python version 3.10 is necessary to run the bot 
- run `pip install -r requirements.txt`
- pay attention: [Pyrogram framework](https://docs.pyrogram.org/) is used in the bot
- copy config_sample.ini to config.ini and edit it with your personal api id and api hash (get here: https://my.telegram.org/auth?to=apps)
- start the bot with `python3.10 ./main.py`

### During the first session of running the bot with Python via Terminal:
- Pyrogram asks you to enter the phone number (attached to your Telegram account) 
- You’ll receive a confirmation code from Telegram
- If your Telegram account has two-step verification enabled - your password will be required 
- If you see ‘bot started’ phrase in Terminal - the bot is working 
- Three group chats (‘Keywords’, ‘Following’, ‘Mentions’) will appear in your Telegram account with @MyLittleDummyBot in every chat  

### commands
#### I. Keywords bot
forwards messages that contain specified keywords to Keywords chat
- /add keyword1 keyword2 ...etc - add new keyword(s) to global listener
- /remove keyword1 keyword2 ...etc - remove keyword(s) from global listener
- /removeall - remove all keywords from global listener (turned off currently)
- /show - show all keywords
- /findchat username|first name last name|chat title

#### II. Mentions bot
forwards all your mentions and message replies (counts as mentions) to Mentions chat
wip

#### III. Following Bot
forwards all messages from specified users to Following chat
todo

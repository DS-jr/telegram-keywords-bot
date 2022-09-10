# read config
config = ConfigParser()
config.read('config.ini')

# start app
user = Client('user')

# TODO catch 401 error when session is expired / removed, delete user.session file and try again
user.start()
user_info = user.get_me()

if(not config.has_section('bot_params')):
    config.add_section('bot_params')

if(not config.has_section('includes_dict')):
    config.add_section('includes_dict')

keywords = set(filter(None, config.get(
    'bot_params', 'keywords', fallback='').split(',')))
excluded_chats = set(filter(None, config.get(
    'bot_params', 'excluded_chats', fallback='').split(',')))
following_set = set(filter(None, config.get(
    'bot_params', 'following', fallback='').split(',')))
includes_dict = dict(config.items('includes_dict'))
for chat in includes_dict:
    includes_dict[chat] = set(filter(None, includes_dict[chat].split(',')))

dummy_bot_name = config.get(
    'bot_params', 'dummy_bot_name', fallback='MyLittleDummyBot')
keywords_chat_id = config.get('bot_params', 'keywords_chat_id', fallback='')
mentions_chat_id = config.get('bot_params', 'mentions_chat_id', fallback='')
following_chat_id = config.get('bot_params', 'following_chat_id', fallback='')

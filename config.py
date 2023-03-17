# read config
from configparser import ConfigParser

# config = ConfigParser()
# config.read('config.ini')

# if not config.has_section('bot_params'):
#     config.add_section('bot_params')
#
# if not config.has_section('includes_dict'):
#     config.add_section('includes_dict')

def read_config():
    config = ConfigParser()
    config.read('config.ini')

    if not config.has_section('bot_params'):
        config.add_section('bot_params')

    if not config.has_section('includes_dict'):
        config.add_section('includes_dict')

    return config

config = read_config()

keywords = set(filter(None, config.get(
    'bot_params', 'keywords', fallback='').split(',')))
excluded_chats = set(filter(None, config.get(
    'bot_params', 'excluded_chats', fallback='').split(',')))
following_set = set(filter(None, config.get(
    'bot_params', 'following', fallback='').split(',')))
includes_dict = dict(config.items('includes_dict'))
for chat in includes_dict:
    includes_dict[chat] = set(filter(None, includes_dict[chat].split(',')))


keywords_chat_id = config.get('bot_params', 'keywords_chat_id', fallback='')
mentions_chat_id = config.get('bot_params', 'mentions_chat_id', fallback='')
following_chat_id = config.get('bot_params', 'following_chat_id', fallback='')
backup_all_messages_chat_id = config.get('bot_params', 'backup_all_messages_chat_id', fallback='')
edited_and_deleted_chat_id = config.get('bot_params', 'edited_and_deleted_chat_id', fallback='')
pinned_messages_chat_id = config.get('bot_params', 'pinned_messages_chat_id', fallback='')
findid_chat_id = config.get('bot_params', 'findid_chat_id', fallback='')


def save_keywords(keywords):
    keywords = set(filter(None, keywords))
    config_set_and_save('bot_params', 'keywords', str(','.join(keywords)))


def save_excluded_chats(excluded_chats):
    excluded_chats = set(filter(None, excluded_chats))
    config_set_and_save('bot_params', 'excluded_chats',
                        str(','.join(excluded_chats)))


def save_following(following):
    following = set(filter(None, following))
    config_set_and_save('bot_params', 'following',
                        str(','.join(following)))


def add_keywords_to_includes(chat, keywords):
    if not chat in includes_dict:
        includes_dict[chat] = set()
    for keyword in keywords:
        includes_dict[chat].add(keyword)


def remove_keywords_from_includes(chat, keywords):
    if not chat in includes_dict:
        return
    for keyword in keywords:
        includes_dict[chat].discard(keyword)

    if keywords == ['all'] or len(includes_dict[chat]) == 0:
        del includes_dict[chat]


def save_includes(includes):
    config_2 = read_config()
    includes = set(filter(None, includes))
    for include in includes:
        config_2.set('chat_specific_keywords', include['id'], str(','.join(include['keywords'])))
    config_set_and_save(skip_set=True)


def config_set_and_save(section, param_name, param_value, skip_set=False):
    config_2 = read_config()
    if(not skip_set):
        config_2.set(section, param_name, param_value)
    with open('config.ini', 'w') as configfile:
        config_2.write(configfile)

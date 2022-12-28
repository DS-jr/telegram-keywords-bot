from configparser import ConfigParser

def create_configini_file():
    config = ConfigParser()
    config.read('config.ini')

    if not config.has_section('pyrogram'):
        config.add_section('pyrogram')
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    api_id = config.get('pyrogram', 'api_id', fallback=None)
    api_hash = config.get('pyrogram', 'api_hash', fallback=None)

    if not api_id:
        inputed_api_id = input("Paste your Telegram App's `api_id' here: ")
        # check if the string inputed_api_id is empty
        config.set('pyrogram', 'api_id', inputed_api_id)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    if not api_hash:
        inputed_api_hash = input("Paste your Telegram App's `api_hash' here: ")
        # check if the string inputed_api_hash is empty
        config.set('pyrogram', 'api_hash', inputed_api_hash)
        with open('config.ini', 'w') as configfile:
            config.write(configfile)

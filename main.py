from first_session import create_configini_file
from bot import start_bot

if __name__ == '__main__':
    create_configini_file()  # Should this line be here or below?
    start_bot()

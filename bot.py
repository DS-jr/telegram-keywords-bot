import re
from pyrogram import Client, filters, idle
# from datetime import datetime
from config import config, keywords_chat_id, following_chat_id, mentions_chat_id, backup_all_messages_chat_id, \
    edited_and_deleted_chat_id, pinned_messages_chat_id, findid_chat_id, keywords, save_keywords, excluded_chats, \
    save_excluded_chats, add_keywords_to_includes, includes_dict, following_set, save_following, config_set_and_save
# from threading import Timer

# start app
user = Client('user')

# init chats
chat_dict = {
    "Keywords": "keywords_chat_id",
    "Mentions": "mentions_chat_id",
    "Following": "following_chat_id",
    "Backup_all_messages": "backup_all_messages_chat_id", # (?) Rename the chat to 'Dump_from_chat' OR 'Backup_from_chat'
    "Edited_and_Deleted_messages_monitoring": "edited_and_deleted_chat_id",
    "Pinned_messages": "pinned_messages_chat_id",
    "Find_Telegram_ID": "findid_chat_id"
}


def is_id(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


def find_chats(client, args):
    dialogs = []
    if len(args) == 1 and (is_id(args[0]) or args[0][0] == '@'):
        try:
            chat = client.get_chat(args[0])
            dialogs.append([str(chat.id), str(chat.title) if chat.title else str(
                chat.first_name) + ' ' + str(chat.last_name)])
        except:
            return dialogs
    else:
        for dialog in client.iter_dialogs():
            searchStr = ' '.join((str(dialog.chat.title), str(dialog.chat.first_name),
                                  str(dialog.chat.last_name), '@' + str(dialog.chat.username)))
            if re.search(' '.join(args), searchStr, re.IGNORECASE):
                dialogs.append([str(dialog.chat.id), str(dialog.chat.title) if dialog.chat.title else str(
                    dialog.chat.first_name) + ' ' + str(dialog.chat.last_name)])
    return dialogs


def find_users(client, args):
    result = []
    users = client.get_users(args)
    for user in users:
        result.append(
            [str(user.id),
             ' '.join(list(filter(None, [user.first_name, user.last_name])))
             ]
        )
    return result


def get_history_count(from_chat_id):   #  ? (test) Is this function necessary
    pass


def backup_all_messages(client, from_chat_id):
    from_chat_full_message_history = client.get_history_count(from_chat_id)
    if from_chat_full_message_history == 0:
        client.send_message(backup_all_messages_chat_id,
                            f"Sorry, NO messages to backup: chat {from_chat_id} is empty.\n Try to use another from_chat_id"
                            )
        return # (?) Test in TG if this solution works fine
    backup_all_messages_chat_size = client.get_history_count(backup_all_messages_chat_id)
    skipped_service_messages = 0
    counter = 0
    # current_time = int(datetime.now().timestamp())
    for message in client.iter_history(from_chat_id):  # iter_history is used in Pyrogram v.1.4. instead of get_chat_history in v2.0.
        counter += 1
        if message.service:
            skipped_service_messages += 1
            continue
        # message_datetime = datetime.fromtimestamp(message.date)
        # client.send_message(chat_id=backup_all_messages_chat_id,
        #                     text=message_datetime.strftime("%A, %d. %B %Y %I:%M%p")) # To show the exact time
        # Timer(counter * 50, message.forward(backup_all_messages_chat_id)).start()
        message.forward(backup_all_messages_chat_id)
        #message.forward(backup_all_messages_chat_id, schedule_date=current_time + counter);
        #forwarded_message = message.forward(backup_all_messages_chat_id)
        #print(forwarded_message.id, forwarded_message.text)
    forward_chat_full_message_history = client.get_history_count(backup_all_messages_chat_id)
    client.send_message(backup_all_messages_chat_id,
                        "RESULTS:\n"
                        f"Forwarding of all messages from chat with chat_ID {from_chat_id} is FINISHED\n"
                        f"Size of your chat to forward from: {from_chat_full_message_history} messages\n"
                        f"Number of messages forwarded by bot: {forward_chat_full_message_history - backup_all_messages_chat_size}\n"
                        f"Number of service messages skipped by bot (Ex.: 'joined chat', 'removed from chat', 'pinned message', etc): {skipped_service_messages}\n"
                        "/help - show Help options"
                        )

############## bot commands handlers #################

# Commands used in all bot chats in Telegram ("Keywords"; "Mentions"; "Following"; etc.) must be listed here:
filtered_commands_list = ['help', 'help_general', 'add', 'show', 'remove', 'findid', 'exclude_chat', 'excluded_chats_list',
                          'delete_from_excluded_chats', 'backup_all_messages', 'include', 'follow', 'unfollow']

list_of_ids_of_all_created_chats = [keywords_chat_id, following_chat_id, mentions_chat_id,backup_all_messages_chat_id,
                                    edited_and_deleted_chat_id, pinned_messages_chat_id, findid_chat_id]

help_general_text = """
...
(Beverly Sills) There are NO short cuts to any place worth going. 
...
""" # (?) Add text w/ all instructions from the final version of ReadMe AFTER main changes in code are finished

# command messages listener
@user.on_message(filters.me & ~filters.edited & filters.command(filtered_commands_list))
def command_messages_handler(client, message):
    # accept commands only for bot chat ids
    if not message.chat or not str(message.chat.id) in list_of_ids_of_all_created_chats:
        return

    chat_id = str(message.chat.id)

    if chat_id == keywords_chat_id:
        keywords_handler(client, message)
    elif chat_id == following_chat_id:
        following_handler(client, message)
    elif chat_id == mentions_chat_id:
        mentions_handler(client, message)
    elif chat_id == backup_all_messages_chat_id:
        backup_all_messages_handler(client, message)
    elif chat_id == edited_and_deleted_chat_id:
        edited_and_deleted_chat_input_handler(client, message)
    elif chat_id == pinned_messages_chat_id:
        pinned_messages_chat_input_handler(client, message)
    elif chat_id == findid_chat_id:
        findid_input_handler(client, message)


# (?) Variant N2:
@user.on_message(filters.me & ~filters.edited & ~filters.command(filtered_commands_list))
def not_command_handler(client, message):  # (?) Draft
    # accept commands only for bot chat ids
    if not message.chat or not str(message.chat.id) in list_of_ids_of_all_created_chats:
        return # (?) Add some text reply outputed to user via TG? (Ex.: "NOT valid. Try again")
    # (Variant 1) (How to follow a TG user) Forward manually any message of this user to your 'Following' chat
    # listen to messages forwarded manually by me to catch them in "Following" chat
    if message.forward_from and str(message.chat.id) == following_chat_id:
        if str(message.forward_from.id) in following_set:
            message.reply('Following already works for id {}'.format(
                message.forward_from.id))
        else:
            following_set.add(str(message.forward_from.id))
            save_following(following_set)
            message.reply('id {} is added to Following list'.format(
                message.forward_from.id))
        return # (?) Add some text reply outputed to user via TG? (Ex.: "NOT valid. Try again")

    message.reply_text( # (?) Is this line used in the correct place? As I've added code below
        'Sorry, this command is NOT valid. Enter /help to see all valid commands'
    )

    # Variant N2 to find Telegram ID via forwarding a message from a target chat to “FindID” chat
    # listen to messages forwarded manually by me to catch them in "Find_Telegram_ID" chat
    if message.forward_from and str(message.chat.id) == findid_chat_id:
        message.reply('The chat (user / group / channel / bot / etc.) you\'ve just forwarded a message from '
                      'has Telegram ID: {} '.format(message.forward_from.id)
                      )
    else:
        message.reply_text('Please, try another way to find Telegram ID. Enter /help')


# "Mentions" chat handler
def mentions_handler(client, message):
    args = message.command
    comm = args.pop(0)
    # print("priNt 'args':", args) # CDL (for testing purposes)
    # print("priNt 'comm':", comm) # CDL (for testing purposes)
    match comm:
        case 'help_general':
            message.reply_text(help_general_text)
        case 'help':
            message.reply_text(
                '/help - show Help options for this chat\n'
                '/help_general - show Help options for all chats\n\n'
                '"Mentions" chat works automatically\n'
                'No need to enter any input in "Mentions" chat\n\n'
                'Messages from all chats where your TG account was mentioned (tagged) will be forwarded to "Mentions" chat\n'
                'Replies to your messages are also counted as mentions'
            )
        case _:
            message.reply_text('Sorry, this command is not valid')


# "Edited_and_Deleted_messages_monitoring" chat handler
def edited_and_deleted_chat_input_handler(client, message): # (?) Or two SEPARATE handlers necessary for “Edited” & for “Deleted”?
    args = message.command
    comm = args.pop(0)
    match comm:
        case 'help_general':
            message.reply_text(help_general_text)
        case 'help':
            message.reply_text(
                '/help - show Help options for this chat\n'
                '/help_general - show Help options for all chats\n\n'
                '"Edited_and_Deleted_messages_monitoring" chat works automatically\n'
                'No need to enter any input in this chat\n\n'
                '..??..  \n'
                '(?) ADD here the text description of this feature from the final version of ReadMe ..??..\n'
            )
        case _:
            message.reply_text('Sorry, this command is not valid')


# "Pinned_messages" chat handler
def pinned_messages_chat_input_handler(client, message):
    args = message.command
    comm = args.pop(0)
    match comm:
        case 'help_general':
            message.reply_text(help_general_text)
        case 'help':
            message.reply_text(
                '/help - show Help options for this chat\n'
                '/help_general - show Help options for all chats\n\n'
                'Pinned messages from all chats are automatically forwarded to your "Pinned_messages" chat\n'   
                'No need to enter any input in this chat'
            )
        case _:
            message.reply_text('Sorry, this command is not valid')


# "Find_Telegram_ID" chat handler
def findid_input_handler(client, message):
    args = message.command
    comm = args.pop(0)
    match comm:
        case 'help_general':
            message.reply_text(help_general_text)
        case 'help':
            message.reply_text(
                '/help - show Help options for this chat\n'
                '/help_general - show Help options for all chats\n\n'
                'To find Telegram ID of any chat (user / group / channel / bot / etc.):\n'
                '\tVariant 1: Enter manually in "Find_Telegram_ID" chat: /findid @username | first_name last_name | chat_title\n'
                '\tVariant 2: Forward manually any message from target chat to "Find_Telegram_ID" chat. Get automatic reply with target chat ID\n\n' 
                '(Finding IDs may work slowly. Wait for Bot\'s reply)\n'
            )
        case 'findid':
            if (not args):
                return message.reply_text('Smth must be entered manually after /findid command: chat_title | first_name last_name | @username')
            dialogs = find_chats(client, args)
            message.reply_text('\n'.join([' - '.join(dialog) for dialog in dialogs]) if len(
                dialogs) else 'Sorry, nothing is found. Enter manually after /findid - chat_title | first_name last_name | @username')
        case _:
            message.reply_text('Sorry, this command is not valid')


# "Backup_all_messages" chat handler
def backup_all_messages_handler(client, message):
    args = message.command
    comm = args.pop(0)
    match comm:
        case 'help_general':
            message.reply_text(help_general_text)
        case 'help':
            message.reply_text(
                '/help - show Help options for this chat\n'
                '/help_general - show Help options for all chats\n'
                '/findid @username | first_name last_name | chat_title - find from_chat_id (may work slowly)\n\n'
                '/backup_all_messages from_chat_id -\n'
                'All messages from a single selected chat are copied & forwarded to "Backup_all_messages" chat\n' 
                'Single-time manual backup (NOT automatic, NOT real time monitoring)\n'
            )
        case 'backup_all_messages': # (?)
            if len(args) == 0:
                message.reply_text('Sorry, from_chat_id is not found\n'
                                   'from_chat_id (Telegram ID of the chat to backup messages from) must be entered manually after /backup_all_messages\n\n'
                                   'Please, use this format: /backup_all_messages from_chat_id\n'
                                   'Use /findid to get from_chat_id')  # chat_title | chat_id | @username
            if len(args) > 1:
                message.reply_text('Wrong input:\n' + '\n'.join([arg for arg in args]) + '\n\nPlease enter a single valid from_chat_id after /backup_all_messages')
            if len(args) == 1:
                from_chat_id = args[0]
                try:
                    from_chat_id = int(from_chat_id)
                except ValueError:
                    message.reply("Sorry, from_chat_id is not valid\n "
                                  "from_chat_id (Telegram ID of the chat to backup messages from) must be entered manually after /backup_all_messages\n\n"
                                  'Please, use this format: /backup_all_messages from_chat_id\n'
                                  "Use /findid to get from_chat_id")
                backup_all_messages(user, args[0])
        case 'findid': # (?)
            if (not args):
                return message.reply_text('Smth must be entered manually after /findid command: chat_title | first_name last_name | @username')
            dialogs = find_chats(client, args)
            message.reply_text('\n'.join([' - '.join(dialog) for dialog in dialogs]) if len(
                dialogs) else 'Sorry, nothing is found. Enter manually after /findid - chat_title | first_name last_name | @username')
        case _:
            message.reply_text('Sorry, this command is not valid')


# "Keywords" chat handler
def keywords_handler(client, message):
    args = message.command
    comm = args.pop(0)
    match comm:
        case 'help_general':
            message.reply_text(help_general_text)
        case 'help':
            message.reply_text(
                '/help - show Help options for this chat\n'
                '/help_general - show Help options for all chats\n'
                '/findid chat_title | first_name last_name | id | @username` - find Telegram ID of chat / user / channel (may work slowly)\n' 
                '/show - show all keywords monitored by bot\n'
                '/add keyword1 keyword2 ... - add new keyword(s)\n'
                '/remove keyword1 keyword2 ... - remove keyword(s)\n'
                '/exclude_chat chat_title | chat_id | @username - exclude chat or user or channel from being monitored by Keywords bot (may work slowly)\n'
                '/excluded_chats_list - show IDs of all excluded chats\n' 
                '/delete_from_excluded_chats chat_id - delete a chat from your excluded chats list\n'
                '/removeall - remove all keywords (turned off currently)\n'
            )
        case 'add':
            for keyword in args:
                keywords.add(keyword.strip().replace(',', ''))
            message.reply_text('processed ' + str(len(args)) + ' keywords')
            save_keywords(keywords)
        case 'show':
            if not keywords:
                message.reply_text('No keywords, add with /add command')
            else:
                message.reply_text('keywords: #' + ', #'.join(keywords))
        case 'remove':
            for keyword in args:
                keywords.discard(keyword.strip().replace(',', ''))
            message.reply_text('processed ' + str(len(args)) + ' keywords')
            save_keywords(keywords)
        case 'removeall':
            message.reply_text('removed ' + str(len(keywords)) + ' keywords')
            keywords.clear()
            save_keywords(keywords)
        case 'findid':
            if(not args):
                return message.reply_text("Smth must be entered manually after /findid command: chat_title | first_name last_name | id | @username")
            dialogs = find_chats(client, args)
            message.reply_text('\n'.join([' - '.join(dialog) for dialog in dialogs]) if len(
                dialogs) else 'Sorry, nothing is found. Enter manually after /findid - chat_title | chat_id | @username')
        case 'exclude_chat':
            if not args:
                return
            dialogs = find_chats(client, args)
            if(len(dialogs) != 1):
                message.reply_text('More than one chat is found:\n' + '\n'.join([' - '.join(
                    dialog) for dialog in dialogs]) if len(dialogs) else 'Sorry, nothing is found. Paste manually after /exclude_chat - chat_title | chat_id | @username')
            else:
                excluded_chats.add(dialogs[0][0])
                save_excluded_chats(excluded_chats)
                message.reply_text(
                    'This chat was added to excluded chats list:\n' + ' - '.join(dialogs[0]))
        case 'excluded_chats_list':
            dialogs = find_chats(client, args)  # ?
            if not excluded_chats:
                message.reply_text('No excluded chats yet')
            else:
                chatid_chatname_string = ""
                for chat_id in excluded_chats:
                    for dialog in dialogs:
                        if dialog[0] == chat_id:
                            chatid_chatname_string += 'Chat ID: ' + str(chat_id) + ' \tChat name: ' + str(dialog[1]) + '\n'
                message.reply_text('Excluded chats:\n' + chatid_chatname_string)
        case 'delete_from_excluded_chats':
            if not args or not args[0] in excluded_chats:
                message.reply('Not found, use chat_id from your list of excluded chats')
            else:
                excluded_chats.discard(args[0])
                save_excluded_chats(excluded_chats)
                message.reply('{} - this chat was deleted from your list of excluded chats'.format(args[0]))
        case 'include':
            if len(args) < 2:
                return
            chat_name = args.pop(0)
            dialogs = find_chats(client, [chat_name])
            if(len(dialogs) != 1):
                message.reply_text('More than one chat is found:\n' + '\n'.join([' - '.join(
                    dialog) for dialog in dialogs]) if len(dialogs) else 'Sorry, nothing is found')
            else:
                add_keywords_to_includes(dialogs[0][0], args)
                message.reply_text('Keywords #{} for the chat:\n'.format(', #'.join(
                    includes_dict[dialogs[0][0]])) + ' - '.join(dialogs[0]))
        case _:
            message.reply_text('Sorry, this command is not valid')

# "Following" chat handler
def following_handler(client, message):
    if str(message.chat.id) != following_chat_id: # (?) Why using this line here?
        return
    args = message.command
    comm = args.pop(0)
    match comm:
        case 'help_general':
            message.reply_text(help_general_text)
        case 'help':
            message.reply_text(
                '/help - show Help options for this chat\n'
                '/help_general - show Help options for all chats\n\n'
                'To follow a Telegram user:\n'
                '\tVariant 1: forward manually any message of this user to your "Following" chat\n'
                '\tVariant 2: /follow user_ID   # Enter /findid manually to get user_ID\n\n'
                '/show - check IDs of all Telegram users in your current "Following" list\n'
                '/unfollow user_ID - remove a user from your "Following" list\n'
                '/findid @username | first_name last_name | chat_title - find user_ID (may work slowly)'
            )
        case 'findid':
            if (not args):
                return message.reply_text('Smth must be entered manually after /findid command: chat_title | first_name last_name | id | @username')
            dialogs = find_chats(client, args)
            message.reply_text('\n'.join([' - '.join(dialog) for dialog in dialogs]) if len(
                dialogs) else 'Sorry, nothing is found. Paste manually after /findid - @username | first_name last_name | chat_title')
        case 'show':
            message.reply('\n'.join([' - '.join(user) for user in find_users(
                client, following_set)]) if following_set else 'The list is empty')
        case 'unfollow':
            if not args or not args[0] in following_set:
                message.reply('Not found')
            else:
                following_set.discard(args[0])
                save_following(following_set)
                message.reply('{} Deleted from Following'.format(args[0]))
        # (Variant 2) (How to follow a TG user) Follow via inputing manually user's TG id
        case 'follow':
            if len(args) == 0:
                message.reply_text('Sorry, ID is not found. Enter manually Telegram ID of the target user after /follow\n'
                                   'Use /findid to get Telegram ID')  # chat_title | chat_id | @username
            if len(args) > 1:
                message.reply_text('More than one ID entered:\n' + '\n'.join([arg for arg in args]) + '\n\nPlease enter a single valid ID after /follow')
            if len(args) == 1:
                user_id = args[0]
                try:
                    user_id = int(user_id)
                except ValueError:
                    message.reply("Sorry, ID is not valid. Enter manually valid Telegram ID of the target user after /follow\n"
                                  "Use /findid to get Telegram ID")
                if user_id in following_set:
                    message.reply('Following already works for id {}'.format(user_id))  # ..??..
                else:
                    following_set.add(user_id)
                    save_following(following_set)
                    message.reply_text('This ID was added to "following" list:\n' + user_id)
        case _:
            message.reply('Sorry, this command is not valid')


# process incoming messages
# limit to <not me> : ~filters.me (by config?)
# exclude forwards ?
# limit to some types of updates (plain text?)
# limit to private chats / groups / channels (by config?)

# b1: search for keywords
# b2: limit to mentions

# listen to only other users' messages;
# skip message edits for now (TODO: handle edited messages) (?)
@user.on_message(~filters.me & ~filters.edited)  # (?)
def not_my_messages_handler(client, message):
    # process keywords
    if message.text and not str(message.chat.id) in excluded_chats:
        # maybe search -> findall and mark all keywords?
        keyword = re.search("|".join(keywords),
                            message.text, re.IGNORECASE)
        if len(keywords) and keyword:
            keywords_forward(client, message, keyword.group())
    # process mentions
    # message can be a reply with attachment with no text
    if message.mentioned:
        mentions_forward(client, message)
    # process following
    if message.from_user and str(message.from_user.id) in following_set:
        following_forward(client, message)


# process Pinned messages
@user.on_message(filters.pinned_message)
def pinned_messages_handler(client, message):
    pinned_messages_forward(client, message)


# process Deleted messages
@user.on_deleted_messages(~filters.me)  # (?) "NOT-me" filter does NOT work correctly now
def deleted_messages_handler(client, message): # https://docs.pyrogram.org/api/decorators#pyrogram.Client.on_deleted_messages
    # print("2. (Watts)  At EVERY moment of life: you are already “there” = liberated = enlightened = in the optimal place / state / moment = where you tried & dreamed to get."!
    deleted_messages_forward(client, message)


# process Edited messages
# Variant N2   *** https://docs.pyrogram.org/api/decorators#pyrogram.Client.on_message
@user.on_message(~filters.me & filters.edited & filters.private) # (?)
def edited_messages_handler(client, message):
    edited_messages_forward(client, message)
# process Edited messages
# Variant N1.  *** on_edited_message decorator did NOT work for Pyrogram 1.4  https://docs.pyrogram.org/api/decorators#pyrogram.Client.on_edited_message
# @user.on_edited_message(~filters.me)  # (?)
# def edited_messages_handler(client, message):
#     if message: # (?)
#         edited_messages_forward(client, message)  # (?)



def make_user_mention(user):
    name = str(user.first_name) + ' ' + str(user.last_name).strip()
    return '[{}](tg://user?id={})'.format(name, user.id)


def make_message_description(message):
    # Direct Messages
    if message.chat.type == 'private':
        source = 'in Direct Messages ({})'.format(make_user_mention(message.from_user))
    # Channels
    elif message.chat.type == 'channel':
        source = 'in channel {} @{}'.format(message.chat.title,
                                          message.chat.username)
    # Groups and Supergroups
    else:
        source_chat_name = str(
            message.chat.title) if message.chat.title else '<unnamed chat>'
        source_chat_link = ' @' + \
            str(message.chat.username) if message.chat.username else ''
        source = 'in chat "{}" {} by {}'.format(
            source_chat_name, source_chat_link, make_user_mention(message.from_user))

    # forward of forward loses the first person
    if message.forward_from:
        return '{}, forwarded from - {}'.format(source, make_user_mention(message.forward_from))

    return source


def keywords_forward(client, message, keyword):
    source = make_message_description(message)
    client.send_message(
        keywords_chat_id, '#{} {}'.format(keyword, source))
    message.forward(keywords_chat_id)
    client.mark_chat_unread(keywords_chat_id)


def mentions_forward(client, message):
    source = make_message_description(message)
    client.send_message(
        mentions_chat_id, 'Mentioned {}'.format(source))
    message.forward(mentions_chat_id)
    client.mark_chat_unread(mentions_chat_id)


def following_forward(client, message):
    source = make_message_description(message)
    client.send_message(
        following_chat_id, 'Action detected {}'.format(source))
    message.forward(following_chat_id)
    client.mark_chat_unread(following_chat_id)


def deleted_messages_forward(client, message):
    # source = make_message_description(message)
    # client.send_message(
    #     edited_and_deleted_chat_id, 'Deleted message {}:'.format(source))
    # message.forward(edited_and_deleted_chat_id)
    client.send_message(edited_and_deleted_chat_id, "Deleted message detected:\n"
                                                    f"message_id: {message[0]['message_id']}\n"
                                                    "(?) Date & time of deletion: ... \n" # (?) Try tu use message_id OR just use the time of the notification
                                                    "(later feature) Chat ID where deletion happened: ...\n"  # (?) Try to use message_id 
                                                    "(later feature) Original message BEFORE being deleted: ..."
                        )
    client.mark_chat_unread(edited_and_deleted_chat_id)


def edited_messages_forward(client, message):
    source = make_message_description(message)
    client.send_message(
        edited_and_deleted_chat_id, 'Message AFTER being edited {}:'.format(source))
    message.forward(edited_and_deleted_chat_id)
    client.mark_chat_unread(edited_and_deleted_chat_id)


def pinned_messages_forward(client, message):
    source = make_message_description(message)
    client.send_message(
        pinned_messages_chat_id, 'Pinned message {}:'.format(source))
    message.forward(pinned_messages_chat_id)
    client.mark_chat_unread(pinned_messages_chat_id)


def start_bot():
    # TODO catch 401 error when session is expired / removed, delete user.session file and try again
    user.start()
    user_info = user.get_me()

    for k in chat_dict:
        if not globals()[chat_dict[k]]: # (?) How does this line work for the first session launch?
            new_chat = user.create_group(k, user_info.id)
            globals()[chat_dict[k]] = new_chat.id
            config_set_and_save('bot_params', chat_dict[k], str(new_chat.id))
    # init message
    # user.send_message(keywords_chat_id, 'bot started')
    # user.send_message(mentions_chat_id, 'bot started')
    # user.send_message(following_chat_id, 'bot started')
    print('bot started')
    idle()

    # stop message
    # user.send_message(keywords_chat_id, 'bot stopped')
    # user.send_message(mentions_chat_id, 'bot stopped')
    # user.send_message(following_chat_id, 'bot stopped')
    print('stopping bot...')
    user.stop()
    print('bot stopped')

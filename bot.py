import re
from pyrogram import Client, filters, idle
# from datetime import datetime
from config import config, keywords_chat_id, following_chat_id, mentions_chat_id, forward_all_messages_chat_id, keywords, save_keywords, \
    excluded_chats, save_excluded_chats, add_keywords_to_includes, includes_dict, following_set, save_following, \
    dummy_bot_name, config_set_and_save
# from threading import Timer

# start app
user = Client('user')

# init chats
chat_dict = {
    "Keywords": "keywords_chat_id",
    "Mentions": "mentions_chat_id",
    "Following": "following_chat_id",
    "Forward_all_messages_from_chat": "forward_all_messages_chat_id"
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


def forward_all_messages_from_chat(client, from_chat_id):
    forward_all_messages_chat_size = client.get_history_count(forward_all_messages_chat_id)
    skipped_service_messages = 0
    counter = 0
    # current_time = int(datetime.now().timestamp())
    # print(datetime.now(), current_time)
    for message in client.iter_history(from_chat_id):  # iter_history is used in Pyrogram v.1.4. instead of get_chat_history in v2.0.
        counter += 1
        if message.service:
            skipped_service_messages += 1
            continue
        # message_datetime = datetime.fromtimestamp(message.date)
        # client.send_message(chat_id=forward_all_messages_chat_id,
        #                     text=message_datetime.strftime("%A, %d. %B %Y %I:%M%p")) # To show the exact time
        # Timer(counter * 50, message.forward(forward_all_messages_chat_id)).start()
        message.forward(forward_all_messages_chat_id)
        #message.forward(forward_all_messages_chat_id, schedule_date=current_time + counter);
        #forwarded_message = message.forward(forward_all_messages_chat_id)
        #print(forwarded_message.id, forwarded_message.text)
    from_chat_full_message_history = client.get_history_count(from_chat_id)
    forward_chat_full_message_history = client.get_history_count(forward_all_messages_chat_id)
    client.send_message(keywords_chat_id, f"Size of your chat to forward from: {from_chat_full_message_history} messages")
    client.send_message(keywords_chat_id, f"Number of messages forwarded by bot (to 'Forward_all_messages_from_chat' chat in your TG account): {forward_chat_full_message_history - forward_all_messages_chat_size}")
    client.send_message(keywords_chat_id, f"Number of service messages (Ex.: 'joined chat', 'removed from chat', 'pinned message', etc) skipped by bot: {skipped_service_messages}")
    client.send_message(keywords_chat_id, f"Forwarding from chat with chat_ID {from_chat_id} to chat with chat_ID {forward_all_messages_chat_id} is finished")

    # from_chat = client.get_chat(from_chat_id)
    # forward_all_messages_chat = client.get_chat(forward_all_messages_chat_id)
    # client.send_message(keywords_chat_id, f"Forwarding from chat [{from_chat.first_name} {from_chat.last_name}](tg://resolve?domain={from_chat_id}) to chat {forward_all_messages_chat.title} is finihsed", "markdown")


    # user.send_message(keywords_chat_id, 'Size of your chat to forward from: ', client.get_history_count(from_chat_id), ' messages')
    # user.send_message(keywords_chat_id, 'Number of messages forwarded by bot (to "Forward_all_messages_from_chat" chat in your TG account): ', client.get_history_count(forward_all_messages_chat_id) - forward_all_messages_chat_size)
    # user.send_message(keywords_chat_id, "Number of service messages (Ex.: 'joined chat', 'removed from chat', 'pinned message', etc) skipped by bot: ", skipped_service_messages)
    # client.send_message(keywords_chat_id, 'aCCept')


    # print('Size of your chat to forward from: ', client.get_history_count(from_chat_id), ' messages')
    # print('Number of messages forwarded by bot (to "Forward_all_messages_from_chat" chat in your TG account): ', client.get_history_count(forward_all_messages_chat_id) - forward_all_messages_chat_size)
    # print("Number of service messages (Rx.: 'joined chat', 'removed from chat', 'pinned message', etc) skipped by bot: ", skipped_service_messages)

    # print(type(client.iter_history(from_chat_id))) # <class 'pyrogram.types.list.List'>
    # client.send_message(chat_id=forward_all_messages_chat_id, text=..??..)

    # async def forward_all_messages_from_chat(client, from_chat_id, to_chat_id):
        #     async with client:
        #         async for message in client.iter_history(from_chat_id):  # iter_history is used in Pyrogram v.1.4. instead of get_chat_history in v2.0.
        #             if message.service:
        #                 continue
        #             message_datetime = datetime.fromtimestamp(message.date)
        #             await client.send_message(chat_id=to_chat_id, text=message_datetime.strftime("%A, %d. %B %Y %I:%M%p")) # To show the exact time
        #             await message.forward(to_chat_id)
        #
        # user.run(forward_all_messages_from_chat(user, 5481261145, -1001706720944))  # Substitute from_chat_id & to_chat_id manually with chat IDs here (use bot's /findid command to get chat IDs)


############## bot commands handlers #################

# command messages listener
@user.on_message(filters.me & ~filters.edited & filters.command(['help', 'add', 'show', 'remove', 'findid', 'exclude_chat', 'excluded_chats_list', 'delete_from_excluded_chats', 'forward_all_messages_from_chat', 'include', 'follow', 'unfollow']))
def commHandler(client, message):
    # accept commands only for bot chat ids
    if not message.chat or not str(message.chat.id) in (keywords_chat_id, following_chat_id, mentions_chat_id, forward_all_messages_chat_id):
        return

    chat_id = str(message.chat.id)

    if chat_id == keywords_chat_id:
        kwHandler(client, message)
    elif chat_id == following_chat_id:
        fwHandler(client, message)

# keywords chat handler
def kwHandler(client, message):
    args = message.command
    comm = args.pop(0)

    match comm:
        case 'help':
            message.reply_text(
                '/add keyword1 keyword2\n/show\n/remove keyword1 keyword2\n/removeall\n/findid chat_title|name|id|@username\n/exclude_chat chat_title|id|@username\n/excluded_chats_list\n/delete_from_excluded_chats chat_id\n/forward_all_messages_from_chat from_chat_id\n/include name|id|@username keywords')
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
                return
            dialogs = find_chats(client, args)
            message.reply_text('\n'.join([' - '.join(dialog) for dialog in dialogs]) if len(
                dialogs) else 'Sorry, nothing is found. Paste manually after /findid - chat_title | chat_id | @username')
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
        case 'forward_all_messages_from_chat':
            if not args:
                message.reply_text('Please, use this format: /forward_all_messages_from_chat from_chat_id  |  Use /findid command to get from_chat_id & paste it manually')
            else:
                forward_all_messages_from_chat(user, args[0])
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

# forwards chat handler
def fwHandler(client, message):
    if str(message.chat.id) != following_chat_id:
        return
    # print(message)
    args = message.command
    comm = args.pop(0)
    match comm:
        case 'show':
            message.reply('\n'.join([' - '.join(user) for user in find_users(
                client, following_set)]) if following_set else 'The list is empty')

        # (Variant 2) (How to follow a TG user) Follow via inputing manually user's TG id
        case 'follow':
            print(args, " - printed 'args'")  # CDL
            # print(args[0], " - printed 'args[0]'")  # CDL
            # print(comm)  # CDL

# (!!) (PROCEED)  Probably it's necessary to delete ALL "dialogs"  =>  Use "args" & write code on my own.  ***Check the latest output in iTerm
            if len(args) == 0:
                message.reply_text('Sorry, ID is not found. Enter manually Telegram ID of the target user after /follow')  # chat_title | chat_id | @username
            if len(args) > 1:
                message.reply_text('More than one ID entered:\n' + '\n'.join([arg for arg in args]) + '\n\nPlease enter a single valid ID after /follow')
            if len(args) == 1:
                if args[0] in following_set:  # ..??..  ***OR just "if" is necessary here?
                    message.reply('Following already works for id {}'.format(args[0]))  # ..??..
                else:
                    following_set.add(args[0])
                    save_following(following_set)
                    message.reply_text('This ID was added to "following" list:\n' + args[0])

            # dialogs = find_chats(client, args) # Finds list of lists with ID & name of all contacts of this user
            # print(dialogs, dialogs[0][0], " - priNted from bot.py foR tEsting purPoses, CDL!")   #  ?  (CDL this line!)

            # if not args:
            #     message.reply('Enter ID of TG user via "/follow user_ID" command')


            # Example block of code: DELETE it later!
            # if str(message.chat.id) in following_set:  # ..??..  (Substitute "message" )
            #             message.reply('Following already works for id {}'.format(
            #                 message.forward_from.id))  # ..??..  (Substitute forward_from !)
                    # else:
                    #     following_set.add(str(message.forward_from.id))  # ..??..  (Substitute forward_from !)
                    #     save_following(following_set)
                    #     message.reply('id {} is added to Following list'.format(
                    #         message.forward_from.id))  # ..??..  (Substitute forward_from !)


        # case 'exclude_chat':  # Example block of code: DELETE it later!
        #     if not args:
        #         return
        #     dialogs = find_chats(client, args)
        #     if(len(dialogs) != 1):
        #         message.reply_text('More than one chat is found:\n' + '\n'.join([' - '.join(
        #             dialog) for dialog in dialogs]) if len(dialogs) else 'Sorry, nothing is found. Paste manually after /exclude_chat - chat_title | chat_id | @username')
        #     else:
        #         excluded_chats.add(dialogs[0][0])
        #         save_excluded_chats(excluded_chats)
        #         message.reply_text(
        #             'This chat was added to excluded chats list:\n' + ' - '.join(dialogs[0]))

    # listen to user messages to catch forwards for following chat
    # @user.on_message(filters.me & ~filters.edited)
    # def myHandler(client, message):
    #     if str(message.chat.id) != following_chat_id:
    #         return
    #     if message.forward_from:
    #         if str(message.forward_from.id) in following_set:
    #             message.reply('Following already works for id {}'.format(
    #                 message.forward_from.id))
    #         else:
    #             following_set.add(str(message.forward_from.id))
    #             save_following(following_set)
    #             message.reply('id {} is added to Following list'.format(
    #                 message.forward_from.id))

        case 'unfollow':
            if not args or not args[0] in following_set:
                message.reply('Not found')
            else:
                following_set.discard(args[0])
                save_following(following_set)
                message.reply('{} Deleted from Following'.format(args[0]))
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
# skip message edits for now (TODO: handle edited messages)
@user.on_message(~filters.me & ~filters.edited)
def notmyHandler(client, message):
    # print(message)
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

# (Variant 1) (How to follow a TG user) Follow via forwarding manually any message from this user to ‘Following’ chat
# listen to user messages to catch forwards for following chat
@user.on_message(filters.me & ~filters.edited)
def myHandler(client, message):
    if str(message.chat.id) != following_chat_id:
        return
    if message.forward_from:
        if str(message.forward_from.id) in following_set:
            message.reply('Following already works for id {}'.format(
                message.forward_from.id))
        else:
            following_set.add(str(message.forward_from.id))
            save_following(following_set)
            message.reply('id {} is added to Following list'.format(
                message.forward_from.id))


def makeUserMention(user):
    name = str(user.first_name) + ' ' + str(user.last_name).strip()
    return '[{}](tg://user?id={})'.format(name, user.id)


def makeMessageDescription(message):
    # Direct Messages
    if message.chat.type == 'private':
        source = 'in Direct Messages ({})'.format(makeUserMention(message.from_user))
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
            source_chat_name, source_chat_link, makeUserMention(message.from_user))

    # forward of forward loses the first person
    if message.forward_from:
        return '{}, forwarded from - {}'.format(source, makeUserMention(message.forward_from))

    return source


def keywords_forward(client, message, keyword):
    source = makeMessageDescription(message)
    client.send_message(
        keywords_chat_id, '#{} {}'.format(keyword, source))
    message.forward(keywords_chat_id)
    client.mark_chat_unread(keywords_chat_id)


def mentions_forward(client, message):
    source = makeMessageDescription(message)
    client.send_message(
        mentions_chat_id, 'Mentioned {}'.format(source))
    message.forward(mentions_chat_id)
    client.mark_chat_unread(mentions_chat_id)


def following_forward(client, message):
    source = makeMessageDescription(message)
    client.send_message(
        following_chat_id, 'Action detected {}'.format(source))
    message.forward(following_chat_id)
    client.mark_chat_unread(following_chat_id)


def start_bot():
    # TODO catch 401 error when session is expired / removed, delete user.session file and try again
    user.start()
    user_info = user.get_me()

    for k in chat_dict:
        if not globals()[chat_dict[k]]:
            new_chat = user.create_group(k, dummy_bot_name)
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

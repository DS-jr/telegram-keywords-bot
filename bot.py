import re
from pyrogram import Client, filters, idle
from datetime import datetime
from config import config, keywords_chat_id, following_chat_id, mentions_chat_id, keywords, save_keywords, \
    excluded_chats, save_excluded_chats, add_keywords_to_includes, includes_dict, following_set, save_following, \
    dummy_bot_name, config_set_and_save

# start app
user = Client('user')

async def forward_all_messages_from_chat(client, from_chat_id, to_chat_id):
    async with client:
        async for message in client.iter_history(from_chat_id):  # iter_history is used in Pyrogram v.1.4. instead of get_chat_history in v2.0.
            if message.service:
                continue
            message_datetime = datetime.fromtimestamp(message.date)
            await client.send_message(chat_id=to_chat_id, text=message_datetime.strftime("%A, %d. %B %Y %I:%M%p")) # To show the exact time
            await message.forward(to_chat_id)

# Substitute_chat_id & to_chat_id manually with chat IDs here (use bot's /findid command to get chat IDs)
# user.run(forward_all_messages_from_chat(user, from_chat_id = 0, to_chat_id = 0))

            # print(message.date, message_datetime)

# @user.on_message()
# async def my_handler(client, message):
#     await message.forward("me")  # (in real time!) Forwards ALL incomming messages to myself (to 'Saved messages' chat):
#
# user.run()

# def main():
    # "me" refers to your own chat (Saved Messages)
    # for message in app.get_chat_history("me"):
    #     print(message)

# for message in user.get_chat_history():
            #print(message.text)

# for message in user.get_history():
            #print(message.text)


# TODO catch 401 error when session is expired / removed, delete user.session file and try again
user.start()
user_info = user.get_me()

# init chats
chat_dict = {
    "Keywords": "keywords_chat_id",
    "Mentions": "mentions_chat_id",
    "Following": "following_chat_id"
}
for k in chat_dict:
    if not globals()[chat_dict[k]]:
        new_chat = user.create_group(k, dummy_bot_name)
        globals()[chat_dict[k]] = new_chat.id
        config_set_and_save('bot_params', chat_dict[k], str(new_chat.id))

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


############## bot commands handlers #################

# command messages listener
@user.on_message(filters.me & ~filters.edited & filters.command(['help', 'add', 'show', 'remove', 'findid', 'exclude_chat', 'excluded_chats_list', 'delete_from_excluded_chats', 'include', 'follow', 'unfollow']))
def commHandler(client, message):
    # accept commands only for bot chat ids
    if not message.chat or not str(message.chat.id) in (keywords_chat_id, following_chat_id, mentions_chat_id):
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
                '/add keyword1 keyword2\n/show\n/remove keyword1 keyword2\n/removeall\n/findid chat_title|name|id|@username\n/exclude_chat chat_title|id|@username\n/excluded_chats_list\n/delete_from_excluded_chats chat_id\n/include name|id|@username keywords')
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
                # Draft v15:
                chatid_chatname_string = ""
                for chat_id in excluded_chats:
                    for dialog in dialogs:
                        if dialog[0] == chat_id:
                            chatid_chatname_string += 'Chat ID: ' + str(chat_id) + ' \tChat name: ' + str(dialog[1]) + '\n'
                message.reply_text('Excluded chats:\n' + chatid_chatname_string)
                
                # chatid_chatname = {} # (?) Simplify the code block below, as now - too many 'for' loops
                # for chat_id in excluded_chats:
                #     for dialog in dialogs:
                #         if dialog[0] == chat_id:
                #             chatid_chatname[chat_id] = dialog[1]
                # message.reply_text('(v14) Excluded chats:\n' + '\n'.join([f'Chat ID: {k} \tChat name: {v}' for k,v in chatid_chatname.items()]))






                # message.reply_text('(v12) Excluded chats:\n' + '\n'.join(chatid_chatname.items()))
                # message.reply_text('(v11) Excluded chats:\n' + '\n'.join(excluded_chats))
                # message.reply_text('(v10) Excluded chats:\n')

        # print(chat_id, dialog[1])
        #             message.reply_text('Chat ID: ' + chat_id + ' Chat name: ' + dialog[1])

                            # message.reply_text('(v10) Excluded chats:\n' + chat_id + dialog[1] + '\n')
                            # print(chat_id, dialog[1])

                # message.reply_text('(v0)Excluded chats:\n' + '\n'.join(excluded_chats))

                # message.reply_text('(v1)Excluded chats:\n' + '\n'.join([' - '.join(dialog) for dialog in dialogs]))
                # message.reply_text('(v2)Excluded chats:\n' + '\n'.join([' - '.join(dialog) for dialog in dialogs[0]]))
                # message.reply_text('(v3)Excluded chats:\n' + ' - '.join(dialogs[1]))
                # message.reply_text('(v4)Excluded chats:\n' + ' - '.join(dialogs[1][0]))
                # message.reply_text('(v5)Excluded chats:\n' + dialogs[1][1])
                # message.reply_text('(v6)Excluded chats:\n' + '\n'.join([' - '.join(e_1) for e_1 in excluded_chats]))
                # message.reply_text('(v7)Excluded chats:\n' + '\n'.join([e_1 for e_1 in excluded_chats]))
                # print(excluded_chats)
                # print(dialogs)
                # message.reply_text('(v8)Excluded chats:\n' + '\n'.join([e_1 for excluded_chats in dialogs]))
                # message.reply_text('(v9)Excluded chats:\n' + '\n'.join(excluded_chats, dialogs[excluded_chats][1]))  #TypeError: list indices must be integers or slices, not set


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

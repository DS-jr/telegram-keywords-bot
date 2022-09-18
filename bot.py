import re

from pyrogram import Client, filters, idle
from config import bot_config


class KeywordsBot:
    def __init__(self, config=bot_config):
        self.user = Client("user")
        self.user.start()
        self.user_info = self.user.get_me()
        self.config = config
        # init chats
        self.chat_dict = {
            "Keywords": "keywords_chat_id",
            "Mentions": "mentions_chat_id",
            "Following": "following_chat_id",
        }

        for k in self.chat_dict:
            if not self.config.__getattr__(k):
                new_chat = self.user.create_group(k, self.config.dummy_bot_name)
                self.config.__setattr__(k, new_chat.id)
                self.config.config_set_and_save("bot_params", self.chat_dict[k], str(new_chat.id))

    @staticmethod
    def is_id(val):
        try:
            int(val)
            return True
        except ValueError:
            return False

    def find_chats(self, client, args):
        dialogs = []
        if len(args) == 1 and (self.is_id(args[0]) or args[0][0] == "@"):
            try:
                chat = client.get_chat(args[0])
                dialogs.append(
                    [
                        str(chat.id),
                        str(chat.title)
                        if chat.title
                        else str(chat.first_name) + " " + str(chat.last_name),
                    ]
                )
            except:
                return dialogs
        else:
            for dialog in client.iter_dialogs():
                searchStr = " ".join(
                    (
                        str(dialog.chat.title),
                        str(dialog.chat.first_name),
                        str(dialog.chat.last_name),
                        "@" + str(dialog.chat.username),
                    )
                )
                if re.search(" ".join(args), searchStr, re.IGNORECASE):
                    dialogs.append(
                        [
                            str(dialog.chat.id),
                            str(dialog.chat.title)
                            if dialog.chat.title
                            else str(dialog.chat.first_name)
                            + " "
                            + str(dialog.chat.last_name),
                        ]
                    )
        return dialogs

    def find_users(self, client, args):
        result = []
        users = client.get_users(args)
        for user in users:
            result.append(
                [
                    str(user.id),
                    " ".join(list(filter(None, [user.first_name, user.last_name]))),
                ]
            )
        return result

    ############## bot commands handlers #################


    # keywords chat handler

    def kwHandler(self, client, message):
        args = message.command
        comm = args.pop(0)

        match comm:
            case "help":
                message.reply_text(
                    "/add keyword1 keyword2\n/show\n/remove keyword1 keyword2\n/removeall\n/findchat name|id|@username\n/exclude name|id|@username\n/include name|id|@username keywords"
                )
            case "add":
                keywords = keywords_bot.config.keywords
                for keyword in args:
                    keywords.add(keyword.strip().replace(",", ""))
                message.reply_text("processed " + str(len(args)) + " keywords")
                keywords_bot.config.save_keywords(keywords)
            case "show":
                if not keywords_bot.config.keywords:
                    message.reply_text("no keywords, add with /add command")
                else:
                    message.reply_text("keywords: #" + ", #".join(keywords_bot.config.keywords))
            case "remove":
                keywords = keywords_bot.config.keywords
                for keyword in args:
                    keywords.discard(keyword.strip().replace(",", ""))
                message.reply_text("processed " + str(len(args)) + " keywords")
                self.config.save_keywords(keywords)
            case "removeall":
                message.reply_text("removed " + str(len(keywords_bot.config.keywords)) + " keywords")
                self.config.save_keywords(set())
            case "findchat":
                if not args:
                    return
                dialogs = self.find_chats(client, args)
                message.reply_text(
                    "\n".join([" - ".join(dialog) for dialog in dialogs])
                    if len(dialogs)
                    else "Ничего не найдено"
                )
            case "exclude":
                if not args:
                    return
                dialogs = self.find_chats(client, args)
                if len(dialogs) != 1:
                    message.reply_text(
                        "Найдено больше одного чата:\n"
                        + "\n".join([" - ".join(dialog) for dialog in dialogs])
                        if len(dialogs)
                        else "Ничего не найдено"
                    )
                else:
                    excluded_chats = keywords_bot.config.keywords
                    excluded_chats.add(dialogs[0][0])
                    self.config.save_excluded_chats(excluded_chats)
                    message.reply_text(
                        "Чат добавлен в список исключений:\n" + " - ".join(dialogs[0])
                    )
            case "include":
                if len(args) < 2:
                    return
                chat_name = args.pop(0)
                dialogs = self.find_chats(client, [chat_name])
                if len(dialogs) != 1:
                    message.reply_text(
                        "Найдено больше одного чата:\n"
                        + "\n".join([" - ".join(dialog) for dialog in dialogs])
                        if len(dialogs)
                        else "Ничего не найдено"
                    )
                else:
                    self.config.add_keywords_to_includes(dialogs[0][0], args)
                    message.reply_text(
                        "Ключевые слова #{} для чата:\n".format(
                            ", #".join(self.config.includes_dict[dialogs[0][0]])
                        )
                        + " - ".join(dialogs[0])
                    )
            case _:
                message.reply_text("Неизвестная команда")

    # forwards chat handler

    def fwHandler(self, client, message):
        if str(message.chat.id) != self.config.following_chat_id:
            return
        # print(message)
        args = message.command
        comm = args.pop(0)
        match comm:
            case "show":
                message.reply(
                    "\n".join(
                        [" - ".join(user) for user in self.find_users(client, self.config.following_set)]
                    )
                    if self.config.following_set
                    else "Список пуст"
                )
            case "unfollow":
                if not args or not args[0] in self.config.following_set:
                    message.reply("Не найден")
                else:
                    following_set = self.config.following_set
                    following_set.discard(args[0])
                    self.config.save_following(following_set)
                    message.reply("{} удален из подписок".format(args[0]))
            case _:
                message.reply("Неизвестная команда")

    # process incoming messages
    # limit to <not me> : ~filters.me (by config?)
    # exclude forwards ?
    # limit to some types of updates (plain text?)
    # limit to private chats / groups / channels (by config?)

    # b1: search for keywords
    # b2: limit to mentions

    # listen to only other users' messages;
    # skip message edits for now (TODO: handle edited messages)
    @user.on_message(~filters.me & ~filters.edited)   #  NameError: name 'user' is not defined
    def notmyHandler(client, message):
        # print(message)
        # process keywords
        if message.text and not str(message.chat.id) in excluded_chats:
            # maybe search -> findall and mark all keywords?
            keyword = re.search("|".join(keywords), message.text, re.IGNORECASE)
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
                message.reply("Уже следим за id {}".format(message.forward_from.id))
            else:
                following_set.add(str(message.forward_from.id))
                save_following(following_set)
                message.reply(
                    "id {} добавлен в список отслеживания".format(
                        message.forward_from.id
                    )
                )

    def makeUserMention(user):
        name = str(user.first_name) + " " + str(user.last_name).strip()
        return "[{}](tg://user?id={})".format(name, user.id)

    def makeMessageDescription(message):
        # личные
        if message.chat.type == "private":
            source = "в лс ({})".format(makeUserMention(message.from_user))
        # каналы
        elif message.chat.type == "channel":
            source = "в канале {} @{}".format(message.chat.title, message.chat.username)
        # группы и супергруппы
        else:
            source_chat_name = (
                str(message.chat.title) if message.chat.title else "<без имени>"
            )
            source_chat_link = (
                " @" + str(message.chat.username) if message.chat.username else ""
            )
            source = "в чате {}{} от {}".format(
                source_chat_name, source_chat_link, makeUserMention(message.from_user)
            )

        # forward of forward loses the first person
        if message.forward_from:
            return "{}, форвард от - {}".format(
                source, makeUserMention(message.forward_from)
            )

        return source

    def keywords_forward(client, message, keyword):
        source = makeMessageDescription(message)
        client.send_message(keywords_chat_id, "#{} {}".format(keyword, source))
        message.forward(keywords_chat_id)
        client.mark_chat_unread(keywords_chat_id)

    def mentions_forward(client, message):
        source = makeMessageDescription(message)
        client.send_message(mentions_chat_id, "Уведомление {}".format(source))
        message.forward(mentions_chat_id)
        client.mark_chat_unread(keywords_chat_id)

    def following_forward(client, message):
        source = makeMessageDescription(message)
        client.send_message(following_chat_id, "Активность {}".format(source))
        message.forward(following_chat_id)
        client.mark_chat_unread(keywords_chat_id)


keywords_bot = KeywordsBot()

# command messages listener
@keywords_bot.user.on_message(
    filters.me
    & ~filters.edited
    & filters.command(
        [
            "help",
            "add",
            "show",
            "remove",
            "findchat",
            "exclude",
            "include",
            "follow",
            "unfollow",
        ]
    )
)
def commHandler(client, message):
    # accept commands only for bot chat ids
    if not message.chat or not str(message.chat.id) in (
        keywords_bot.config.keywords_chat_id,
        keywords_bot.config.following_chat_id,
        keywords_bot.config.mentions_chat_id,
    ):
        return

    chat_id = str(message.chat.id)

    if chat_id == keywords_bot.config.keywords_chat_id:
        keywords_bot.kwHandler(client, message)
    elif chat_id == keywords_bot.config.following_chat_id:
        keywords_bot.fwHandler(client, message)
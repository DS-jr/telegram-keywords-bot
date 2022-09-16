# read config
from configparser import ConfigParser

CONFIG_FILENAME = "config.ini"
config = ConfigParser()
config.read(CONFIG_FILENAME)

if not config.has_section("bot_params"):
    config.add_section("bot_params")

if not config.has_section("includes_dict"):
    config.add_section("includes_dict")


class BotConfig:
    def __init__(self, config):
        self.config = config

        for chat in self.includes_dict:
            self.includes_dict[chat] = set(
                filter(None, self.includes_dict[chat].split(","))
            )

    @property
    def keywords(self):
        return set(
            filter(
                None, self.config.get("bot_params", "keywords", fallback="").split(",")
            )
        )

    @property
    def excluded_chats(self):
        return set(
            filter(
                None,
                self.config.get("bot_params", "excluded_chats", fallback="").split(","),
            )
        )

    @property
    def following_set(self):
        return set(
            filter(
                None, self.config.get("bot_params", "following", fallback="").split(",")
            )
        )

    @property
    def includes_dict(self):
        return dict(self.config.items("includes_dict"))

    @property
    def dummy_bot_name(self):
        return self.config.get(
            "bot_params", "dummy_bot_name", fallback="MyLittleDummyBot"
        )

    @property
    def keywords_chat_id(self):
        return self.config.get("bot_params", "keywords_chat_id", fallback="")

    @property
    def mentions_chat_id(self):
        return self.config.get("bot_params", "mentions_chat_id", fallback="")

    @property
    def following_chat_id(self):
        return self.config.get("bot_params", "following_chat_id", fallback="")

    def config_set_and_save(self, section, param_name, param_value, skip_set=False):
        if not skip_set:
            self.config.set(section, param_name, param_value)
        with open(CONFIG_FILENAME, "w") as configfile:
            self.config.write(configfile)

    def save_keywords(self, keywords):
        keywords = set(filter(None, keywords))
        self.config_set_and_save("bot_params", "keywords", str(",".join(keywords)))

    def save_excluded_chats(self, excluded_chats):
        excluded_chats = set(filter(None, excluded_chats))
        self.config_set_and_save(
            "bot_params", "excluded_chats", str(",".join(excluded_chats))
        )

    def save_following(self, following):
        following = set(filter(None, following))
        self.config_set_and_save("bot_params", "following", str(",".join(following)))

    def add_keywords_to_includes(self, chat, keywords):
        if chat not in self.includes_dict:
            self.includes_dict[chat] = set()
        for keyword in keywords:
            self.includes_dict[chat].add(keyword)

    def remove_keywords_from_includes(self, chat, keywords):
        if chat not in self.includes_dict:
            return
        for keyword in keywords:
            self.includes_dict[chat].discard(keyword)

        if keywords == ["all"] or len(self.includes_dict[chat]) == 0:
            del self.includes_dict[chat]

    def save_includes(self, includes):
        includes = set(filter(None, includes))
        for include in includes:
            config.set(
                "chat_specific_keywords",
                include["id"],
                str(",".join(include["keywords"])),
            )
        self.config_set_and_save(skip_set=True)

bot_config = BotConfig(config)

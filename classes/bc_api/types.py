"""Thanks to https://github.com/boticord/boticordpy"""

from datetime import datetime, timezone
from enum import IntEnum, Enum, EnumMeta
import copy
from dataclasses import _is_dataclass_instance, fields, dataclass
from typing import (
    Dict,
    Union,
    Generic,
    Tuple,
    TypeVar,
    get_origin,
    get_args,
    Optional,
    List,
)
from sys import modules
from itertools import chain

from typing_extensions import get_type_hints


KT = TypeVar("KT")
VT = TypeVar("VT")
T = TypeVar("T")


class Singleton(type):
    # Thanks to this stackoverflow answer (method 3):
    # https://stackoverflow.com/q/6760685/12668716
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TypeCache(metaclass=Singleton):
    # Thanks to Pincer Devs. This class is from the Pincer Library.
    cache = {}

    def __init__(self):
        lcp = modules.copy()
        for module in lcp:
            if not module.startswith("melisa"):
                continue

            TypeCache.cache.update(lcp[module].__dict__)


def _asdict_ignore_none(obj: Generic[T]) -> Union[Tuple, Dict, T]:
    """
    Returns a dict from a dataclass that ignores
    all values that are None
    Modification of _asdict_inner from dataclasses
    Parameters
    ----------
    obj: Generic[T]
        The object to convert
    Returns
    -------
        A dict without None values
    """

    print(obj)

    if _is_dataclass_instance(obj):
        result = []
        for f in fields(obj):
            value = _asdict_ignore_none(getattr(obj, f.name))

            if isinstance(value, Enum):
                result.append((f.name, value.value))
            elif not f.name.startswith("_"):
                result.append((f.name, value))

        return dict(result)

    elif isinstance(obj, tuple) and hasattr(obj, "_fields"):
        return type(obj)(*[_asdict_ignore_none(v) for v in obj])

    elif isinstance(obj, (list, tuple)):
        return type(obj)(_asdict_ignore_none(v) for v in obj)

    elif isinstance(obj, datetime):
        return str(round(obj.timestamp() * 1000))

    elif isinstance(obj, dict):
        return type(obj)(
            (_asdict_ignore_none(k), _asdict_ignore_none(v)) for k, v in obj.items()
        )
    else:
        return copy.deepcopy(obj)


class APIObjectBase:
    """
    Represents an object which has been fetched from the BotiCord API.
    """

    def __attr_convert(self, attr_value: Dict, attr_type: T) -> T:
        factory = attr_type

        # Always use `__factory__` over __init__
        if getattr(attr_type, "__factory__", None):
            factory = attr_type.__factory__

        if attr_value is None:
            return None

        if attr_type is not None and isinstance(attr_value, attr_type):
            return attr_value

        if isinstance(attr_value, dict):
            return factory(attr_value)

        return factory(attr_value)

    def __post_init__(self):
        TypeCache()

        attributes = chain.from_iterable(
            get_type_hints(cls, globalns=TypeCache.cache).items()
            for cls in chain(self.__class__.__bases__, (self,))
        )

        for attr, attr_type in attributes:
            # Ignore private attributes.
            if attr.startswith("_"):
                continue

            types = self.__get_types(attr, attr_type)

            types = tuple(filter(lambda tpe: tpe is not None, types))

            if not types:
                raise ValueError(
                    f"Attribute `{attr}` in `{type(self).__name__}` only "
                    "consisted of missing/optional type!"
                )

            specific_tp = types[0]

            attr_gotten = getattr(self, attr)

            if tp := get_origin(specific_tp):
                specific_tp = tp

            if isinstance(specific_tp, EnumMeta) and not attr_gotten:
                attr_value = None
            elif tp == list and attr_gotten and (classes := get_args(types[0])):
                attr_value = [
                    self.__attr_convert(attr_item, classes[0])
                    for attr_item in attr_gotten
                ]
            elif tp == dict and attr_gotten and (classes := get_args(types[0])):
                attr_value = {
                    key: self.__attr_convert(value, classes[1])
                    for key, value in attr_gotten.items()
                }
            else:
                attr_value = self.__attr_convert(attr_gotten, specific_tp)

            setattr(self, attr, attr_value)

    def __get_types(self, attr: str, arg_type: type) -> Tuple[type]:
        origin = get_origin(arg_type)

        if origin is Union:
            # Ahh yes, typing module has no type annotations for this...
            # noinspection PyTypeChecker
            args: Tuple[type] = get_args(arg_type)

            if 2 <= len(args) < 4:
                return args

            raise ValueError(
                f"Attribute `{attr}` in `{type(self).__name__}` has too many "
                f"or not enough arguments! (got {len(args)} expected 2-3)"
            )

        return (arg_type,)

    @classmethod
    def __factory__(cls: Generic[T], *args, **kwargs) -> T:
        return cls.from_dict(*args, **kwargs)

    def __repr__(self):
        attrs = ", ".join(
            f"{k}={v!r}"
            for k, v in self.__dict__.items()
            if v and not k.startswith("_")
        )

        return f"{type(self).__name__}({attrs})"

    def __str__(self):
        if _name := getattr(self, "__name__", None):
            return f"{_name} {self.__class__.__name__.lower()}"

        return super().__str__()

    def to_dict(self) -> Dict:
        """
        Transform the current object to a dictionary representation. Parameters that
        start with an underscore are not serialized.
        """
        return _asdict_ignore_none(self)


class BotLibrary(IntEnum):
    """The library that the bot is based on"""

    DISCORD4J = 1
    """Discord4j"""

    DISCORDCR = 2
    """Discordcr"""

    DISCORDGO = 3
    """DiscordGO"""

    DISCORDDOO = 4
    """Discordoo"""

    DSHARPPLUS = 5
    """DSharpPlus"""

    DISCORDJS = 6
    """Discord.js"""

    DISCORDNET = 7
    """Discord.Net"""

    DISCORDPY = 8
    """discord.py"""

    ERIS = 9
    """eris"""

    JAVACORD = 10
    """JavaCord"""

    JDA = 11
    """JDA"""

    OTHER = 12
    """Other"""

    NONE = 0
    """Bot's library doesn't specified"""


class ResourceStatus(IntEnum):
    """Status of the project on monitoring"""

    HIDDEN = 0
    """is hidden"""

    PUBLIC = 1
    """is public"""

    BANNED = 2
    """is banned"""

    PENDING = 3
    """is pending"""


class ServerTag(IntEnum):
    """Tags of the server"""

    SPEAKING = 130
    """Speaking"""

    FUN = 131
    """Fun"""

    GAMES = 132
    """Games"""

    CINEMA = 133
    """Cinema"""

    ANIME = 134
    """Anime"""

    ART = 135
    """Art"""

    CODING = 136
    """Coding"""

    MUSIC = 137
    """Music"""

    ADULT = 138
    """18+"""

    ROLEPLAY = 139
    """Role-Play"""

    HUMOUR = 140
    """Humour"""

    GENSHIN = 160
    """Genshin"""

    MINECRAFT = 161
    """Minecraft"""

    GTA = 162
    """GTA"""

    CS = 163
    """CS"""

    DOTA = 164
    """Dota"""

    AMONG_US = 165
    """Among Us"""

    FORTNITE = 166
    """Fortnite"""

    BRAWL_STARS = 167
    """Brawl Stars"""


class BotTag(IntEnum):
    """Tags of the bot"""

    MODERATION = 0
    """Moderation"""

    BOT = 1
    """Bot"""

    UTILITIES = 2
    """Utilities"""

    ENTERTAINMENT = 3
    """Entertainment"""

    MUSIC = 4
    """Music"""

    ECONOMY = 5
    """Economy"""

    LOGS = 6
    """Logs"""

    LEVELS = 7
    """Levels"""

    NSFW = 8
    """NSFW (18+)"""

    SETTINGS = 9
    """Settings"""

    ROLE_PLAY = 10
    """Role-Play"""

    MEMES = 11
    """Memes"""

    GAMES = 12
    """Games"""

    AI = 13
    """AI"""


@dataclass(repr=False)
class UserLinks(APIObjectBase):
    """Links of the userk"""

    vk: Optional[str]
    """vk.com"""

    telegram: Optional[str]
    """t.me"""

    donate: Optional[str]
    """Donate"""

    git: Optional[str]
    """Link to git of the user"""

    custom: Optional[str]
    """Custom link"""

    @classmethod
    def from_dict(cls, data: dict):
        """Generate a UserLinks from the given data.

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into a UserLinks.
        """

        self: UserLinks = super().__new__(cls)
        data = data or {}

        self.vk = data.get("vk")
        self.telegram = data.get("telegram")
        self.donate = data.get("donate")
        self.git = data.get("git")
        self.custom = data.get("custom")

        return self


@dataclass(repr=False)
class UserBadge(APIObjectBase):
    """Information about user's profile badge"""

    id: int
    """Badge's ID"""

    name: str
    """Badge's name"""

    asset_url: str
    """Badge's icon URL"""

    @classmethod
    def from_dict(cls, data: dict):
        """Generate a UserBadge from the given data.

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into a UserBadge.
        """
        self: UserBadge = super().__new__(cls)

        self.id = data["id"]
        self.name = data["name"]
        self.asset_url = data["assetURL"]

        return self


@dataclass(repr=False)
class ResourceUp(APIObjectBase):
    """Information about bump (bot/server)"""

    id: str
    """Bump's id"""

    expires: datetime
    """Expiration date. (ATTENTION! When using `to_dict()`, the data may not correspond to the actual data due to the peculiarities of the `datetime` module)"""

    @classmethod
    def from_dict(cls, data: dict):
        """Generate a ResourceUp from the given data.

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into a ResourceUp.
        """

        self: ResourceUp = super().__new__(cls)

        self.id = data["id"]
        self.expires = datetime.fromtimestamp(
            int(int(data["expires"]) / 1000), tz=timezone.utc
        )

        return self


@dataclass(repr=False)
class ResourceRating(APIObjectBase):
    """Rating of bot/server"""

    count: int
    """Number of ratings"""

    rating: int
    """Rating (from 1 to 5)"""

    @classmethod
    def from_dict(cls, data: dict):
        """Generate a ResourceRating from the given data.

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into a ResourceRating.
        """

        self: ResourceRating = super().__new__(cls)

        self.count = data["count"]
        self.rating = data["rating"]

        return self


@dataclass(repr=False)
class PartialUser(APIObjectBase):
    """Partial user from BotiCord."""

    username: str
    """Username"""

    discriminator: str
    """Discriminator"""

    avatar: Optional[str]
    """Avatar of the user"""

    id: str
    """Id of the user"""

    socials: UserLinks
    """Links of the user"""

    description: Optional[str]
    """Description of the user"""

    short_description: Optional[str]
    """Short description of the user"""

    status: Optional[str]
    """Status of the user"""

    short_domain: Optional[str]
    """Short domain"""

    @classmethod
    def from_dict(cls, data: dict):
        """Generate a PartialUser from the given data.

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into a PartialUser.
        """

        self: cls = super().__new__(cls)

        self.username = data["username"]
        self.discriminator = data.get("discriminator")
        self.avatar = data.get("avatar")
        self.id = data["id"]
        self.socials = UserLinks.from_dict(data.get("socials", {}))
        self.description = data.get("description")
        self.short_description = data.get("shortDescription")
        self.status = data.get("status")
        self.short_domain = data.get("shortDomain")

        return self


@dataclass(repr=False)
class ResourceServer(APIObjectBase):
    """Information about server from BotiCord.

    .. warning::

        The result of the reverse conversion (`.to_dict()`) may not match the actual data.
    """

    id: str
    """Server's ID"""

    name: str
    """Server's name"""

    short_description: str
    """Server's short description"""

    description: str
    """Server's description"""

    avatar: Optional[str]
    """Server's avatar"""

    short_link: Optional[str]
    """Server's short link"""

    invite_link: str
    """Server's invite link"""

    premium_active: bool
    """Server's premium state"""

    premium_auto_fetch: Optional[bool]
    """Server's premium auto fetch state"""

    premium_banner_url: Optional[str]
    """Server's premium banner URL"""

    premium_splash_url: Optional[str]
    """Server's premium splash URL"""

    standart_banner_id: int
    """Server's standart banner ID"""

    owner: str
    """Server's owner ID"""

    status: ResourceStatus
    """Server's status"""

    ratings: List[ResourceRating]
    """Server's ratings"""

    created_date: datetime
    """Server's creation time"""

    members: Optional[int]
    """Server's members count"""

    website: Optional[str]
    """Server's website"""

    tags: List[ServerTag]
    """Server's tags"""

    moderators: List[PartialUser]
    """Server's moderators"""

    up_count: int
    """Server's up count"""

    ups: Optional[ResourceUp]
    """Server's ups"""

    @classmethod
    def from_dict(cls, data: dict):
        """Generate a ResourceServer from the given data.

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into a ResourceServer."""

        self = super().__new__(cls)

        self.id = data.get("id")
        self.name = data.get("name")
        self.short_description = data.get("shortDescription")
        self.description = data.get("description")
        self.avatar = data.get("avatar")
        self.short_link = data.get("shortLink")
        self.invite_link = data.get("inviteLink")
        self.owner = data.get("owner")
        self.website = data.get("website")
        self.up_count = data.get("upCount")
        self.standart_banner_id = data.get("standartBannerID")

        self.premium_active = data["premium"].get("active")
        self.premium_splash_url = data["premium"].get("splashURL")
        self.premium_auto_fetch = data["premium"].get("autoFetch")
        self.premium_banner_url = data["premium"].get("bannerURL")

        self.status = ResourceStatus(data.get("status"))
        self.ratings = [
            ResourceRating.from_dict(rating) for rating in data.get("ratings", [])
        ]
        self.created_date = datetime.strptime(
            data.get("createdDate"), "%Y-%m-%dT%H:%M:%S.%f%z"
        )
        self.tags = [ServerTag(tag) for tag in data.get("tags", [])]
        self.ups = [ResourceUp.from_dict(up) for up in data.get("ups", [])]
        self.moderators = [
            PartialUser.from_dict(mod) for mod in data.get("moderators", [])
        ]

        self.members = data.get("memberCount")

        return self


@dataclass(repr=False)
class ResourceBot(APIObjectBase):
    """Bot published on BotiCord

    .. warning::

        The result of the reverse conversion (`.to_dict()`) may not match the actual data.
    """

    id: str
    """ID of the bot"""

    name: str
    """Name of the bot"""

    short_description: str
    """Short description of the bot"""

    description: str
    """Description of the bot"""

    avatar: Optional[str]
    """Avatar of the bot"""

    short_link: Optional[str]
    """Short link to the bot's page"""

    standart_banner_id: int
    """Server's standart banner ID"""

    invite_link: str
    """Invite link"""

    premium_active: bool
    """Is premium status active? (True/False)"""

    premium_splash_url: Optional[str]
    """Link to the splash"""

    premium_auto_fetch: Optional[bool]
    """Is auto-fetch enabled? (True/False)"""

    premium_banner_url: Optional[str]
    """Premium banner URL"""

    owner: str
    """Owner of the bot"""

    status: ResourceStatus
    """Status of the bot"""

    ratings: List[ResourceRating]
    """Bot's ratings"""

    prefix: str
    """Prefix of the bot"""

    discriminator: str
    """Bot's discriminator"""

    created_date: datetime
    """Date when the bot was published"""

    support_server_invite_link: Optional[str]
    """Link to the support server"""

    library: Optional[BotLibrary]
    """The library that the bot is based on"""

    guilds: Optional[int]
    """Number of guilds"""

    shards: Optional[int]
    """Number of shards"""

    members: Optional[int]
    """Number of members"""

    website: Optional[str]
    """Link to bot's website"""

    tags: List[BotTag]
    """List of bot tags"""

    up_count: int
    """Number of ups"""

    ups: List[ResourceUp]
    """List of bot's ups"""

    developers: List[PartialUser]
    """List of bot's developers"""

    @classmethod
    def from_dict(cls, data: dict):
        """Generate a ResourceBot from the given data.

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into a ResourceBot.
        """

        self: ResourceBot = super().__new__(cls)

        self.id = data.get("id")
        self.name = data.get("name")
        self.short_description = data.get("shortDescription")
        self.description = data.get("description")
        self.avatar = data.get("avatar")
        self.short_link = data.get("shortLink")
        self.invite_link = data.get("inviteLink")
        self.owner = data.get("owner")
        self.prefix = data.get("prefix")
        self.discriminator = data.get("discriminator")
        self.support_server_invite_link = data.get("support_server_invite")
        self.website = data.get("website")
        self.up_count = data.get("upCount")
        self.standart_banner_id = data.get("standartBannerID")

        self.premium_active = data["premium"].get("active")
        self.premium_splash_url = data["premium"].get("splashURL")
        self.premium_auto_fetch = data["premium"].get("autoFetch")
        self.premium_banner_url = data["premium"].get("bannerURL")

        self.status = ResourceStatus(data.get("status"))
        self.ratings = [
            ResourceRating.from_dict(rating) for rating in data.get("ratings", [])
        ]
        self.created_date = datetime.strptime(
            data["createdDate"], "%Y-%m-%dT%H:%M:%S.%f%z"
        )
        self.library = (
            BotLibrary(data["library"]) if data.get("library") is not None else None
        )
        self.tags = [BotTag(tag) for tag in data.get("tags", [])]
        self.ups = [ResourceUp.from_dict(up) for up in data.get("ups", [])]
        self.developers = [
            PartialUser.from_dict(dev) for dev in data.get("developers", [])
        ]

        self.guilds = data.get("guilds")
        self.shards = data.get("shards")
        self.members = data.get("members")

        return self


@dataclass(repr=False)
class UserProfile(PartialUser):
    """Information about user's profile from BotiCord.'"""

    badges: List[UserBadge]
    """User's badges list."""

    bots: List[ResourceBot]
    """User's bots list"""

    servers: List[ResourceServer]
    """User's servers list"""

    @classmethod
    def from_dict(cls, data: dict):
        """Generate a UserProfile from the given data.

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into a UserProfile."""

        self = super().from_dict(data)

        self.badges = [UserBadge.from_dict(badge) for badge in data.get("badges", [])]
        self.bots = [ResourceBot.from_dict(bot) for bot in data.get("bots", [])]
        self.servers = [
            ResourceServer.from_dict(server) for server in data.get("servers", [])
        ]

        return self


@dataclass(repr=False)
class MeiliIndexedBot(APIObjectBase):
    """Bot found on BotiCord

    .. warning::

        The result of the reverse conversion (`.to_dict()`) may not match the actual data.
    """

    id: str
    """ID of the bot"""

    name: str
    """Name of the bot"""

    short_description: str
    """Short description of the bot"""

    description: str
    """Description of the bot"""

    avatar: Optional[str]
    """Avatar of the bot"""

    invite: str
    """Invite link"""

    premium_active: bool
    """Is premium status active? (True/False)"""

    premium_banner: Optional[str]
    """Premium banner URL"""

    banner: int
    """Standart banner"""

    rating: int
    """Bot's rating"""

    discriminator: str
    """Bot's discriminator"""

    library: Optional[BotLibrary]
    """The library that the bot is based on"""

    guilds: Optional[int]
    """Number of guilds"""

    shards: Optional[int]
    """Number of shards"""

    members: Optional[int]
    """Number of members"""

    tags: List[BotTag]
    """List of bot tags"""

    ups: int
    """List of bot's ups"""

    @classmethod
    def from_dict(cls, data: dict):
        """Generate a MeiliIndexedBot from the given data.

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into a MeiliIndexedBot.
        """

        self: MeiliIndexedBot = super().__new__(cls)

        self.id = data.get("id")
        self.name = data.get("name")
        self.short_description = data.get("shortDescription")
        self.description = data.get("description")
        self.avatar = data.get("avatar")
        self.invite = data.get("invite")
        self.discriminator = data.get("discriminator")
        self.ups = data.get("ups")
        self.rating = data.get("rating")
        self.banner = data.get("banner")

        self.premium_active = data.get("premiumActive")
        self.premium_banner = data.get("premiumBanner")

        self.library = (
            BotLibrary(data["library"]) if data.get("library") is not None else None
        )
        self.tags = [BotTag(tag) for tag in data.get("tags", [])]

        self.guilds = data.get("guilds")
        self.shards = data.get("shards")
        self.members = data.get("members")

        return self


@dataclass(repr=False)
class MeiliIndexedServer(APIObjectBase):
    """Server found on BotiCord

    .. warning::

        The result of the reverse conversion (`.to_dict()`) may not match the actual data.
    """

    id: str
    """ID of the server"""

    name: str
    """Name of the server"""

    short_description: str
    """Short description of the server"""

    description: str
    """Description of the server"""

    avatar: Optional[str]
    """Avatar of the server"""

    invite: str
    """Invite link"""

    premium_active: bool
    """Is premium status active? (True/False)"""

    premium_banner: Optional[str]
    """Premium banner URL"""

    banner: int
    """Standart banner"""

    discord_banner: Optional[str]
    """Discord banner URL"""

    rating: int
    """Server's rating"""

    members: Optional[int]
    """Number of members"""

    tags: List[ServerTag]
    """List of server tags"""

    ups: int
    """List of server's ups"""

    @classmethod
    def from_dict(cls, data: dict):
        """Generate a MeiliIndexedServer from the given data.

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into a MeiliIndexedServer.
        """

        self: MeiliIndexedServer = super().__new__(cls)

        self.id = data.get("id")
        self.name = data.get("name")
        self.short_description = data.get("shortDescription")
        self.description = data.get("description")
        self.avatar = data.get("avatar")
        self.invite = data.get("invite")
        self.ups = data.get("ups")
        self.rating = data.get("rating")
        self.banner = data.get("banner")

        self.premium_active = data.get("premiumActive")
        self.premium_banner = data.get("premiumBanner")
        self.discord_banner = data.get("discordBanner")

        self.tags = [ServerTag(tag) for tag in data.get("tags", [])]

        self.members = data.get("members")

        return self


@dataclass(repr=False)
class MeiliIndexedComment(APIObjectBase):
    """Comment found on BotiCord"""

    id: str
    """ID of the comment"""

    author: str
    """Id of the author of the comment"""

    rating: int
    """Comment's rating"""

    content: str
    """Content of the comment"""

    resource: str
    """Id of the resource"""

    created: datetime
    """When the comment was created"""

    mod_reply: Optional[str]
    """Reply to the comment"""

    @classmethod
    def from_dict(cls, data: dict):
        """Generate a MeiliIndexedComment from the given data.

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to convert into a MeiliIndexedComment.
        """

        self: MeiliIndexedComment = super().__new__(cls)

        self.id = data.get("id")
        self.rating = data.get("rating")
        self.author = data.get("author")
        self.content = data.get("content")
        self.resource = data.get("resource")
        self.mod_reply = data.get("modReply")
        self.created = datetime.utcfromtimestamp(data.get("created") / 1000)

        return self

import logging
import typing
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Awaitable

import slixmpp
from slixmpp import JID
from slixmpp.xmlstream import StanzaBase

from .e2ee import XEP_0384
from .message import Message
from .xmpp import XMPPClient


class Client:
    """
    This is the main class `slixbot` provides.

    Typically, you will want to instantiate it:

    >>> bot = Client()

    And attach handlers to it via its decorator interface.

    >>> @bot.on_message
    ... async def on_message(msg: Message) -> None:
    ...     print("I have received a message:", msg)

    You can also control some of the bot behaviour via instance attributes, such as its nickname:

    >>> bot.nick = "R2D2"

    …or the MUCs it will automatically join on startup:

    >>> bot.mucs = ["room1@conference.example.org", "room2@conference.example.org"]

    The easiest interface to start processing events is to use `Client.run()`.

    >>> bot.run("user@example.org", "password")  # doctest: +SKIP

    """

    __omemo: XEP_0384
    _xmpp: XMPPClient

    def __init__(self, storage: Path | str | None = None) -> None:
        """
        If you want to be able to use [OMEMO encryption](https://xmpp.org/extensions/xep-0384.html),
        you need to pass the path to a local file to store keys and state.

        :param storage: Path to a JSON file with write permissions
        """
        self.nick = "slixbot"
        """
        The nickname you want the bot to have.
        """
        self.mucs = list[JID | str]()
        """
        The rooms ([MUC](https://xmpp.org/extensions/xep-0045.html)) you want the bot to join on login.
        """

        if isinstance(storage, str):
            storage = Path(storage)
        self.__storage_path = storage
        self.__handlers: defaultdict[str, list[Callable[[], Awaitable[StanzaBase]]]] = (
            defaultdict(list)
        )

    async def __decrypt(self, msg: slixmpp.Message) -> tuple[slixmpp.Message, bool]:
        if not self.__omemo:
            return msg, False

        namespace = self.__omemo.is_encrypted(msg)
        if namespace is None:
            return msg, False

        msg, device_information = await self.__omemo.decrypt_message(msg)
        return msg, True

    def __set_stream(self, jid: JID | str, password: str) -> None:
        self.mucs = [JID(m) for m in self.mucs]
        xmpp = self._xmpp = XMPPClient(
            jid, password, self.__storage_path, self.mucs, self.nick
        )
        for event, handlers in self.__handlers.items():
            for handler in handlers:
                xmpp.add_event_handler(event, handler)

        self.__omemo = xmpp["xep_0384"]

    def __is_muc_jid(self, jid: JID | str) -> bool:
        return JID(jid) in self.mucs

    def run(self, jid: JID | str, password: str) -> None:
        """
        Launches the bot and run indefinitely.

        This will log in, and process events.

        >>> bot = Client()
        >>> bot.run("test1@localhost", "password")  # doctest: +SKIP

        :param jid: JID of the account this bot will use
        :param password: Password of the JID(to) in self.mucs else "chat"account this bot will use
        """
        self.__set_stream(jid, password)
        self._xmpp.connect()
        try:
            self._xmpp.loop.run_forever()
        except KeyboardInterrupt:
            self._xmpp.disconnect()
            self._xmpp.loop.run_until_complete(self._xmpp.disconnected)
            exit(0)

    async def start(self, jid: JID | str, password: str) -> None:
        """
        Starts the bot.

        This is similar to `Client.run` but is an async function, and requires you
        to control the asyncio loop.

        >>> import asyncio
        >>> bot = Client()
        >>> async def main():
        ...     await bot.start("test1@localhost", "password")
        ...     await asyncio.sleep(1)  # will exit after 1 seconds
        >>> asyncio.run(main())

        :param jid: JID of the account this bot will use
        :param password: Password of the account this bot will use
        """
        self.__set_stream(jid, password)
        await self._xmpp.connect()

    def on_start(self, coro: Callable[[], Awaitable[None]]) -> None:
        """
        Decorator for coroutines to await after the bot logs in.

        >>> bot = Client()
        >>> @bot.on_start
        ... async def on_start() -> None:
        ...     print("I have just started, yoohoo!")

        :param coro: A coroutine that will be awaited after the bot logs in.
        """

        async def wrapped(_: typing.Any) -> None:
            await coro()

        self.__handlers["session_start"].append(wrapped)  # type:ignore[arg-type]

    async def send_message(
        self, to: JID | str, body: str, encrypted: bool = False
    ) -> None:
        """
        Sends a chat message to a JID.

        :param to: Recipient of the message
        :param body: Text content of the message
        :param encrypted: Whether to E2E encrypt this message
        """
        to = JID(to)
        muc = self.__is_muc_jid(to)

        msg = self._xmpp.make_message(
            mto=to,
            mbody=body,
            mtype="groupchat" if muc else "chat",
        )

        if not encrypted:
            msg.send()
            return

        if muc:
            dest: JID | set[JID] = await self._xmpp.get_all_affiliations(to)
        else:
            dest = JID(to.bare)

        messages, errors = await self.__omemo.encrypt_message(msg, dest)
        if errors:
            log.error("OMEMO errors: %s", errors)
        for _jid, msg in messages.items():
            msg.send()

    def on_message(self, coro: Callable[[Message], Awaitable[None]]) -> None:
        """
        Decorator for message handlers.

        This will be called when the bot receives ny chat message.

        >>> bot = Client()
        >>> @bot.on_message
        ... async def on_message(msg: Message) -> None:
        ...     if msg.is_from_group:
        ...         print(f"I have received a message from {msg.sender.nickname} in the the room {msg.sender.muc_jid}")
        ...     else:
        ...         print(f"I have just received a direct message from {msg.sender.jid}")

        :param coro: A coroutine that will be awaited when receiving a message.
            It takes a single positional argument.
        """

        async def wrapped(msg: StanzaBase) -> None:
            assert isinstance(msg, slixmpp.Message)
            if msg.get_mucnick() == self.nick:
                return
            if not msg["body"] or msg.get_type() == "groupchat":
                return
            msg, encrypted = await self.__decrypt(msg)
            await coro(Message(self, msg, encrypted))

        self.__handlers["message"].append(wrapped)  # type:ignore[arg-type]

    def on_direct_message(self, coro: Callable[[Message], Awaitable[None]]) -> None:
        """
        Decorator for direct message handlers.

        >>> bot = Client()
        >>> @bot.on_direct_message
        ... async def on_message(msg: Message) -> None:
        ...     print(f"I have just received a direct message from {msg.sender}")

        :param coro: A coroutine that will be awaited when receiving a message.
            It takes a single positional argument.
        """

        async def wrapped(msg: StanzaBase) -> None:
            assert isinstance(msg, slixmpp.Message)
            if not msg["body"] or msg.get_type() == "groupchat":
                return
            msg, encrypted = await self.__decrypt(msg)
            await coro(Message(self, msg, encrypted))

        self.__handlers["message"].append(wrapped)  # type:ignore[arg-type]

    def on_muc_message(self, coro: Callable[[Message], Awaitable[None]]) -> None:
        """
        Decorator for direct message handlers.

        >>> bot = Client()
        >>> @bot.on_muc_message
        ... async def on_message(msg: Message) -> None:
        ...     print(f"I have received a message from {msg.sender.nickname} in the the room {msg.sender.muc_jid}")

        :param coro: A coroutine that will be awaited when receiving a message.
            It takes a single positional argument.
        """

        async def wrapped(msg: slixmpp.Message) -> None:
            if not msg["body"]:
                return
            if msg.get_mucnick() == self.nick:
                return
            msg, encrypted = await self.__decrypt(msg)
            await coro(Message(self, msg, encrypted))

        self.__handlers["groupchat_message"].append(wrapped)  # type:ignore[arg-type]


log = logging.getLogger(__name__)

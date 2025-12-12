import asyncio

import pytest
from conftest import Secret

from slixbot.client import Client
from slixbot.message import Message


@pytest.mark.parametrize("encrypted", [False, True])
@pytest.mark.asyncio
async def test_private_message(
    secret1: Secret, secret2: Secret, tmp_path, prosody, encrypted: bool
):
    bot1 = Client(tmp_path / "1.json" if encrypted else None)
    bot2 = Client(tmp_path / "2.json" if encrypted else None)

    bot1_start = asyncio.Event()
    bot2_receive = asyncio.Future()
    bot1_receive = asyncio.Future()

    @bot1.on_start
    async def send_message():
        await bot1.send_message(to=secret2.jid, body="Hello 1", encrypted=encrypted)
        bot1_start.set()

    @bot2.on_direct_message
    async def on_message(message: Message):
        await message.reply("Hello 2")
        bot2_receive.set_result(message)

    @bot1.on_direct_message
    async def on_message(message: Message):
        bot1_receive.set_result(message)

    await bot1.start(secret1.jid, secret1.password)
    await bot2.start(secret2.jid, secret2.password)

    await asyncio.wait_for(
        asyncio.gather(bot1_start.wait(), bot2_receive, bot1_receive),
        timeout=20,
    )

    assert bot2_receive.result().body == "Hello 1"
    assert bot1_receive.result().body == "Hello 2"


@pytest.mark.parametrize("encrypted", [False, True])
@pytest.mark.asyncio
async def test_muc_private_message(
    secret1: Secret, secret2: Secret, tmp_path, prosody, encrypted: bool
):
    bot1 = Client(tmp_path / "1.json" if encrypted else None)
    bot2 = Client(tmp_path / "2.json" if encrypted else None)

    bot1.nick = "nick1"
    bot2.nick = "nick2"

    bot1.mucs = bot2.mucs = [f"room1@rooms.{prosody}"]

    bot1_start = asyncio.Event()
    bot2_start = asyncio.Event()
    bot2_receive = asyncio.Future()
    bot1_receive = asyncio.Future()

    muc_ready = asyncio.Event()

    @bot1.on_start
    async def on_start():
        await bot1._xmpp.plugin["xep_0045"].set_affiliation(
            f"room1@rooms.{prosody}", "member", jid=secret2.jid
        )
        form = await bot1._xmpp.plugin["xep_0045"].get_room_config(
            f"room1@rooms.{prosody}"
        )
        form.set_values(
            {
                "muc#roomconfig_publicroom": False,
                "muc#roomconfig_membersonly": True,
                "muc#roomconfig_whois": "anyone",
            }
        )
        await bot1._xmpp.plugin["xep_0045"].set_room_config(
            f"room1@rooms.{prosody}", form
        )
        muc_ready.set()
        await bot2_start.wait()
        await bot1.send_message(
            to=f"room1@rooms.{prosody}", body="Hello 1", encrypted=encrypted
        )
        if bot1_start.is_set():
            raise AssertionError
        bot1_start.set()

    @bot2.on_start
    async def on_start():
        if bot2_start.is_set():
            raise AssertionError
        bot2_start.set()

    @bot2.on_muc_message
    async def on_message(message: Message):
        bot2_receive.set_result(message)
        await message.reply("Hello 2")

    @bot1.on_muc_message
    async def on_message(message: Message):
        bot1_receive.set_result(message)

    await bot1.start(secret1.jid, secret1.password)
    await bot2.start(secret2.jid, secret2.password)

    await asyncio.wait_for(
        asyncio.gather(bot1_start.wait(), muc_ready.wait(), bot2_receive, bot1_receive),
        timeout=20,
    )

    assert bot2_receive.result().body == "Hello 1"
    assert bot1_receive.result().body == "Hello 2"

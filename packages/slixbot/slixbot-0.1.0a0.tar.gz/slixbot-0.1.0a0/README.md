# slixmpp-bot

An easy to use library to build [XMPP](https://xmpp.org/) bots in python.

## Basic Usage

```python3

from slixbot import Client, Message

bot = Client()


@bot.on_message
async def echo(msg: Message):
    await msg.reply(msg.body)


bot.mucs = ["room1@server, room2@server"]
bot.run("user@server", "password")
```

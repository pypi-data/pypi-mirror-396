import slixmpp
from slixmpp import JID


class Sender:
    jid: slixmpp.JID
    nick: str


class Account(Sender):
    def __init__(self, jid: JID) -> None:
        pass


class Participant(Sender):
    occupant_id: str | None
    real_jid: slixmpp.JID | None

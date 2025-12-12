import logging
from typing import TYPE_CHECKING

import slixmpp
from slixmpp import JID

if TYPE_CHECKING:
    from .client import Client


class _BaseSender:
    jid: JID
    is_participant: bool
    """
    Am I a participant in a group chat?
    """
    is_contact: bool
    """
    Am I a 1:1 contact?
    """


class Contact(_BaseSender):
    jid: JID
    """
    Bare JID of this contact
    """

    def __init__(self, jid: JID) -> None:
        """
        @private
        """
        self.jid = JID(jid.bare)
        self.is_participant = False
        self.is_contact = True

    @property
    def nickname(self) -> str:
        """
        Nickname of this contact.
        """
        return self.jid.resource


class Participant(_BaseSender):
    jid: JID
    """
    Full JID of this participant, in the form room@rooms.example.org/nickname
    """

    def __init__(self, jid: JID) -> None:
        """
        @private
        """
        self.jid = jid
        self.is_participant = True
        self.is_contact = False

    @property
    def muc_jid(self) -> JID:
        """
        JID of the MUC this participant is part of
        """
        return JID(self.jid.bare)

    @property
    def nickname(self) -> str:
        """
        Nickname of this participant.
        """
        return self.jid.resource


class Message:
    """
    Represents a message received by `slixbot`.
    """

    body: str
    """
    Text content of the message.
    """

    sender: Contact | Participant
    """
    JID from which this message originated from.
    """

    def __init__(self, client: "Client", msg: slixmpp.Message, encrypted: bool):
        """
        @private
        """
        self._slix_msg = msg
        self.body = msg["body"]
        if msg.get_type() == "groupchat":
            self.sender = Participant(msg.get_from())
        else:
            self.sender = Contact(msg.get_from())
        self.client = client
        self._encrypted = encrypted

    @property
    def is_encrypted(self) -> bool:
        """
        :return: Whether this message was encrypted or not
        """
        return self._encrypted

    @property
    def is_from_group(self) -> bool:
        """
        :return: Whether this message is a MUC message or a direct message
        """
        return self._slix_msg.get_type() == "groupchat"

    # @property
    # def __omemo(self) -> XEP_0384:
    #     return self.client["xep_0384"]  # type:ignore[no-any-return]

    async def reply(self, body: str) -> None:
        """
        Reply to a given message

        :param: text of the message
        """
        return await self.client.send_message(
            self._slix_msg.get_from().bare, body, self.is_encrypted
        )
        # msg = self.client.make_message(
        #     mto=self._slix_msg.get_from().bare,
        #     mbody=body,
        #     mtype="groupchat" if self.is_from_group else "chat",
        # )
        # if not self._encrypted:
        #     msg.send()
        #     return
        #
        # if self.is_from_group:
        #     dest: JID | set[JID] = await self.client.get_all_affiliations(self._slix_msg.get_from().bare)
        # else:
        #     dest = self._slix_msg.get_from()
        #
        # messages, errors = await self.__omemo.encrypt_message(msg, dest)
        # if errors:
        #     log.error("OMEMO errors: %s", errors)
        # for _jid, msg in messages.items():
        #     msg.send()


log = logging.getLogger(__name__)

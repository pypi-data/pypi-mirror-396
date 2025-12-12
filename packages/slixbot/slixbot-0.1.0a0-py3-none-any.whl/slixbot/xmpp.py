import logging
from pathlib import Path

import slixmpp
from slixmpp import JID

from .e2ee import XEP_0384


class XMPPClient(slixmpp.ClientXMPP):
    def __init__(
        self,
        jid: str | JID,
        password: str,
        storage: Path | None,
        mucs: list[JID | str],
        nick: str | None,
    ):
        super().__init__(jid, password)
        self.register_plugin("xep_0045")
        self.register_plugin("xep_0172")
        self.register_plugin("xep_0363")
        if storage is None:
            log.warning("No storage defined, slixbot cannot do E2EE")
        else:
            self.register_plugin(
                "xep_0384", {"json_file_path": storage}, module=XEP_0384.__name__
            )

        self.add_event_handler("session_start", self._start)
        self._mucs = mucs
        self._nick = nick

    async def _start(self, _: str) -> None:
        self.send_presence()
        self.get_roster()  # type:ignore[no-untyped-call]

        for muc in self._mucs:
            try:
                await self.plugin["xep_0045"].join_muc_wait(
                    JID(muc), self._nick or self.boundjid.user, maxchars=0
                )
            except Exception as e:  # too broad, but what does this raise?
                log.exception("Could not join %s: %s", muc, e)

    async def get_all_affiliations(self, muc_jid: JID | str) -> set[JID]:
        result = set()
        for affiliation in "member", "admin", "owner":
            for jid in await self.plugin["xep_0045"].get_affiliation_list(
                muc_jid, affiliation
            ):
                result.add(JID(jid))
        return result


log = logging.getLogger(__name__)

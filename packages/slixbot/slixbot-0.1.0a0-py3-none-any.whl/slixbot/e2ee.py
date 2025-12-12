import json
import logging
from pathlib import Path
from typing import FrozenSet, Optional

from omemo.storage import Just, Maybe, Nothing, Storage
from omemo.types import DeviceInformation, JSONType
from slixmpp.plugins import register_plugin  # type:ignore[attr-defined]
from slixmpp_omemo import XEP_0384


class StorageImpl(Storage):
    def __init__(self, json_file_path: Path) -> None:
        super().__init__()

        self.__json_file_path = json_file_path
        self.__data: dict[str, JSONType] = {}
        if self.__json_file_path.exists():
            with open(self.__json_file_path, encoding="utf8") as f:
                self.__data = json.load(f)

    async def _load(self, key: str) -> Maybe[JSONType]:
        if key in self.__data:
            return Just(self.__data[key])

        return Nothing()

    async def _store(self, key: str, value: JSONType) -> None:
        self.__data[key] = value
        with open(self.__json_file_path, "w", encoding="utf8") as f:
            json.dump(self.__data, f)

    async def _delete(self, key: str) -> None:
        self.__data.pop(key, None)
        with open(self.__json_file_path, "w", encoding="utf8") as f:
            json.dump(self.__data, f)


class XEP_0384Impl(XEP_0384):
    default_config = {
        "fallback_message": "This message is OMEMO encrypted.",
        "json_file_path": None,
    }
    __storage: Storage

    def plugin_init(self) -> None:
        if not self.json_file_path:
            raise RuntimeError("JSON file path not specified.")

        self.__storage = StorageImpl(Path(self.json_file_path))

        super().plugin_init()

    @property
    def storage(self) -> Storage:
        return self.__storage

    @property
    def _btbv_enabled(self) -> bool:
        return True

    async def _devices_blindly_trusted(
        self, blindly_trusted: FrozenSet[DeviceInformation], identifier: str | None
    ) -> None:
        log.info(f"[{identifier}] Devices trusted blindly: {blindly_trusted}")

    async def _prompt_manual_trust(
        self, manually_trusted: FrozenSet[DeviceInformation], identifier: Optional[str]
    ) -> None:
        pass


register_plugin(XEP_0384Impl)
log = logging.getLogger(__name__)


__all__ = ("XEP_0384",)

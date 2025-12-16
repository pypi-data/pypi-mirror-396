import json
from dataclasses import MISSING, fields, is_dataclass
from enum import Enum
from types import NoneType, UnionType
from typing import Any, Type, TypeVar, cast, get_args, get_origin

from evsrc.lib.model import Aggregate, EventRecord, Version
from evsrc.lib.ports import EventBatchParser
from dcjdict import from_jdict, to_jdict


class JsonEventBatchParser(EventBatchParser):
    def __init__(
        self,
        cls: Type[Aggregate],
    ):
        self._cls = cls

    def encode(self, records: list[EventRecord]) -> bytes:
        if not records:
            return b""

        tss = []
        event_dicts = []
        version_value = records[0].version.value - 1
        ts = records[0].version.timestamp
        for record in records:
            if record.version.value - version_value != 1:
                raise ValueError(
                    f"There is a gap between {record.version.value} and {version_value}"
                )
            tss.append(record.version.timestamp - ts)
            event_data = to_jdict(record.event)
            event_data["__event__"] = record.event.__class__.__name__
            event_dicts.append(event_data)
            ts = record.version.timestamp
            version_value += 1

        return json.dumps(
            {
                "from": [records[0].version.value, records[0].version.timestamp],
                "tss": tss,
                "events": event_dicts,
            }
        ).encode()

    def decode(self, raw: bytes) -> list[EventRecord]:
        records = []
        data = json.loads(raw)
        version_value, ts = data.pop("from")
        for inc, event_data in zip(data.pop("tss"), data.pop("events")):
            ts += inc
            event_cls = getattr(self._cls, event_data.pop("__event__"))
            event = from_jdict(event_data, event_cls)
            records.append(EventRecord(Version(version_value, ts), event))
            version_value += 1

        return records

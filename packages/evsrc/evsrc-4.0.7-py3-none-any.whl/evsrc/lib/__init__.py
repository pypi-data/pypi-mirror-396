__all__ = (
    "Aggregate",
    "AggregateParser",
    "AggregateRepository",
    "ChangeEvent",
    "Clock",
    "EventHistorian",
    "EventRecord",
    "EventBatchParser",
    "FileSystem",
    "File",
    "Version",
)

import asyncio
import datetime
import time

from .ports import Clock, FileSystem, AggregateParser, EventBatchParser, File
from .model import ChangeEvent, Aggregate, EventRecord, Version, EventHistorian


class RealClock(Clock):
    def timestamp(self) -> int:
        return int(datetime.datetime.now().timestamp() * 1000)


from .repos import AggregateRepository

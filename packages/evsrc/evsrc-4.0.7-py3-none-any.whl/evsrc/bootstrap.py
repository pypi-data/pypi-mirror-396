from typing import Type
from evsrc.infra.json import (
    JsonEventBatchParser,
)
from evsrc.lib.ports import AggregateParser, FileSystem, Aggregate
from evsrc.lib.stores import EventBatchStore, SnapshotStore
from .lib.repos import AggregateRepository


def new_json_aggregate_repo(
    cls: Type[Aggregate],
    fs: FileSystem,
    aggregate_parser: AggregateParser,
    max_length: int = 50,
    max_time: float = 28 * 24 * 3600.0,
) -> AggregateRepository:
    aggregate_name = cls.__name__
    batchs = EventBatchStore(fs, JsonEventBatchParser(cls))
    snaps = SnapshotStore(fs, aggregate_parser)
    return AggregateRepository(aggregate_name, batchs, snaps, max_length, max_time)

"""Persistence of EventBatchs and Snapshots using a FileSystem and Parsers"""
from .model import EventRecord, Aggregate

from .ports import EventBatchParser, AggregateParser, FileSystem, ConcurrenceError


class EventBatchStore:
    """Persist event records on a abstract file system"""

    def __init__(
        self,
        fs: FileSystem,
        parser: EventBatchParser,
    ):
        self._fs = fs
        self._parser = parser

    async def load_batch(
        self, aggregate_key: str, till_version: int = -1
    ) -> list[EventRecord]:
        filename = f"{aggregate_key}/events"
        if till_version != -1:
            filename = f"{filename}-{till_version}"
        try:
            async with self._fs.open(filename, "r") as f:
                raw = await f.read()
        except FileNotFoundError:
            return []

        return self._parser.decode(raw)

    async def save_batch(self, aggregate_key: str, batch: list[EventRecord]):
        if not batch:
            return

        async with self._fs.open(f"{aggregate_key}/events", "w") as f:
            try:
                raw = await f.read()
                last_batch = self._parser.decode(raw)
                if last_batch:
                    if (
                        last_batch
                        and last_batch[-1].version.value + 1 != batch[0].version.value
                    ):
                        raise ConcurrenceError(
                            f"Version should be {last_batch[-1].version.value + 1} but is {batch[0].version.value} at '{aggregate_key}'"
                        )
                    async with self._fs.open(
                        f"{aggregate_key}/events-{last_batch[-1].version.value}", "w"
                    ) as g:
                        await g.write(raw)
            except FileNotFoundError:
                ...

            await f.write(self._parser.encode(batch))

    async def append_records(self, aggregate_key: str, records: list[EventRecord]):
        if not records:
            return

        async with self._fs.open(f"{aggregate_key}/events", "w") as f:
            try:
                raw = await f.read()
                if not raw:
                    last_batch = []
                else:
                    last_batch = self._parser.decode(raw)
            except FileNotFoundError:
                last_batch = []

            if (
                last_batch
                and last_batch[-1].version.value + 1 != records[0].version.value
            ):
                raise ConcurrenceError(
                    f"Version should be {last_batch[-1].version.value + 1} but is {records[0].version.value} at '{aggregate_key}'"
                )
            records = last_batch + records

            await f.write(self._parser.encode(records))


class SnapshotStore:
    """Persistence layer for aggregate snapshots"""

    def __init__(self, fs: FileSystem, parser: AggregateParser):
        self._fs = fs
        self._parser = parser

    async def save_snapshot(self, aggregate: Aggregate, version_value: int):
        """Save a snapshot of the aggregate"""
        async with self._fs.open(f'{aggregate.key}/snap-{version_value}', 'w') as f:
            await f.write(self._parser.encode(aggregate))

    async def load_snapshot(self, aggregate_key: str, version_value: int) -> Aggregate:
        """Load an aggregate from its version"""
        try:
            async with self._fs.open(f'{aggregate_key}/snap-{version_value}', 'r') as f:
                raw = await f.read()
        except FileNotFoundError:
            raw = b''

        return self._parser.decode(raw)

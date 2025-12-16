import asyncio
from typing import Callable, Awaitable
from weakref import WeakValueDictionary

from .model import Aggregate, EventRecord, Version, ChangeEvent
from .ports import Clock
from .stores import EventBatchStore, SnapshotStore
from . import RealClock


class AggregateNotFound(Exception):
    def __init__(self, aggregate_name: str, key: str):
        self.aggregate_name = aggregate_name
        self.key = key
        super().__init__(
            f'Aggregate "{aggregate_name}" with key "{key}" not found in persistence layer'
        )


class AggregateRepository:
    """One repository by type of Aggregate"""

    def __init__(
        self,
        aggregate_name: str,
        batchs: EventBatchStore,
        snaps: SnapshotStore,
        max_length: int = 0,  # Maximum number of events to keep in last event batch
        max_time: float = 0.0,  # Maximum time to keep in last event batch
        clock: Clock | None = None,
    ):
        self._aggregate_name = aggregate_name
        self._batchs = batchs
        self._snaps = snaps
        self._max_length = max_length
        self._max_time = max_time
        self._clock = clock or RealClock()

        self._observers = []
        self._aggregates = WeakValueDictionary()
        self._batch_records = {}

    def add_observer(self, callback: Callable[[str, EventRecord], Awaitable]):
        """Notify about batchchanges to any observer
        Useful for the implementation of projections"""

        self._observers.append(callback)

    async def get(self, aggregate_key: str, at_ts: int = 0):
        if aggregate_key in self._aggregates and not at_ts:
            return self._aggregates[aggregate_key]

        aggregate, version = await self._get(aggregate_key, at_ts)
        if not at_ts:
            self._link_aggregate(aggregate, version + 1)

        return aggregate

    async def _get(self, aggregate_key: str, at_ts: int = 0) -> tuple[Aggregate, int]:
        """Recover an aggregate"""
        snap = None
        version_value = -1
        while True:
            batch = await self._batchs.load_batch(aggregate_key, version_value)
            if not batch:
                raise AggregateNotFound(self._aggregate_name, aggregate_key)

            if not at_ts:
                break

            if at_ts and batch[0].version.timestamp < at_ts:
                break

            if batch[0].version.value == 0:
                break

            version_value = batch[0].version.value - 1

        snap = await self._snaps.load_snapshot(
            aggregate_key, batch[0].version.value - 1
        )
        for record in batch:
            if at_ts and record.version.timestamp > at_ts:
                break
            version_value = record.version.value
            record.event.apply_on(snap)

        if snap is None:
            raise AggregateNotFound(self._aggregate_name, aggregate_key)

        return snap, version_value

    async def set(self, aggregate: Aggregate):
        """Persist the aggregate"""
        if not aggregate.key:
            return

        if (
            aggregate.key not in self._aggregates
            or self._aggregates[aggregate.key] != aggregate
        ):
            self._link_aggregate(aggregate, 0)

        await self._notify(aggregate.key)

        records = self._batch_records.pop(aggregate.key, [])
        if not records:
            return

        if await self._shall_i_take_create_new_batch(aggregate.key, len(records)):
            await self._batchs.save_batch(aggregate.key, records)
        else:
            await self._batchs.append_records(aggregate.key, records)

    async def _shall_i_take_create_new_batch(
        self, aggregate_key: str, records_length: int
    ):
        if not self._max_length and not self._max_time:
            return False

        batch = await self._batchs.load_batch(aggregate_key)
        if not batch:
            return False

        if self._max_length and records_length + len(batch) < self._max_length:
            return False

        if (
            self._max_time
            and (self._clock.timestamp() - batch[0].version.timestamp) / 1000
            < self._max_time
        ):
            return False

        snap, _ = await self._get(aggregate_key, batch[-1].version.timestamp)
        await self._snaps.save_snapshot(snap, batch[-1].version.value)

        return True

    def _link_aggregate(self, aggregate, from_version_number):
        next_version = [from_version_number]

        def callback(batch: ChangeEvent, _: Aggregate):
            if aggregate.key not in self._batch_records:
                self._batch_records[aggregate.key] = [
                    EventRecord(
                        Version(next_version[0], self._clock.timestamp()), batch
                    )
                ]
            else:
                self._batch_records[aggregate.key].append(
                    EventRecord(
                        Version(next_version[0], self._clock.timestamp()), batch
                    )
                )
            next_version[0] += 1

        self._clean_destroyed_aggregates()
        aggregate.add_event_observer(callback)
        self._aggregates[aggregate.key] = aggregate

    def _clean_destroyed_aggregates(self):
        for key in set(self._batch_records.keys()) - set(self._aggregates.keys()):
            self._batch_records.pop(key)

    async def _notify(self, key):
        await asyncio.gather(
            *[self._notify_to_observer(callback, key) for callback in self._observers]
        )

    async def _notify_to_observer(self, callback, key):
        for record in self._batch_records.get(key, []):
            await callback(key, record)

    # TODO: It is a dangerous UNDO, I could regret to implement
    # async def restore(self, aggregate_key: str, at_ts: int):
    #     """Restore the aggregate to a previous state, removing the old ones"""

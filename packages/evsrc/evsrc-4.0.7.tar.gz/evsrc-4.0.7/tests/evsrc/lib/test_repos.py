import pytest
from typing import Concatenate, cast
from evsrc.infra.inmem import InMemFileSystem
from evsrc.infra.pickle import PickleAggregateParser, PickleEventBatchParser
from evsrc.lib.ports import ConcurrenceError
from evsrc.lib.repos import AggregateNotFound, AggregateRepository, EventRecord
from evsrc.lib.stores import EventBatchStore, SnapshotStore
from tests.evsrc.fakes import FakeAggregate, FakeClock

TS = 1000


@pytest.fixture
def clock():
    return FakeClock(TS)


@pytest.fixture
def fs():
    return InMemFileSystem()


def given_a_repo(fs, clock, max_time=0, max_length=0):
    return AggregateRepository(
        "fake_aggregate",
        EventBatchStore(fs, PickleEventBatchParser()),
        SnapshotStore(fs, PickleAggregateParser(FakeAggregate)),
        max_length=max_length,
        max_time=max_time,
        clock=clock,
    )


class An_AggregateRepository:
    async def should_persist_aggregates(self, fs, clock):
        aggr = FakeAggregate()
        aggr.create("key")
        aggr.modify("attr")

        repo1 = given_a_repo(fs, clock)
        await repo1.set(aggr)

        repo2 = given_a_repo(fs, clock)
        loaded = cast(FakeAggregate, await repo2.get("key"))

        assert loaded.key == "key"
        assert loaded.attr == "attr"

    async def should_keep_loaded_aggregates(self, fs, clock):
        aggr = FakeAggregate()
        aggr.create("key")
        aggr.modify("attr")
        repo = given_a_repo(fs, clock)
        await repo.set(aggr)
        aggr.modify("attr1")

        loaded = cast(FakeAggregate, await repo.get("key"))

        assert loaded == aggr
        assert loaded.attr == "attr1"

    async def should_keep_version_sorting(self, fs, clock):
        aggr = FakeAggregate()
        aggr.create("key")
        aggr.modify("attr")
        repo = given_a_repo(fs, clock)
        await repo.set(aggr)

        repo2 = given_a_repo(fs, clock)
        loaded = cast(FakeAggregate, await repo2.get("key"))
        loaded.modify("attr2")
        await repo2.set(loaded)

        repo3 = given_a_repo(fs, clock)
        loaded = cast(FakeAggregate, await repo3.get("key"))
        assert loaded.attr == "attr2"

    async def should_raise_aggregate_not_found(self, fs, clock):
        repo = given_a_repo(fs, clock)
        with pytest.raises(AggregateNotFound):
            await repo.get("key")

    async def should_detect_concurrence(self, fs, clock):
        aggr = FakeAggregate()
        aggr.create("key")
        aggr.modify("attr")
        repo = given_a_repo(fs, clock)

        await repo.set(aggr)

        repo2 = given_a_repo(fs, clock)
        loaded = cast(FakeAggregate, await repo2.get("key"))
        loaded.modify("attr1")
        await repo2.set(loaded)

        aggr.modify("attr2")
        with pytest.raises(ConcurrenceError):
            await repo.set(aggr)

    async def should_take_snapshot_if_max_len(self, fs, clock):
        aggr = FakeAggregate()
        aggr.create("key")
        aggr.modify("attr")
        repo = given_a_repo(fs, clock, max_length=2)
        await repo.set(aggr)
        assert not await fs.ls("key/snap-1")

        aggr.modify("attr1")
        await repo.set(aggr)

        assert await fs.ls("key/snap-1")

        repo2 = given_a_repo(fs, clock)
        aggr = cast(FakeAggregate, await repo2.get("key"))
        assert aggr.attr == "attr1"

    async def should_take_snapshot_if_max_time(self, fs, clock):
        aggr = FakeAggregate()
        aggr.create("key")
        aggr.modify("attr")
        repo = given_a_repo(fs, clock, max_time=1)
        await repo.set(aggr)
        assert not await fs.ls("key/snap-1")

        clock.sleep(2.0)
        aggr.modify("attr1")
        await repo.set(aggr)

        assert await fs.ls("key/snap-1")
        assert len(await fs.ls()) == 3  # two event files and one snap

        repo2 = given_a_repo(fs, clock)
        aggr = cast(FakeAggregate, await repo2.get("key"))
        assert aggr.attr == "attr1"

    async def should_dont_create_twice(self, fs, clock):
        aggr = FakeAggregate()
        aggr.create("key")

        repo = given_a_repo(fs, clock, max_time=1)
        await repo.set(aggr)

        aggr = FakeAggregate()
        aggr.create("key")
        with pytest.raises(ConcurrenceError):
            await repo.set(aggr)

    async def should_load_past_aggregate_state(self, fs, clock):
        aggr = FakeAggregate()
        aggr.create("key")

        repo = given_a_repo(fs, clock)
        await repo.set(aggr)

        clock.sleep(1)
        aggr.modify("attr1")

        clock.sleep(1)
        aggr.modify("attr2")
        await repo.set(aggr)

        repo1 = given_a_repo(fs, clock)
        aggr = cast(FakeAggregate, await repo1.get("key", clock.timestamp() - 1000))

        assert aggr.attr == "attr1"

    async def should_notify_event_to_external_observers(self, fs, clock):
        records = []

        async def callback(key, record: EventRecord):
            records.append((key, record))

        repo = given_a_repo(fs, clock)
        repo.add_observer(callback)

        aggr = FakeAggregate()
        aggr.create("key")
        aggr.modify("attr")
        await repo.set(aggr)

        assert len(records) == 2

    async def _should_restore_old_version(self):
        ...

    async def should_not_store_aggregate_without_key(self, fs, clock):
        aggr = FakeAggregate()
        repo = given_a_repo(fs, clock)

        await repo.set(aggr)

        assert not aggr.key
        with pytest.raises(AggregateNotFound):
            assert await repo.get("")

import pytest
from evsrc.lib.stores import EventBatchStore, SnapshotStore, ConcurrenceError
from evsrc.lib.model import Version, EventRecord
from tests.evsrc.fakes import FakeAggregate
from evsrc.infra.inmem import InMemFileSystem
from evsrc.infra.pickle import PickleAggregateParser, PickleEventBatchParser


@pytest.fixture
def fs():
    return InMemFileSystem()


@pytest.fixture
def batchs(fs):
    return EventBatchStore(fs, PickleEventBatchParser())


BATCHS = [
    EventRecord(Version(0, 5), FakeAggregate.Created("key")),
    EventRecord(Version(1, 10), FakeAggregate.Modified("attr1")),
    EventRecord(Version(2, 20), FakeAggregate.Modified("attr2")),
    EventRecord(Version(3, 30), FakeAggregate.Modified("attr3")),
    EventRecord(Version(4, 40), FakeAggregate.Modified("attr4")),
    EventRecord(Version(5, 50), FakeAggregate.Modified("attr5")),
    EventRecord(Version(6, 60), FakeAggregate.Modified("attr6")),
]


class A_EventBatchStore:
    async def should_save_batchs(
        self,
        batchs,
    ):
        await batchs.save_batch("key", BATCHS)

        assert await batchs.load_batch("key") == BATCHS

    async def should_append_records(
        self,
        batchs,
    ):
        await batchs.save_batch("key", BATCHS[:3])
        await batchs.append_records("key", BATCHS[3:])

        assert await batchs.load_batch("key") == BATCHS

    async def should_split_batchs_when_several_saves(self, batchs):
        await batchs.save_batch("key", BATCHS[:3])
        await batchs.save_batch("key", BATCHS[3:])

        assert await batchs.load_batch("key") == BATCHS[3:]
        assert await batchs.load_batch("key", 2) == BATCHS[:3]

    async def should_avoid_save_unordered_batchs(self, batchs):
        await batchs.save_batch("key", BATCHS[:3])

        with pytest.raises(ConcurrenceError):
            await batchs.save_batch("key", BATCHS[4:])

    async def should_avoid_append_unordered_batchs(self, batchs):
        await batchs.save_batch("key", BATCHS[:3])

        with pytest.raises(ConcurrenceError):
            await batchs.append_records("key", BATCHS[4:])

    async def should_load_empty(self, batchs):
        assert not await batchs.load_batch("key")


@pytest.fixture
def snaps():
    return SnapshotStore(InMemFileSystem(), PickleAggregateParser(FakeAggregate))


class A_SnapshotStore:
    async def should_return_empty_aggregate_if_no_snap(self, snaps):
        aggr = await snaps.load_snapshot("no-exist", 1)
        assert aggr
        assert not aggr.key

    async def should_persist_snapshots(self, snaps):
        aggr = FakeAggregate()
        aggr.create("key")
        aggr.modify("attr1")

        await snaps.save_snapshot(aggr, 1)

        loaded = await snaps.load_snapshot("key", 1)
        assert loaded.attr == "attr1"

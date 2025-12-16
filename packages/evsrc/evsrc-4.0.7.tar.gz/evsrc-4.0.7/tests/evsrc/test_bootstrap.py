from evsrc.bootstrap import new_json_aggregate_repo
from evsrc.lib.ports import AggregateParser, Aggregate
from evsrc.lib.repos import AggregateRepository
from tests.evsrc.fakes import FakeAggregate
from evsrc.infra.inmem import InMemFileSystem


class FakeAggregateParser(AggregateParser):
    def decode(self, raw: bytes) -> Aggregate:
        FakeAggregate()

    def encode(self, aggregate: Aggregate) -> bytes:
        return b""


def test_construct_jsonable_aggregate_repo():
    assert new_json_aggregate_repo(
        FakeAggregate, InMemFileSystem(), FakeAggregateParser(), 1000
    )
    assert (
        type(
            new_json_aggregate_repo(
                FakeAggregate, InMemFileSystem(), FakeAggregateParser(), 60, 1000
            )
        )
        is AggregateRepository
    )

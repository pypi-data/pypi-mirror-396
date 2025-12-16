"""Implementation of parsers with pickle"""
from typing import Callable
from ..lib.ports import AggregateParser, EventBatchParser, Aggregate, EventRecord
import pickle


class PickleAggregateParser(AggregateParser):
    def __init__(self, aggregate_constructor: Callable[[], Aggregate]):
        self._constructor = aggregate_constructor

    def encode(self, aggregate: Aggregate) -> bytes:
        return pickle.dumps(aggregate)

    def decode(self, raw: bytes = b"") -> Aggregate:
        if not raw:
            return self._constructor()

        return pickle.loads(raw)


class PickleEventBatchParser(EventBatchParser):
    def encode(self, records: list[EventRecord]) -> bytes:
        return pickle.dumps(records)

    def decode(self, raw: bytes) -> list[EventRecord]:
        if not raw:
            return []
        batch = pickle.loads(raw)
        return batch

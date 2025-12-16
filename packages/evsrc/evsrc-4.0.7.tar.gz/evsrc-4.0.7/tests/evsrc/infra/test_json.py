import pytest
from evsrc.infra.json import (
    JsonEventBatchParser,
)

from evsrc.lib.model import EventRecord, Version
from tests.evsrc.fakes import FakeAggregate


class A_JsonEventBatchParser:
    def given_a_sequence_of_event_records(self, number_of_events=3):
        records = []

        def create_record(event, _):
            records.append(EventRecord(Version(len(records), 1000), event))

        aggr = FakeAggregate()
        aggr.add_event_observer(create_record)
        aggr.create("key")
        for idx in range(number_of_events - 1):
            aggr.modify(f"attr{idx}")
        return records

    def should_encode_event_records(self):
        records = self.given_a_sequence_of_event_records()
        parser = JsonEventBatchParser(FakeAggregate)
        assert parser.encode(records)
        assert type(parser.encode(records)) is bytes
        assert parser.decode(parser.encode(records)) == records

    def should_raise_error_if_event_is_lost(self):
        records = self.given_a_sequence_of_event_records(10)
        parser = JsonEventBatchParser(FakeAggregate)

        with pytest.raises(ValueError):
            parser.encode(records[:5] + records[6:])

    def should_return_empty_if_no_records(self):
        assert JsonEventBatchParser(FakeAggregate).encode([]) == b""

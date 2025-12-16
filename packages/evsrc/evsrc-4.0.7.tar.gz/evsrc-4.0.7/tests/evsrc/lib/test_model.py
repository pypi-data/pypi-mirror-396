import pytest
from tests.evsrc.fakes import FakeAggregate, Aggregate, ChangeEvent
from typing import Callable, Self, Any


@pytest.fixture
def aggregate():
    return FakeAggregate()


class EmptyAggregate(Aggregate):
    def add_event_observer(self, callback: Callable[[ChangeEvent, Self], None]):
        return super().add_event_observer(callback)

    @property
    def key(self):
        return "key"



class A_EventHistorian:
    def handle_event(self, event, aggregate):
        self.events.append(event)
        self.aggregates.append(aggregate)

    def should_has_its_change_events_observable(self, aggregate: FakeAggregate):
        self.events = []
        self.aggregates = []
        aggregate.add_event_observer(self.handle_event)

        aggregate.create("key")
        aggregate.modify("attr")

        assert self.events == [
            FakeAggregate.Created("key"),
            FakeAggregate.Modified("attr"),
        ]
        assert self.aggregates == [aggregate] * 2

    def should_keep_changes_events_to_new_observers(self, aggregate: FakeAggregate):
        aggregate.create("key")
        aggregate.modify("attr")

        self.events = []
        self.aggregates = []
        aggregate.add_event_observer(self.handle_event)

        assert self.events == [
            FakeAggregate.Created("key"),
            FakeAggregate.Modified("attr"),
        ]
        assert self.aggregates == [aggregate] * 2

    def should_avoid_duplication_of_observers(self, aggregate: FakeAggregate):
        self.events = []
        self.aggregates = []
        aggregate.add_event_observer(self.handle_event)
        aggregate.add_event_observer(self.handle_event)

        aggregate.create("key")

        assert len(self.events) == 1


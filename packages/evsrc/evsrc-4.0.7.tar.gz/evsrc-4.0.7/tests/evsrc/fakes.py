import asyncio

from typing import Callable, Any, Self
from dataclasses import dataclass
from evsrc.lib.ports import Clock
from evsrc.lib.model import Aggregate, ChangeEvent, EventHistorian


class FakeClock(Clock):
    def __init__(self, ts: int):
        self._ts = ts

    def timestamp(self) -> int:
        return self._ts

    def sleep(self, seconds: float):
        self._ts += int(seconds * 1000)

    async def asleep(self, seconds: float):
        self.sleep(seconds)
        await asyncio.sleep(0)


class FakeAggregate(Aggregate):
    @dataclass
    class Created(ChangeEvent):
        key: str

        def apply_on(self, aggregate: "FakeAggregate"):
            aggregate._key = self.key

    @dataclass
    class Modified(ChangeEvent):
        attr: str

        def apply_on(self, aggregate: "FakeAggregate"):
            aggregate.attr = self.attr

    def __init__(self):
        self._handler = EventHistorian(self)
        self._key = ""
        self.attr = ""

    @property
    def key(self) -> str:
        return self._key

    def add_event_observer(self, callback: Callable[[ChangeEvent, Self], None]):
        self._handler.add_observer(callback)

    def _trigger(self, event: ChangeEvent):
        event.apply_on(self)
        self._handler.register_event(event)

    def create(self, key: str):
        self._trigger(self.Created(key))

    def modify(self, attr: str):
        self._trigger(self.Modified(attr))

    @classmethod
    def construct_event(cls, event_class_name: str, **kwargs) -> ChangeEvent:
        cls = getattr(cls, event_class_name)
        return cls(**kwargs)

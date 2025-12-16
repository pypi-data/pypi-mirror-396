from dataclasses import dataclass
from typing import Any, Callable, Self
import abc


class ChangeEvent(abc.ABC):
    """Change of the state of an aggregate"""

    @abc.abstractmethod
    def apply_on(self, aggregate: Any):
        """Apply event on aggregate, changing its state"""


class Aggregate(abc.ABC):
    """Interface of aggregate
    IMPORTANT: The vents shall be embebed as classes inside aggregate"""

    @property
    @abc.abstractmethod
    def key(self) -> str:
        """Unique key between same type of aggregate"""
        return ""

    @abc.abstractmethod
    def add_event_observer(self, callback: Callable[[ChangeEvent, Self], None]):
        """Add a observer of event changes, it should include olders"""



class EventHistorian:
    """Helper for an Aggregate to notify events happened before subscription
    Optional use, but recommended"""

    def __init__(self, aggregate: Aggregate):
        self._history = []
        self._observers = set()
        self._aggregate = aggregate

    def add_observer(self, callback: Callable[[ChangeEvent, Any], None]):
        """Add callback to be used when a event is trigered, it avoids accidental duplication"""
        if callback in self._observers:
            return

        self._observers.add(callback)
        for event in self._history:
            callback(event, self._aggregate)

    def register_event(self, event: ChangeEvent):
        """Register event to history"""
        self._history.append(event)
        for callback in self._observers:
            callback(event, self._aggregate)


@dataclass
class Version:
    value: int
    timestamp: int  # in ms


@dataclass
class EventRecord:
    version: Version
    event: ChangeEvent

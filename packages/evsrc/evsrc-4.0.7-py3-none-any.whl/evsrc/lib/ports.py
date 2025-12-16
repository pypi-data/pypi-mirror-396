"""Ports to be implemented by the developer to assert event sourcing works"""
import abc
from .model import EventRecord, Aggregate
from typing import Self


class ConcurrenceError(Exception):
    ...


class File(abc.ABC):
    """Interface to be implemented by storage systems like a asynchronous file"""

    @abc.abstractmethod
    async def __aenter__(self) -> Self:
        """Context manager"""

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        """Context manager"""

    @abc.abstractmethod
    async def read(self, size: int = -1) -> bytes:
        """Read content of file"""

    @abc.abstractmethod
    async def write(self, b: bytes):
        """Write bytes to the file"""


class FileSystem(abc.ABC):
    @abc.abstractmethod
    def open(self, filename: str, mode: str) -> File:
        """Create a FileLike ready to be used"""

    @abc.abstractmethod
    async def rm(self, pattern: str):
        """Remove the files following a pattern"""

    @abc.abstractmethod
    async def ls(self, pattern: str = "*") -> list[str]:
        """List all filenames in current location"""


class EventBatchParser(abc.ABC):
    """Parse list of event records"""

    @abc.abstractmethod
    def encode(self, records: list[EventRecord]) -> bytes:
        """Encode a batch of event records to bytes"""

    @abc.abstractmethod
    def decode(self, raw: bytes) -> list[EventRecord]:
        """Decode a batch of event records"""


class AggregateParser(abc.ABC):
    """Parse aggregate to bytes"""

    @abc.abstractmethod
    def encode(self, aggregate: Aggregate) -> bytes:
        """Encode an aggregate to bytes, for being stored"""

    @abc.abstractmethod
    def decode(self, raw: bytes) -> Aggregate:
        """Create an aggregate by a sequence of bytes"""


class Clock(abc.ABC):
    """Interface for injecting time dependency"""

    @abc.abstractmethod
    def timestamp(self) -> int:
        """Current timestamp in miliseconds"""

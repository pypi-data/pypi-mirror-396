# Event Sourcing with Python

Libray for python developers to help use of Event Sourcing Architecture for the persistence layer


# Installation

This library is published in pypi, so you can install with `pip`:

``` bash
pip install evsrc
```

# Usage

The library has two main interfaces to implement at its application layer:
- `Aggregate`: Every change in the aggregate is done by one event (`ChangeEvent`) and can notify it to any external observer.
- `ChangeEvent`: The events shall implement a method `apply_on` where the argument is the aggregate and changes the state of it. It is recommended to be inside the class (yes, python allows that).

The persistence has been modeled as files in file systems. The events and snapshots of aggregates are stored as files. For this purpose, the developer should implement these interfaces or ports:

- `FileSystem`: The units of storage are files (or file-like). This interface not only can be implemented with a operating system filesystem, but azure storage, amazon s3, redis,...
- `AggregateParser`: Encode to bytes lists of aggregates and the inverse function(decode). It is recommended one by aggregate type.
- `EventBatchParser`: Encode to bytes lists of EventRecords and the inverse function(decode). It is recommended one by aggregate type.

There are some apapters for the ports already implemented and available to developer:

- `InMemFileSystem`: implementation in memory, useless unless you'll want quick integration tests.
- `PickleAggregateParser`, `PickleEventBatchParser`: The parsing use `pickle` library to encoding and decoding bytes. Very easy!!!
- `JsonAggregateParser`, `JsonEventBatchParser`: The parsing use `json` library to encoding and decoding bytes. Very important the concept of JDict which is a dict with string as keys and only jsonable tokens(bool, str, int, float, lists, jdict). It needs to embed 


## v4.0.7 (2025-12-12)

### Fix

- remove lib from gitignore

## v4.0.6 (2025-12-10)

### Fix

- install git in pipeline
- update pipeline for uv
- externalize encoding of dataclasses

## v4.0.5 (2025-11-20)

### Fix

- Add dependency dcjdict

## v4.0.4 (2025-11-20)

### Fix

- publish without tokens in gitlab

## v4.0.3 (2025-11-20)

### Fix

- upload to pypi

## v4.0.2 (2025-11-18)

### Fix

- remove construct_event from aggregate

## v4.0.1 (2025-11-17)

### Fix

- correct credentials to push main

### Refactor

- remove JsonAggregateParser

## v4.0.0 (2025-11-17)

### Feat

- add jsonstore functions
- rollback function is added
- add dict as value args
- add custom dict mappers
- break the interface totally
- parse dicts
- parse enums as values or names
- convert to tuples values

### Fix

- remove comments in cicd scripts
- avoid create twice an aggregate
- mapping return None
- return none in load aggregate
- dont update json versions
- notify event records to observer
- incorrect pyproject
- loaded tables dont save in onmem

### Refactor

- simplify value objects
- restore dict methods to value objects
- remove table dependency
- move all infra to a directory

### Perf

- improve onmem store

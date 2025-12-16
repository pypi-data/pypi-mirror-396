#!/usr/bin/env sh

uv run pytest \
    -W ignore::DeprecationWarning \
    --cov=evsrc \
    --cov-report=xml \
    --cov-report=term \
    --cov-report=html \
    --junitxml=test-results.xml  tests/evsrc

    # -W error::UserWarning \
    # --cov-config=.coveragerc \


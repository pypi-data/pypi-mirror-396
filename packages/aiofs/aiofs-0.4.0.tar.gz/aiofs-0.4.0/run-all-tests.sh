#!/usr/bin/env bash

uv run pytest \
    -W ignore::DeprecationWarning \
    --cov=aiofs \
    --cov-report=xml \
    --cov-report=term \
    --cov-report=html \
    tests/aiofs

    # -W error::UserWarning \
    # --cov-config=.coveragerc \

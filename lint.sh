#!/bin/bash

flake8 --max-line-length=120 --exclude=./.venv/ --show-source .

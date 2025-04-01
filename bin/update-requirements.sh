#!/bin/sh -e

pipenv requirements > requirements.txt
pipenv requirements --dev-only > requirements-dev.txt

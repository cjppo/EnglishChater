#!/usr/bin/env bash
# exit on error
set -o errexit

poetry install
poetry add gunicorn

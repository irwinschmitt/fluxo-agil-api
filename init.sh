#!/bin/bash

echo "Running migrations..."
alembic upgrade head

echo "Creating initial data..."
python -m app.initial_data

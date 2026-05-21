#!/usr/bin/env bash
# CraftFlow build script for Render

# Exit immediately if any command fails
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Collect static files into STATIC_ROOT
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Seeding database
python manage.py seed_data
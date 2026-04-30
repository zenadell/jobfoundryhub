#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements/base.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Load initial data from local dump (Only run this manually if needed)
# if [ -f datadump.json ]; then
#     echo "Loading data from datadump.json..."
#     python manage.py loaddata datadump.json
# fi

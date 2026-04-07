#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files (--clear removes stale files first)
python manage.py collectstatic --no-input --clear

# Run database migrations
python manage.py migrate

# Reset database sequences to avoid duplicate key errors (PostgreSQL)
python manage.py shell -c "
from django.core.management.color import no_style
from django.db import connection
from django.apps import apps
models = [apps.get_model(a, m) for a, m in [('orders','Order'),('orders','OrderItem'),('menu','FoodItem'),('reviews','Review')]]
with connection.cursor() as c:
    for sql in connection.ops.sequence_reset_sql(no_style(), models):
        c.execute(sql)
print('Sequences reset.')
"

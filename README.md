# openfootydata

An API for Australian Football data.

# Requirements

 * Python 3
 * PostgreSQL

# Getting Started

    pip install -r requirements.txt
    psql --command="CREATE DATABASE openfootydata"
    python manage.py migrate
    python manage.py runserver

# Run Tests

    python manage.py test

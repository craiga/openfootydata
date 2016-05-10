# Open Footy Data

[![Build Status](https://travis-ci.org/craiga/openfootydata.svg?branch=master)](https://travis-ci.org/craiga/openfootydata) [![codecov](https://codecov.io/gh/craiga/openfootydata/branch/master/graph/badge.svg)](https://codecov.io/gh/craiga/openfootydata)


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

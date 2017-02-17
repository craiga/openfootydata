# Open Footy Data

[![Build Status](https://travis-ci.org/craiga/openfootydata.svg?branch=master)](https://travis-ci.org/craiga/openfootydata) [![codecov](https://codecov.io/gh/craiga/openfootydata/branch/master/graph/badge.svg)](https://codecov.io/gh/craiga/openfootydata) [![Code Climate](https://codeclimate.com/github/craiga/openfootydata/badges/gpa.svg)] (https://codeclimate.com/github/craiga/openfootydata)


An API for Australian Football data.

# Starting Development Environment

    docker-compose up

To run migrations:

    docker-compose run --rm web python manage.py migrate

# Managing Dependencies

Dependencies are managed using pip-tools. To install a new dependency, add it to requirements.in and then run the following:

    docker-compose run --rm web pip-compile
    docker-compose build

# Quality Assurance

To run tests:

    docker-compose run --rm web nosetests

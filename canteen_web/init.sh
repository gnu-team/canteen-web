#!/bin/bash
# This script generates a secret_key and does some initial database setup.

[[ -z $VIRTUAL_ENV ]] && {
    printf 'Please activate a virtual environment and try again.\n' >&2
    exit 2
}

[[ ! -f config.ini ]] && {
    printf 'Please copy config.example.ini to config.ini and try again.\n' >&2
    exit 3
}

# See README.md for explanation of what these commands do

printf '\n[secrets]\nsecret_key = ' >>config.ini && \
python3 -c "import os, string; pop = string.ascii_letters + string.punctuation + string.digits; print(''.join(pop[int(x/256 * len(pop))] for x in os.urandom(512)))" >>config.ini && \
./manage.py migrate && \
./manage.py loaddata groups && \
./manage.py createsuperuser && \
./manage.py collectstatic && \
printf 'Done setting up project.\n'

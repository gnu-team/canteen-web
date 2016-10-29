#!/bin/bash
# This script generates a secret_key and does some initial database setup.

[[ -z $VIRTUAL_ENV ]] && {
    printf 'Please activate a virtual environment and try again.\n' >&2
    exit 2
}

# See README.md for explanation of what these commands do

python3 -c "import os, string; pop = string.ascii_letters + string.punctuation + string.digits; print(''.join(pop[int(x/256 * len(pop))] for x in os.urandom(512)), end='')" >secret_key && \
./manage.py migrate && \
./manage.py loaddata groups && \
./manage.py createsuperuser && \
./manage.py collectstatic && \
printf 'Done setting up project.\n'

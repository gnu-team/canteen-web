Canteen Web Backend
===================

Getting started
---------------

### Setting up virtualenv

The first time after cloning the repository, create the virtualenv:

    $ virtualenv -p python3 venv

Then enter the virtual environment (you'll need to do this in any fresh
shell before running the application or using pip):

    $ . venv/bin/activate

And finally, install the required packages:

    $ pip install -r requirements.txt

### Django project

In the `canteen_web` directory, do one of the following:

#### Option 1: `init.sh`

Run `init.sh`, which will do some setup for you:

    $ ./init.sh

#### Option 2: By hand

Generate a secret key:

    $ python3 -c "import os, string; pop = string.ascii_letters + string.punctuation + string.digits; print(''.join(pop[int(x/256 * len(pop))] for x in os.urandom(512)), end='')" >secret_key

Now, run the following to initialize the SQLite database:

    $ ./manage.py migrate

Load the default groups into the database:

    $ ./manage.py loaddata groups

And then create an initial administrator:

    $ ./manage.py createsuperuser

Optionally, then collect the static files for production:

    $ ./manage.py collectstatic

### Running a development server

Run

    $ ./manage.py runserver

And visit <http://localhost:8000/>.

### Deployment

Follow the steps above (including the virtualenv step) and then create a file
in `canteen_web` named `hosts` with allowed values for the `Host` header, one
per line. This will disable debug mode.

    $ printf 'canteen-water.org\nwww.canteen-water.org' >hosts

Now, start the uwsgi server:

    $ ./run.sh

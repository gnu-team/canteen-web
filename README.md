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

In the `canteen_web`, directory, run the following to initialize the
SQLite database:

    $ ./manage.py migrate

And then create an initial administrator:

    $ ./manage.py createsuperuser

Canteen Web Backend
===================

Getting started
---------------

### Installing `bower` packages

Change to the `canteen_web/canteen_browser` directory and run:

    $ bower install

### Setting up virtualenv

The first time after cloning the repository, create the virtualenv:

    $ virtualenv -p python3 venv

Then enter the virtual environment (you'll need to do this in any fresh
shell before running the application or using pip):

    $ . venv/bin/activate

And finally, install the required packages:

    $ pip install -r requirements.txt

### Installing PostgreSQL+PostGIS

`canteen-web` requires [PostgreSQL][3] and [PostGIS][4] since we use
PostGIS-specific functionality. On Debian Jessie, I did roughly the following:

 1. Installed `postgresql`, `postgis`, and `postgresql-9.4-postgis-2.1`
 2. `sudo -u postgres createuser austin`
 3. `sudo -u postgres createdb -O austin canteen`

I then wrote the following as my `[db]` section in `config.ini` (see below):

    [db]
    engine=postgresql
    name=canteen

### Django project

Before going any further, in `canteen_web`, you must copy `config.example.ini`
to `config.ini` and update the `[db]` section as needed. Next, do one of the
following:

#### Option 1: `init.sh`

Run `init.sh`, which will do some setup for you:

    $ ./init.sh

#### Option 2: By hand

Append a new secret key to `config.ini`:

    $ printf '\n[secrets]\nsecret_key = ' >>config.ini
    $ python3 -c "import os, string; pop = string.ascii_letters + string.punctuation + string.digits; print(''.join(pop[int(x/256 * len(pop))] for x in os.urandom(512)))" >>config.ini

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

Follow the steps above (including the virtualenv step) and then change
the `host` key in the `[production]` section of `config.ini` to the
allowed values for the `Host` header as described below. This will
disable debug mode.

Now, start the uwsgi server:

    $ ./run.sh

Next, you'll need to configure your HTTP server to serve the static
files directory at `/static/` and proxy `/` to the uwsgi server. I use
nginx configuration roughly along the lines of the following:

    server {
            listen 443 ssl;
            listen [::]:443 ssl;

            server_name canteen-water.org www.canteen-water.org;

            location / {
                    uwsgi_pass unix:///path/to/canteen/canteen_web/sock;
                    include uwsgi_params;

            }

            location /static/ {
                    alias /path/to/canteen/canteen_web/static/;
            }
    }

Notice that it accepts only HTTPS connections. This is intentional — the
client currently sends passwords in plaintext with every request, so
using straight HTTP should be avoided at all costs. A [Let's Encrypt][1]
certificate is free and supported by Java [starting with 8u101][2], so I
use one.

Configuration
-------------

See `canteen_web/config.example.ini`, which you should copy to
`canteen_web/config.ini` and change as needed.

[1]: https://letsencrypt.org/
[2]: http://stackoverflow.com/a/34111150/321301
[3]: https://www.postgresql.org/
[4]: http://postgis.net/

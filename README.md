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

Create an initial `config.ini`, populating it with a new secret key:

    $ printf '[secrets]\nsecret_key = ' >config.ini
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

`canteen_web/config.ini` should contain something like the following:

    [secrets]
    secret_key = xxx

    ; Below this point is optional but needed in deployment

    [production]
    hosts = canteen-water.org www.canteen-water.org

    [mail]
    host = mail.mymail.com
    port = 25
    use_ssl = false ; Implicit SSL
    use_tls = true  ; STARTTLS
    user = account@canteen-water.org
    password = hunter2


[1]: https://letsencrypt.org/
[2]: http://stackoverflow.com/a/34111150/321301

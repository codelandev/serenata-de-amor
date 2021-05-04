# Jarbas — a tool for [Serenata de Amor](http://github.com/okfn-brasil/serenata-de-amor)

[Jarbas](http://jarbas.serenata.ai/) is part of [Serenata de Amor](http://github.com/okfn-brasil/serenata-de-amor) — we fight corruption with data science.

Jarbas is in charge of making data from [CEAP](https://github.com/okfn-brasil/serenata-de-amor/blob/main/CONTRIBUTING.md#more-about-the-quota-for-exercising-parliamentary-activity-ceap) more accessible. In the near future Jarbas will show what [Rosie](https://github.com/okfn-brasil/serenata-de-amor/tree/main/rosie) thinks of each reimbursement made for our congresspeople.

## Table of Contents

1. [JSON API endpoints](#json-api-endpoints)
    1. [Reimbursement](#reimbursement)
    1. [Subquota](#subquota)
    1. [Applicant](#applicant)
    1. [Company](#company)
    1. [Tapioca Jarbas](#tapioca-jarbas)
1. [Installing](#installing)
    1. [Settings](#settings)
    1. [Using Docker](#using-docker)
    1. [Local install](#local-install)

## JSON API endpoints

### Reimbursement

Each `Reimbursement` object is a reimbursement claimed by a congressperson and identified publicly by its `document_id`.

#### Retrieving a specific reimbursement

##### `GET /api/chamber_of_deputies/reimbursement/<document_id>/`

Details from a specific reimbursement. If `receipt_url` wasn't fetched yet, the server **won't** try to fetch it automatically.

##### `GET /api/chamber_of_deputies/reimbursement/<document_id>/receipt/`

URL of the digitalized version of the receipt of this specific reimbursement.

If `receipt_url` wasn't fetched yet, the server **will** try to fetch it automatically.

If you append the parameter `force` (i.e. `GET /api/chamber_of_deputies/reimbursement/<document_id>/receipt/?force=1`) the server will re-fetch the receipt URL.

Not all receipts are available, so this URL can be `null`.

#### Listing reimbursements

##### `GET /api/chamber_of_deputies/reimbursement/`

Lists all reimbursements.

##### Filtering

All these endpoints accepts any combination of the following parameters:

* `applicant_id`
* `cnpj_cpf`
* `document_id`
* `issue_date_start` (inclusive)
* `issue_date_end` (exclusive)
* `month`
* `subquota_number`
* `suspicions` (_boolean_, `1` parses to `True`, `0` to `False`)
* `has_receipt` (_boolean_, `1` parses to `True`, `0` to `False`)
* `year`
* `state`
* `order_by`: `issue_date` (default) or `probability` (both descending)
* `in_latest_dataset` (_boolean_, `1` parses to `True`, `0` to `False`)
* `search` (Search the value in any of the fields below)
  * `congressperson_name`
  * `supplier`
  * `cnpj_cpf`
  * `party`
  * `state`
  * `receipt_text`
  * `passenger`
  * `leg_of_the_trip`
  * `subquota_description`
  * `subquota_group_description`

For example:

```
GET /api/chamber_of_deputies/reimbursement/?year=2016&cnpj_cpf=11111111111111&subquota_number=42&order_by=probability
```

This request will list:

* all 2016 reimbursements
* made in the supplier with the CNPJ 11.111.111/1111-11
* made according to the subquota with the ID 42
* sorted by the highest probability

Also you can pass more than one value per field (e.g. `document_id=111111,222222`).

##### `GET /api/chamber_of_deputies/reimbursement/<document_id>/same_day/`

Lists all reimbursements of expenses from the same day as `document_id`.

### Subquota

Subquotas are categories of expenses that can be reimbursed by congresspeople.

#### Listing subquotas

##### `GET /api/chamber_of_deputies/subquota/`

Lists all subquotas names and IDs.

##### Filtering

Accepts a case-insensitve `LIKE` filter in as the `q` URL parameter (e.g. `GET /api/chamber_of_deputies/subquota/?q=meal` list all applicant that have `meal` in their names.

### Applicant

An applicant is the person (congressperson or the leadership of a party or government) who claimed the reimbursemement.

#### List applicants

##### `GET /api/chamber_of_deputies/applicant/`

Lists all names of applicants together with their IDs.

##### Filtering

Accepts a case-insensitive `LIKE` filter as the `q` URL parameter (e.g. `GET /api/chamber_of_deputies/applicant/?q=lideranca` list all applicant that have `lideranca` in their names.

### Company

A company is a Brazilian company in which congressperson have made expenses and claimed for reimbursement.

#### Retrieving a specific company

##### `GET /api/company/<cnpj>/`

This endpoit gets the info we have for a specific company. The endpoint expects a `cnpj` (i.e. the CNPJ of a `Company` object, digits only). It returns `404` if the company is not found.

### Tapioca Jarbas

There is also a [tapioca-wrapper](https://github.com/vintasoftware/tapioca-wrapper) for the API. The [tapioca-jarbas](https://github.com/daneoshiga/tapioca-jarbas/) can be installed with `pip install tapioca-jarbas` and can be used to access the API in any Python script.

## Installing

### Settings

Copy `contrib/.env.sample` as `.env` in the project's root folder and adjust your settings. These are the main variables:

##### Django settings

* `ENVIRONMENT` (_str_) Environment in which the application is running. (e.g. production or development)
* `LOG_LEVEL` (_str_) [The granularity of error log outputs](http://docs.gunicorn.org/en/stable/settings.html#loglevel)
* `WEB_TIMEOUT` (_int_) [Workers silent for more than this many seconds are killed and restarted](http://docs.gunicorn.org/en/stable/settings.html#timeout)
* `WEB_WORKERS` (_int_) [The number of worker processes for handling requests](http://docs.gunicorn.org/en/stable/settings.html#workers)
* `GOSS_VERSION` (_str_) [Version for Goss tester in Docker](https://goss.rocks)
* `SECRET_KEY` (_str_) [Django's secret key](https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-SECRET_KEY)
* `ALLOWED_HOSTS` (_str_) [Django's allowed hosts](https://docs.djangoproject.com/en/1.10/ref/settings/#allowed-hosts)
* `USE_X_FORWARDED_HOST` (_bool_) [Whether to use the `X-Forwarded-Host` header](https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-USE_X_FORWARDED_HOST)
* `CACHE_BACKEND` (_str_) [Cache backend](https://docs.djangoproject.com/en/1.10/ref/settings/#std:setting-CACHES-BACKEND) (e.g. `django.core.cache.backends.memcached.MemcachedCache`)
* `CACHE_LOCATION` (_str_) [Cache location](https://docs.djangoproject.com/en/1.10/ref/settings/#location) (e.g. `localhost:11211`)
* `SECURE_PROXY_SSL_HEADER` _(str)_ [Django secure proxy SSL header](https://docs.djangoproject.com/en/1.10/ref/settings/#secure-proxy-ssl-header) (e.g. `HTTP_X_FORWARDED_PROTO,https` transforms in tuple `('HTTP_X_FORWARDED_PROTO', 'https')`)

##### NewRelic settings

* `NEW_RELIC_APP_NAME` (_str_) [The name of the application you wish to report data against in the New Relic UI. If not defined, this defaults to `Python Application`](https://docs.newrelic.com/docs/agents/python-agent/configuration/python-agent-configuration#app_name)  (e.g. `Jarbas`)
* `NEW_RELIC_ENVIRONMENT` (_str_) [The name of a specific deployment environment](https://docs.newrelic.com/docs/agents/python-agent/configuration/python-agent-configuration#config-file-deployment-environments) (e.g. `Production`)
* `NEW_RELIC_LICENSE_KEY` (_str_) [Specifies the license key of your New Relic account. This key associates your app's metrics with your New Relic account.](https://docs.newrelic.com/docs/agents/python-agent/configuration/python-agent-configuration#license_key)
* `NEW_RELIC_DEVELOPER_MODE` (_str_) (e.g. true or false)

##### Database

* `DATABASE_URL` (_string_) [Database URL](https://github.com/kennethreitz/dj-database-url#url-schema), must be [PostgreSQL](https://www.postgresql.org) since Jarbas uses [JSONField](https://docs.djangoproject.com/en/1.10/ref/contrib/postgres/fields/#jsonfield).

##### Message Broker

* `CELERY_BROKER_URL` (_string_) [Celery](http://docs.celeryproject.org/en/latest/django/first-steps-with-django.html) compatible message broker URL (e.g. `amqp://guest:guest@localhost//`)

##### Google settings

* `GOOGLE_ANALYTICS` (_str_) Google Analytics tracking code (e.g. `UA-123456-7`)
* `GOOGLE_STREET_VIEW_API_KEY` (_str_) Google Street View Image API key

##### Twitter settings

* `TWITTER_CONSUMER_KEY` (_str_) Twitter API key
* `TWITTER_CONSUMER_SECRET` (_str_) Twitter API secret
* `TWITTER_ACCESS_TOKEN` (_str_) Twitter access token
* `TWITTER_ACCESS_SECRET` (_str_) Twitter access token secret

To get this credentials follow [`python-twitter`
instructions](https://python-twitter.readthedocs.io/en/latest/getting_started.html#getting-your-application-tokens).

##### For the production environment

* `VIRTUAL_HOST_WEB` (_str_) host used for the HTTPS certificate (for testing production settings locally you might need to add this host name to your `/etc/hosts`)
* `LETSENCRYPT_EMAIL` (_str_) Email used to create the HTTPS certificate at Let's Encrypt
* `HTTPS_METHOD` (_str_) if set to `noredirect` does **not** redirect from HTTP to HTTPS (default: `redirect`)

##### Searchvector schedule

* `SCHEDULE_SEARCHVECTOR` (_bool_) Enable searchvector scheduling
* `SCHEDULE_SEARCHVECTOR_CRON_MINUTE` (_str_) Minute
* `SCHEDULE_SEARCHVECTOR_CRON_HOUR` (_str_) Hour
* `SCHEDULE_SEARCHVECTOR_CRON_DAY_OF_WEEK` (_str_) Day of week
* `SCHEDULE_SEARCHVECTOR_CRON_DAY_OF_MONTH` (_str_) Day of month
* `SCHEDULE_SEARCHVECTOR_CRON_MONTH_OF_YEAR` (_str_) Month of year

### Using Docker

You must first install [Docker](https://docs.docker.com/engine/installation/) and [Docker Compose](https://docs.docker.com/compose/install/)
 environments.

#### Build and start services

```console
$ make run
```

If you want to run with sample data:
```console
$ make run-and-populate-sample-data
```

##### How o add more data

Seeding it with sample data:

```console
$ docker-compose run --rm django python manage.py reimbursements /mnt/data/reimbursements_sample.csv
$ docker-compose run --rm django python manage.py companies /mnt/data/companies_sample.xz
$ docker-compose run --rm django python manage.py suspicions /mnt/data/suspicions_sample.xz
$ docker-compose run --rm django python manage.py tweets
```

If you're interesting in having a database full of data you can get the datasets running [Rosie](https://github.com/okfn-brasil/serenata-de-amor/tree/main/rosie).
To add a fresh new `reimbursements.xz` or `suspicions.xz` brewed by [Rosie](https://github.com/okfn-brasil/serenata-de-amor/tree/main/rosie), or a `companies.xz` you've got from the [toolbox](https://github.com/okfn-brasil/serenata-toolbox), you just need copy these files to `contrib/data` and refer to them inside the container from the path `/mnt/data/`.

#### Creating search vector

For text search in the dashboard:

```console
$ docker-compose run --rm django python manage.py searchvector
```

#### Acessing Jabas

You can access it at [`localhost:8000`](http://localhost:8000/) in development mode or [`localhost`](http://localhost:80/) in production mode.

To change any of the default environment variables defined in the `docker-compose.yml` just export it in a local environment variable, so when you run Jarbas it will get them.

#### Docker Ready?

Not sure? Test it!

```console
$ docker-compose run --rm django python manage.py check
$ docker-compose run --rm django python manage.py test
```

### Local install

#### Requirements

Jarbas requires [Python 3.5](http://python.org), [Node.js 8](https://nodejs.org/en/), [RabbitMQ 3.6](https://www.rabbitmq.com), and [PostgreSQL 9.6](https://www.postgresql.org). Once you have `pip` and `npm` available install the dependencies:

```console
$ npm install
$ ./node_modules/.bin/elm-package install --yes  # this might not be necessary https://github.com/npm/npm/issues/17316
$ python -m pip install -r requirements-dev.txt
```

##### Python's `lzma` module

In some Linux distros `lzma` is not installed by default. You can check whether you have it or not with `$ python -m lzma`. In Debian based systems you can fix that with `$ apt-get install liblzma-dev` or in macOS with `$ brew install xz` — but you might have to re-compile your Python.

#### Setup your environment variables

Basically this means copying `contrib/.env.sample` as `.env` in the project's root folder — but there is [an entire section on that](#settings).

#### Migrations

Once you're done with requirements, dependencies and settings, create the basic database structure:

```console
$ python manage.py migrate
```

#### Load data

To load data you need RabbitMQ running and a Celery worker:

```
$ celery worker --app jarbas
```

Now you can load the data from our datasets and get some other data as static files:

```
$ python manage.py reimbursements <path to reimbursements.xz>
$ python manage.py suspicions <path to suspicions.xz file>
$ python manage.py companies <path to companies.xz>
$ python manage.py tweets
```

There are sample files to seed yout database inside `contrib/data/`. You can get full datasets running [Rosie](https://github.com/okfn-brasil/serenata-de-amor/tree/main/rosie) or directly with the [toolbox](https://github.com/okfn-brasil/serenata-toolbox).

#### Creating search vector

For text search in the dashboard:

```console
$ python manage.py searchvector
```

#### Generate static files

We generate assets through NodeJS, so run it before Django collecting static files:

```console
$ npm run assets
$ python manage.py collectstatic

```

#### Ready?

Not sure? Test it!

```
$ python manage.py check
$ python manage.py test
```

#### Ready!

Run the server with `$ python manage.py runserver` and load [localhost:8000](http://localhost:8000) in your favorite browser.

#### Using Django Admin


If you would like to access the Django Admin for an alternative view of the reimbursements, you can access it at [`localhost:8000/admin/`](http://localhost:8000/admin/) creating an user with:

```console
$ python manage.py createsuperuser
```

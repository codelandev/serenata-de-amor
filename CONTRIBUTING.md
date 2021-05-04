# Contributing Guide

## Before you start

Please, make sure you have read the [_Tech crash course_](README.md#tech-crash-course-into-operação-serenata-de-amor) – you already know what Rosie, Jarbas, Whistleblower and the toolbox are about, right?

Also we have a 700+ members tech community to support you on [our Telegram open tech group](https://telegram.me/joinchat/AKDWc0BDOqriD1n-mntRBg). Don't hesitate to reach us there.

## Installing

As our stack is not a simple one we opted for standardizing our instructions do [Docker Compose](https://docs.docker.com/compose/install/), which will help you spin up every service in a few commands.

Everything is expected to work with:

```console
$ make run-and-populate-sample-data
```

**Note:** `docker-compose up` is just a health check to assure all dependencies are succesfully installed and the project is running well. To run properly Jarbas and Rosie there are a few more steps (migrations, for example), which are the ones below.

Then `.env` file you just copied contains [environment variables for Jarbas](jarbas/README.md#settings). Feel free to customize it.

### Running Rosie

Example to run only Rosie:

```console
$ docker-compose run --rm rosie python rosie.py run chamber_of_deputies
```

[Check Rosie's `README.md` for more details](rosie/README.md).

### Running Jarbas

This is an example to run only Jarbas. First run migrations and provision:

```console
$ docker-compose run --rm django python manage.py migrate
$ docker-compose run --rm django python manage.py reimbursements /mnt/data/reimbursements_sample.csv
$ docker-compose run --rm django python manage.py companies /mnt/data/companies_sample.xz
$ docker-compose run --rm django python manage.py suspicions /mnt/data/suspicions_sample.xz
$ docker-compose run --rm django python manage.py searchvector
$ docker-compose run --rm django python manage.py tweets
```

The spin up the web server:

```console
$ docker-compose up django
```

Then browse from [`0.0.0.0:8000`](http://0.0.0.0:8000). [Check Jarbas's `README.md` for more details](jarbas/README.md).

## The basics of contributing

A lot of discussions about ideas take place in the [Issues](https://github.com/okfn-brasil/serenata-de-amor/issues) section. There and interacting in the Telegram group you can catch up with what's going on and also suggest new ideas.

Unfortunatelly we have no public roadmap, barely an internal one – but you can follow what the core team is working on [on Trello](https://trello.com/b/5sE3ToT2/serenata).

### The Git basics

**1. _Fork_ this repository**

There's a big button for that in GitHub interface, usually on the top right corner.

**2. Clone your fork of the repository**

```console
$ git clone http://github.com/<YOUR-GITHUB-USERNAME>/serenata-de-amor.git
```

**3. Create a feature branch**

```console
$ git checkout -b <YOUR-GITHUB-USERNAME>-new-stuff
```

Please, note that we prefix branch names with GitHub usernames, this helps us in keeping track of changes and who is working on them.


**4. Do what you do best**

Now it's your time to shine and write meaningful code to raise the bar of the project!

**5. Commit your changes**

```console
$ git commit -am 'My pretty cool contribution'
```

**6. Push to the branch to your fork**

```consle
$ git push origin <YOUR-GITHUB-USERNAME>-new-stuff
```

**7. Create a new _Pull Request_**

From your fork at GitHub usually there is a button to open pull requests.

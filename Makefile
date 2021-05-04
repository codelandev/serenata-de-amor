SHELL=/bin/bash

setup:
	@# create .env file only if not exists
	@cp -n contrib/.env.sample .env

run: setup
	@# build and start services
	@docker-compose up -d --build

	@# validate and run migrations
	@docker-compose run --rm django python manage.py check
	@docker-compose run --rm django python manage.py migrate

populate-sample-data:
	@docker-compose run --rm django python manage.py reimbursements /mnt/data/reimbursements_sample.csv
	@docker-compose run --rm django python manage.py companies /mnt/data/companies_sample.xz
	@docker-compose run --rm django python manage.py suspicions /mnt/data/suspicions_sample.xz
	@docker-compose run --rm django python manage.py tweets

run-and-populate-sample-data: run populate-sample-data

clean:
	@docker-compose rm -fsv

recreate: clean run

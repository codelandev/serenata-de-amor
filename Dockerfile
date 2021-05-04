# TODO: check this image
FROM codesimple/elm:0.18 as elm-builder

WORKDIR /code

COPY package.json package.json
COPY package-lock.json package-lock.json
COPY elm-package.json elm-package.json
COPY gulpfile.js gulpfile.js

RUN npm install

COPY jarbas /code/jarbas

RUN elm make jarbas/layers/elm/Main.elm --output /code/jarbas/assets/layers/static/app.js --yes

FROM python:3.6.4-alpine3.7

WORKDIR /code

ENV AMAZON_BUCKET=serenata-de-amor-data \
    AMAZON_REGION=sa-east-1 \
    PYTHONUNBUFFERED=1 \
    SECRET_KEY=${SECRET_KEY:-my-secret}

RUN set -ex && \
    apk update && apk add --no-cache curl tzdata libpq && \
    cp /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && \
    echo "America/Sao_Paulo" > /etc/timezone && \
    apk update && apk add --no-cache \
      --virtual=.build-dependencies \
      gcc \
      musl-dev \
      postgresql-dev \
      git \
      python3-dev && \
    python -m pip --no-cache install -U pip

COPY ./requirements.txt /code/requirements.txt
COPY ./requirements-dev.txt /code/requirements-dev.txt
COPY manage.py /code/manage.py
COPY jarbas /code/jarbas
COPY rosie /code/rosie

COPY --from=elm-builder /code/jarbas/assets/layers/static/app.js /code/jarbas/layers/static/app.js

RUN set -ex && \
    python -m pip --no-cache install -r requirements-dev.txt && \
    python manage.py collectstatic --no-input && \
    apk del --purge .build-dependencies

HEALTHCHECK --interval=1m --timeout=2m CMD curl 0.0.0.0:8000/healthcheck/
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

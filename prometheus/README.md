# [Prometheus](https://prometheus.io/) — a tool for monitoring, load analysis and analytics

Prometheus is an [open-source](https://github.com/prometheus/prometheus) monitoring tool and really well accepted by the community.

It uses agents that exposes metrics at a certain port, and then prometheus scrapes those metrics via HTTP requests and store them at his [Time Series Database](https://github.com/prometheus/tsdb).

Prometheus has [several agents](https://prometheus.io/docs/instrumenting/exporters/)(they call them 'exporters') build by themselves or by the community and it also have [libraries](https://prometheus.io/docs/instrumenting/clientlibs/) so we can build our own custom exporters, so it can monitor almost everything.

## Table of Contents

1. [Configuration](#Configuration)
    1. [Prometheus configuration](#Prometheus-configuration)
    1. [Docker Compose](#Docker-Compose)
1. [Monitoring and load analysis](#Monitoring-and-load-analysis)
    1. [Process exporter](#Process-exporter)
    1. [Node exporter](#Node-exporter)
    1. [Postgres exporter](#Postgres-exporter)
    1. [Selfmonitoring](#Selfmonitoring)
1. [Analytics](#Analytics)
    1. [BI exporter](#BI-exporter)
1. [Testing](#Testing)
1. [Grafana](#Grafana)
1. [Contributing](#Contributing)
    1. [New exporters](#New-exporters)
    1. [New reimbursement data](#New-reimbursement-data)

## Configuration

### Prometheus configuration

As we said before, prometheus can scrape metrics from several targets, but we need to tell him where to scrape and how often. We do that at the [prometheus.yml](prometheus.yml) file.

First we set a default scraping interval to 15 seconds and a timeout limit for the scraping to 10 seconds:
```yaml
global:
  scrape_interval: 15s
  scrape_timeout: 10s
```

Then we create a new job called `monitoring`, this job will be responsible for scraping monitoring and load analysis metrics. On this job we will tell prometheus where he should be scraping(More information at the [Docker compose](#Docker-compose) section):

```yaml
- job_name: monitoring
  static_configs:
  - targets:
    - localhost:9090
    - grafana:3000
    - node_exporter:9100
    - process_exporter:9256
    - postgres_exporter:9187
```

Our last job will be the `businessInteligence` job. On this one we will not only provide an scraping address, but actually override the scraping interval and timeout(I will explain why at the [BI exporter](#BI-exporter) section):

```yaml
- job_name: businessInteligence
  scrape_interval: 2h  
  scrape_timeout: 30m
  static_configs:
  - targets:
    - bi_exporter:9187
```

### Docker Compose

Here I will talk about some important configuration we made at our `docker-compose.yml` file so that everything works like it should. 

The main thing here is the docker network. We added some new services that need to communicate with others services, and it's only possible if we create a network between them.

As seen at the [prometheus configuration](#Prometheus-configuration) section, prometheus scrapes metrics from some addresses that we choose. Those address are made [here](../docker-compose.yml#L41):

```yaml
 links:
      - node_exporter:node_exporter
      - process_exporter:process_exporter
      - postgres_exporter:postgres_exporter
      - bi_exporter:bi_exporter
      - grafana:grafana
```

If we add an exporter that needs to communicate with another service, the same configuration needs to be made. We can use our postgres exporter as an example:

```yaml
postgres_exporter:
    image: wrouesnel/postgres_exporter
    environment:
      DATA_SOURCE_NAME: postgres://jarbas:mysecretpassword@postgres/jarbas?sslmode=disable
    links:
      - postgres:postgres
```


## Monitoring and load analysis

### Process exporter

This exporter is responsible to expose metrics about every process running at the host machine and it will be our best friend when we want to analyse rosie's performance. For more information about this exporter, please go to this [Github Project](https://github.com/ncabatoff/process-exporter)

### Node exporter

This exporter is responsible to expose general metrics about your Linux host machine, like RAM, CPU, Disk, etc. For more information about this exporter, please go to this [Github Project](https://github.com/prometheus/node_exporter)

### Postgres exporter

This exporter is responsible to expose query results made on a postgres database. It already have some default queries with monitoring purposes(like slow queries and tablespace size), but more can be added with a YAML file.

We've added some custom monitoring queries at the [postgres-exporter/monitoring.yml](postgres-exporter/monitoring.yml) file. For more information about this exporter, please go to this [Github Project](https://github.com/wrouesnel/postgres_exporter)

### Selfmonitoring

Grafana and Prometheus already expose monitoring metrics by default, no need to an extra exporter for them. So we added them as targets as well, as shown at the [prometheus configuration](#Prometheus-configuration) section.



## Analytics

Prometheus provides it's own query language, called [PromQL](https://prometheus.io/docs/prometheus/latest/querying/basics/), and several cool and easy-to-use functions come with it, like [average, standard variation, standard deviation, max, min, count](https://prometheus.io/docs/prometheus/latest/querying/functions/#aggregation_over_time), and the list goes on and on.

With those functions it's possible to make analytical studies on top of our reimbursement data, we just need to send this data to prometheus.

We can do that with the [postgres-exporter](https://github.com/wrouesnel/postgres_exporter), that we've called `bi_exporter` at our [docker-compose.yml](../docker-compose.yml)

### BI exporter

We know that we can add custom queries to our postgres exporter, so why don't we expose reimbursement data with it?

One important thing is, as seen at the postgres exporter's documentation, we can disable monitoring metrics with the flags `--disable-default-metrics` and `--disable-settings-metrics` so this particular exporter will be responsible only for reimbursement data. Then we can create custom queries and add them to our [postgres-exporter/businessInteligence.yml](postgres-exporter/businessInteligence.yml) file.

> **Warning**: Be careful with your queries

For testing purposes we use a database with only sample data, so our custom queries will usually be fast and can be executed more often. When going to production stage, our database is a lot bigger and our queries might get slower, so it would be better to execute them less often. 

To change this configuration, you can comment and uncomment those lines at [prometheus.yml](prometheus.yml):

```yaml
 scrape_interval: 2h  # Use 2h interval in production
#  scrape_interval: 5m  # For testing purposes, smaller intervals are more appropriate
```

That's something really important to keep an eye on, because the queries we make here will be executed at our postgres periodically and that is the same database that jarbas use. Heavy queries will have a bad impact and may cause unavailability to our main applications(Jarbas and Rosie)

Another point is, there is not too many reimbursements added to our database every single hour... so there is no point on executing our queries too often, but if we configure it's interval to more than 2h, there will be times when prometheus won't return any data. That is because of how prometheus manages volatile and non-volatile memory. (If you are interested, more information about it can be found [here](https://fabxc.org/tsdb/))





## Testing

Too much talking, too little doing. Let's run this thing!

You can start Prometheus and all the exporters with the same command you start jarbas:

```shell
docker-compose up -d
```

Your prometheus will be available at http://localhost:9090 :champagne: 

After everything is up, we must populate our database with sample data that our exporter will expose to our prometheus.

```shell
docker-compose run --rm django python manage.py migrate
docker-compose run --rm django python manage.py reimbursements /mnt/data/reimbursements_sample.csv
docker-compose run --rm django python manage.py companies /mnt/data/companies_sample.xz
```

Now everything is setup and we just gotta wait to prometheus to scrape our exporter.

You can see your configuration and targets at http://localhost:9090/config and http://localhost:9090/targets respectively.

When looking at your targets, you will see `UP` Status if our prometheus have already scraped metrics at the configured addresses, `DOWN` if it couldn't scrape anything at the configured address and `UNKNOWN` if it still haven't tried to scrape yet. If you've configured your bi exporter scrape interval with a long time, it will take a while for it's status to change.

Prometheus have it's own [documentation](https://prometheus.io/docs/introduction/overview/) if you are interested to learn more about it.





## Grafana

Why have all those monitoring metrics and reimbursement data stored at our prometheus if we don't do anything with it? That's why we have Grafana!

Grafana is an open-source, dashboard and graph editor that can use several different datasources, like Postgres and Prometheus.

At grafana we will show all our monitoring metrics with in a "human readable" way and it will be possible to build dashboards about our reimbursement data as well.

To better understand how use configure and use our grafana, please read it's own [documentation](../grafana/README.md)


## Contributing

### New exporters
Currently we are only monitoring our Prometheus, Grafana, Postgres, our Linux host and it's processes, but as we talked before, Prometheus has [several other agents](https://prometheus.io/docs/instrumenting/exporters/) and you can help us configuring new exporters to monitor other parts of Serenata de Amor.

To do so, just add the new exporter and it's configuration to our [docker-compose.yml](../docker-compose.yml) and it's address to [prometheus.yml](prometheus.yml) configuration file.

If everything works as expected, you will be able to query the new metrics at http://localhost:9090/graph

### New reimbursement data

If there is some reimbursement information that is missing on prometheus and you'd like to use, you can always modify or add new queries to our [postgres-exporter/businessInteligence.yml](postgres-exporter/businessInteligence.yml) file, just keep an eye on it's cost!

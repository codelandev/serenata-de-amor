# [Grafana](https://grafana.com/) - a tool for time series analytics and monitoring

Grafana is an [open-source](https://github.com/grafana/grafana) dashboard editor that support several datasources, like Postgres and Prometheus.

We use grafana to visualize our data in an easy way and to make analytical studies on top of it.


## Table of contents
1. [Grafana provisioning](#Grafana-provisioning)
    1. [Datasources](#Datasources)
    1. [Dashboards](#Dashboards)
1. [Load analysis](#Load-analysis)
1. [Testing](#Testing)
1. [Contributing](#Contributing)



## Grafana provisioning

We can create new datasources and dashboard all we want, but unfortunatly everything we create won't be persistent if we destroy and execute a new grafana container.

We want to create new dashboards and datasources that can be easily replicated when new contributors try to help us. For this we will use [Grafana provisioning](https://grafana.com/docs/administration/provisioning/).

We can add YAML and JSON files to our provisioning folder(/etc/grafana/provisioning by default) and the dashboards and datasources we create will be passed on to every contributor that uses our project.

At our [docker-compose.yml](../docker-compose.yml) we've added an external volume to our grafana service:

```yaml
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
```

With this configuration, everything we put at our [provisioning folder](provisioning) will be replicated to our Grafana container's provisioning folder.

### Datasources

At our [datasources folder](provisioning/datasources) we add YAML files that will provide our Prometheus and Postgres datasources.

Further documentation about datasource provisioning can be found [here](https://grafana.com/docs/administration/provisioning/#datasources).


### Dashboards

Dashboard provisioning is a little bit trickier. Grafana itself has folders in it:
![image](https://user-images.githubusercontent.com/24193764/59293696-1f32a680-8c56-11e9-8b74-eabec410d6b1.png)

This folders are provisioned with YAML files, and the dashboards located in each folder with JSON files.

At our [dashboards folder](provisioning/dashboards) we add YAML files that will provide our folders. At those YAMLs, we will tell Grafana where it will find the JSON files that will provide our dashboards. For example:

```yaml
apiVersion: 1
providers:
- name: 'monitoring'
  orgId: 1
  folder: 'Monitoring'
  type: file
  disableDeletion: true
  updateIntervalSeconds: 300
  options:
    path: /etc/grafana/provisioning/dashboards/monitoring
```

Here we tell where our JSONs are:

```yaml
    path: /etc/grafana/provisioning/dashboards/monitoring
```



## Load Analysis

Grafana, alongside with Prometheus, is great for load analysis!

With prometheus monitoring processes(More information about it at our Prometheus [documentation](../prometheus/README.md)) we can see how much RAM, SWAP, CPU, etc, is used by each application that makes part of Serenata de Amor, and that includes our main apps, Rosie and Jarbas.

After everything is up, you can acess the Process monitoring dashboard at  http://localhost:3000/d/lOXQMRMZ1/process-monitoring?orgId=1

Then run rosie:

```shell
docker run --rm -v /tmp/serenata-data:/tmp/serenata-data serenata/rosie python rosie.py run chamber_of_deputies
```

We can then see how much resources it uses over time, like RAM for example:

![image](https://user-images.githubusercontent.com/24193764/58755015-97a8a300-84b1-11e9-82d0-24511ac70743.png)

If you make changes to Jarbas' or Rosie's code, you can use this dashboard to analyse if the performance got better or worse!



## Testing

It's quite simple to get your Grafana going, just like the other tools, just run the docker compose:

```shell
docker compose up -d
```

Your grafana will be available at http://localhost:3000
And your dashboards at http://localhost:3000/dashboards
You can login into grafana with the credentials *admin/admin*

> PS: Sometimes dashboards take some time to load. If they are not there, wait 5 to 10 minutes for them to load.


## Contributing

It's quite simple to contribute to our grafana! You just need to add your new dashboard's JSON to the correct [provisioning folder](provisioning/dashboards).


If you want to use Prometheus to monitor a service of Serenata that is not monitored yet, you can create a new dashboard with the collected metrics and add it's JSON to the [monitoring folder](provisioning/dashboards/monitoring).

For dashboards that focus on reimbursement analytics, add their JSON at the [business inteligence folder](provisioning/dashboards/businessInteligence).

If you are wondering if you need to code the whole JSON... no, you don't need to do that!

You can build your dashboard with the Grafana UI and just export the JSON, by clicking at the `Share Dashboard` button located at the superior right corner:

![image](https://user-images.githubusercontent.com/24193764/58824721-208b2000-8613-11e9-92ed-a2673a05ec58.png)

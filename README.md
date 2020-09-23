# ADCPLOT

## NetCDF Plotting API

NetCDF data access is based on <a href="http://xarray.pydata.org/en/stable/" target="_blank">xarray</a>.
Plotting routines are based on <a href="https://docs.bokeh.org/en/latest/index.html" target="_blank">bokeh</a>.


To run the service a working docker environment is needed and make sure the docker-compose tool is available.

On debian based linux distribution simply run:

```bash
apt-get install docker-io docker-compose
```

To start the service, clone this repository and execute the docker-compose instruction:

```
git clone https://github.com/NorDataNet/adcplot
cd adcplot
docker-compose up
```
Note: you may nedd root privileges depending on how your docker settings.

Once the service is running, assuming a NetCDF resource is available at `resource_url`:

* Get list of variables from a NetCDF resource
    http://localhost:7000/adcplot/plot?get=param&resource_url=resource_url
* Get the bokeh plot of a selected variable embedded in a html div `tsplot`
    http://localhost:7000/adcplot/plot?get=plot&resource_url=resource_url&variable=variable_name&axis=axis_name


Example using the built-in example data served via hyrax opendap server:

```bash
curl http://localhost:7000/adcplot/plot?get=param&resource_url=http://hyrax:8080/opendap/SN99938.nc
```

which will return the following json:

```json
{"y_axis":["air_pressure_at_sea_level",
           "surface_air_pressure_2m", 
           "air_temperature_2m", 
           "air_pressure_at_sea_level_qnh", 
           "wind_speed_10m", 
           "wind_from_direction_10m", 
           "relative_humidity"]}
```

To get a json object that can be embeded in a html div named tsplot
http://localhost:7000/adcplot/plot?get=plot&resource_url=http://hyrax:8080/opendap/SN99938.nc&variable=air_pressure_at_sea_level&axis=y_axis

To test the plotting widget is possible to code the API call into an HTML file using `fetch`, see [example](app/static/index.html).
